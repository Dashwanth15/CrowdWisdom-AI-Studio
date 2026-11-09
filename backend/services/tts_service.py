"""
CrowdWisdom AI Studio — Text-To-Speech (TTS) Narration Engine
Synthesizes cinematic spoken voiceovers for video advertisement scenes.
Provides frame-accurate audio-visual synchronization, natural pre-roll/post-roll breathers,
and sidechain telemetry for soundtrack ducking.
Supports neural edge-tts with automatic fallback to Windows SAPI.
"""
import os
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class TTSService:
    """
    Synthesizes and synchronizes audible voiceover narration across storyboard scenes.
    Ensures zero mid-word audio truncation and frame-perfect scene alignment.
    """

    def __init__(self, voice: str = "en-US-ChristopherNeural"):
        self.voice = voice

    async def synthesize_scene_audio(self, text: str, output_path: str) -> bool:
        """
        Synthesizes spoken narration for a single scene.
        Attempts edge-tts first; falls back to Windows SAPI if unavailable.
        """
        clean_text = text.strip()
        if not clean_text:
            return False

        # Attempt 1: Edge TTS Neural Voice (High fidelity commercial narrator with 6s timeout)
        try:
            import edge_tts
            communicate = edge_tts.Communicate(clean_text, self.voice, rate="+2%", volume="+5%")
            await asyncio.wait_for(communicate.save(output_path), timeout=6.0)
            if Path(output_path).exists() and Path(output_path).stat().st_size > 500:
                return True
        except Exception as e:
            logger.info(f"[TTS] Edge-TTS notice: {e}. Trying Windows SAPI fallback...")

        # Attempt 2: Windows SAPI Native Voice Fallback
        try:
            def _sapi_speak():
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                stream = win32com.client.Dispatch("SAPI.SpFileStream")
                # 3 = SSFMCreateForWrite
                stream.Open(output_path, 3, False)
                speaker.AudioOutputStream = stream
                speaker.Speak(clean_text)
                stream.Close()

            await asyncio.to_thread(_sapi_speak)
            if Path(output_path).exists() and Path(output_path).stat().st_size > 500:
                return True
        except Exception as sapi_err:
            logger.warning(f"[TTS] SAPI fallback also failed: {sapi_err}")

        return False

    async def synthesize_all_scenes(
        self, scenes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes audio for all storyboard scenes ahead of rendering.
        Measures exact speech duration so scenes can be dynamically timed to speech.
        """
        from moviepy import AudioFileClip
        results = []

        for idx, sc in enumerate(scenes):
            vo_text = (sc.get("voiceover") or sc.get("on_screen_text") or "").strip()
            item = {
                "scene_index": idx,
                "has_speech": False,
                "audio_path": None,
                "speech_duration": 0.0,
            }

            if vo_text:
                temp_file = Path(tempfile.gettempdir()) / f"cwt_vo_{idx}_{os.getpid()}_{idx}.mp3"
                success = await self.synthesize_scene_audio(vo_text, str(temp_file))
                if success and temp_file.exists():
                    try:
                        clip = AudioFileClip(str(temp_file))
                        item["has_speech"] = True
                        item["audio_path"] = str(temp_file)
                        item["speech_duration"] = float(clip.duration)
                        clip.close()
                    except Exception as clip_err:
                        logger.warning(f"[TTS] Scene {idx} audio inspect notice: {clip_err}")

            results.append(item)

        return results

    async def generate_narration_track(
        self,
        scenes: List[Dict[str, Any]],
        total_duration: float,
        allocated_durations: Optional[List[float]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Generates a continuous, synchronized narration audio track for all scenes.
        Returns a dictionary containing:
        - master_audio_path: path to master MP3 file
        - speech_intervals: list of (start_sec, end_sec) active voice timestamps for music ducking
        - adjusted_durations: list of exact scene durations that fit speech with natural breathers
        """
        from moviepy import AudioFileClip, AudioClip, concatenate_audioclips

        speech_results = await self.synthesize_all_scenes(scenes)
        num_scenes = len(scenes)

        # Calculate optimal scene durations driven by actual speech length
        # Rule: 0.35s pre-roll (let cut register) + speech + 0.85s post-roll (breather before cut)
        raw_scene_durations = []
        for idx in range(num_scenes):
            sp = speech_results[idx]
            min_needed = (sp["speech_duration"] + 1.2) if sp["has_speech"] else 3.5
            if allocated_durations and idx < len(allocated_durations):
                chosen_dur = max(min_needed, allocated_durations[idx])
            else:
                default_sc_dur = float(scenes[idx].get("duration_seconds", 6.0))
                chosen_dur = max(min_needed, default_sc_dur)
            raw_scene_durations.append(round(chosen_dur, 2))

        # Scale durations to align smoothly with target total_duration if desired
        target_total = max(total_duration, sum(raw_scene_durations))
        scale = target_total / max(sum(raw_scene_durations), 1.0)
        adjusted_durations = [round(d * scale, 2) for d in raw_scene_durations]

        scene_audio_clips = []
        speech_intervals: List[Tuple[float, float]] = []
        current_timeline_sec = 0.0
        has_any_speech = False

        def make_silence(duration: float):
            d = max(0.01, duration)
            def _silence_gen(t):
                t_arr = np.atleast_1d(t)
                return np.zeros((len(t_arr), 2)) if hasattr(t, '__len__') else np.zeros(2)
            return AudioClip(_silence_gen, duration=d, fps=44100)

        try:
            for idx in range(num_scenes):
                sc_dur = adjusted_durations[idx]
                sp = speech_results[idx]

                if sp["has_speech"] and sp["audio_path"] and Path(sp["audio_path"]).exists():
                    has_any_speech = True
                    try:
                        speech_clip = AudioFileClip(sp["audio_path"])
                        speech_dur = float(speech_clip.duration)

                        # Natural cinematic pacing:
                        # 0.35s pre-roll breath before speech starts
                        pre_roll_dur = 0.35
                        post_roll_dur = max(0.2, sc_dur - pre_roll_dur - speech_dur)

                        pre_silence = make_silence(pre_roll_dur)
                        post_silence = make_silence(post_roll_dur)

                        # Record interval for intelligent music ducking
                        speech_start = current_timeline_sec + pre_roll_dur
                        speech_end = speech_start + speech_dur
                        speech_intervals.append((speech_start, speech_end))

                        aligned_scene_audio = concatenate_audioclips([pre_silence, speech_clip, post_silence])
                        scene_audio_clips.append(aligned_scene_audio)
                        current_timeline_sec += sc_dur
                        continue
                    except Exception as clip_err:
                        logger.warning(f"[TTS] Alignment notice scene {idx}: {clip_err}")

                # Scene has no speech — full scene silence
                scene_audio_clips.append(make_silence(sc_dur))
                current_timeline_sec += sc_dur

            if not has_any_speech or not scene_audio_clips:
                return None

            master_narration = concatenate_audioclips(scene_audio_clips)

            # Master file output
            master_output_path = Path(tempfile.gettempdir()) / f"cwt_narration_master_{os.getpid()}.mp3"
            master_narration.write_audiofile(str(master_output_path), fps=44100, logger=None)
            master_narration.close()

            # Clean up intermediate scene audio temp files immediately
            for sp in speech_results:
                if sp.get("audio_path"):
                    try:
                        p = Path(sp["audio_path"])
                        if p.exists():
                            p.unlink()
                    except Exception:
                        pass

            # Close individual clips
            for c in scene_audio_clips:
                try:
                    c.close()
                except Exception:
                    pass

            return {
                "master_audio_path": str(master_output_path),
                "speech_intervals": speech_intervals,
                "adjusted_durations": adjusted_durations,
            }

        except Exception as e:
            logger.error(f"[TTS] Narration track synthesis error: {e}")
            return None


tts_service = TTSService()
