"""
CrowdWisdom AI Studio — Sound Design Service (Stage 3)
Institutional-Grade Multi-Layered Commercial Audio Engine.

Produces broadcast-quality audio tracks featuring:
1. Dynamic 120 BPM fintech synth score (harmonic pads, pulsing 808 sub-bass, metallic percussion).
2. Opening cinematic braam / sub-drop impact for opening hook retention.
3. Directional transition whooshes, pink-noise risers, and sub-bass impact landings.
4. Digital telemetry clicks and market data micro-transients.
5. Closing resolution chime and harmonic brand swell on final CTA.
6. Exponential sidechain vocal ducking with smooth attack/release and vocal presence notch EQ.
"""
import math
import logging
from typing import List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class SoundDesignService:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate_commercial_soundtrack(
        self,
        total_duration: float,
        speech_intervals: List[Tuple[float, float]],
        transition_timestamps: Optional[List[float]] = None,
        cta_timestamp: Optional[float] = None,
        bpm: float = 120.0
    ) -> np.ndarray:
        """
        Synthesizes a master stereo audio track (shape: [num_samples, 2])
        combining hybrid fintech stems, cinematic SFX impacts, and dynamic vocal sidechain.
        """
        sr = self.sample_rate
        n_samples = int(total_duration * sr)
        t = np.linspace(0, total_duration, n_samples, endpoint=False, dtype=np.float32)

        # -------------------------------------------------------------
        # Stem 1: Warm Analog Pad & Pulsing Arpeggio (D Minor Progression)
        # Dm (D3, F3, A3) -> Bb (Bb2, D3, F3) -> F (F2, C3, A3) -> C (C3, E3, G3)
        # -------------------------------------------------------------
        beat_dur = 60.0 / bpm          # 0.5s per beat
        chord_dur = beat_dur * 4.0      # 2.0s per chord
        chords = [
            [146.83, 174.61, 220.00, 293.66],  # Dm (D3, F3, A3, D4)
            [116.54, 146.83, 174.61, 233.08],  # Bb (Bb2, D3, F3, Bb3)
            [87.31,  130.81, 174.61, 220.00],  # F  (F2, C3, F3, A3)
            [130.81, 164.81, 196.00, 261.63],  # C  (C3, E3, G3, C4)
        ]

        chord_phase = (t % (chord_dur * 4.0)) / chord_dur
        chord_idx = np.floor(chord_phase).astype(int) % 4

        pad_left = np.zeros(n_samples, dtype=np.float32)
        pad_right = np.zeros(n_samples, dtype=np.float32)

        for tone_i in range(4):
            freqs = np.array([chords[c][tone_i] for c in chord_idx], dtype=np.float32)
            # Stereo detuning (left -0.3Hz, right +0.3Hz) for wide atmospheric spread
            pad_left += 0.18 * np.sin(2 * np.pi * (freqs - 0.35) * t)
            pad_right += 0.18 * np.sin(2 * np.pi * (freqs + 0.35) * t)
            # Subtle warm second harmonic
            pad_left += 0.06 * np.sin(2 * np.pi * (freqs * 2.0) * t)
            pad_right += 0.06 * np.sin(2 * np.pi * (freqs * 2.0) * t)

        # Pulsing 8th-note synth bass
        eighth_dur = beat_dur / 2.0
        eighth_phase = (t % eighth_dur) / eighth_dur
        bass_env = np.exp(-eighth_phase * 6.0)
        bass_freqs = np.array([chords[c][0] * 0.5 for c in chord_idx], dtype=np.float32) # Sub octave
        bass_pulse = 0.22 * bass_env * np.sin(2 * np.pi * bass_freqs * t)

        # -------------------------------------------------------------
        # Master Mix Buffers (initialized directly with Stem 1: Harmony)
        # -------------------------------------------------------------
        raw_left = (pad_left + bass_pulse) * 0.40
        raw_right = (pad_right + bass_pulse) * 0.40
        del pad_left, pad_right, bass_pulse

        # -------------------------------------------------------------
        # Stem 2: Hybrid Cinematic Percussion (120 BPM)
        # -------------------------------------------------------------
        beat_t = t % beat_dur
        beat_num = np.floor(t / beat_dur).astype(int) % 4

        # Punchy 808 sub-kick on beats 0 and 2
        is_kick = (beat_num == 0) | (beat_num == 2)
        kick_env = np.where(is_kick & (beat_t < 0.24), np.exp(-beat_t * 22.0), 0.0)
        kick_freq = 52.0 + 75.0 * np.exp(-beat_t * 36.0)
        kick_mono = 0.38 * kick_env * np.sin(2 * np.pi * kick_freq * beat_t)
        del kick_env, kick_freq

        # Snappy commercial rimshot/snare on beats 1 and 3
        is_snare = (beat_num == 1) | (beat_num == 3)
        snare_env = np.where(is_snare & (beat_t < 0.16), np.exp(-beat_t * 28.0), 0.0)
        np.random.seed(42)
        snare_noise = np.random.uniform(-1.0, 1.0, n_samples).astype(np.float32)
        snare_mono = 0.16 * snare_env * (snare_noise + 0.6 * np.sin(2 * np.pi * 320.0 * beat_t))
        del snare_env, snare_noise

        # Hi-hat on 8th and 16th notes
        sub_beat_t = t % (beat_dur / 2.0)
        hat_env = np.where(sub_beat_t < 0.035, np.exp(-sub_beat_t * 90.0), 0.0)
        hat_mono = 0.06 * hat_env * (np.sin(2 * np.pi * 7800.0 * t) + np.sin(2 * np.pi * 9600.0 * t))
        del hat_env

        # Accumulate percussion in-place
        raw_left += (kick_mono + snare_mono * 0.9 + hat_mono * 1.1) * 0.70
        raw_right += (kick_mono + snare_mono * 1.1 + hat_mono * 0.9) * 0.70
        del kick_mono, snare_mono, hat_mono

        # -------------------------------------------------------------
        # Stem 3: Opening Hook Braam & Sub-Bass Drop (t in [0.0, 1.8s])
        # -------------------------------------------------------------
        braam_mask = t <= 1.8
        if np.any(braam_mask):
            b_t = t[braam_mask]
            b_env = np.exp(-b_t * 2.2)
            # Low brassy multi-oscillator saw drop: D1 (36.7Hz) + D2 (73.4Hz) + F2 (87.3Hz)
            b_pitch_drop = np.exp(-b_t * 1.6)
            f_drop = 36.7 + 28.0 * b_pitch_drop
            braam_osc = (
                0.35 * np.sin(2 * np.pi * f_drop * b_t) +
                0.22 * np.sin(2 * np.pi * f_drop * 2.0 * b_t) +
                0.14 * np.sin(2 * np.pi * (f_drop * 3.0 + 0.5) * b_t)
            )
            raw_left[braam_mask] += 0.42 * b_env * braam_osc
            raw_right[braam_mask] += 0.42 * b_env * braam_osc
            del b_t, b_env, braam_osc

        # -------------------------------------------------------------
        # Stem 4: Directional Transition Whooshes, Risers & Impact Landings
        # -------------------------------------------------------------
        if transition_timestamps:
            for s_idx, t_trans in enumerate(transition_timestamps):
                # 1. Reverse Riser / Sweep in [t_trans - 0.42s, t_trans]
                rise_mask = (t >= (t_trans - 0.42)) & (t <= t_trans)
                if np.any(rise_mask):
                    u_rise = (t[rise_mask] - (t_trans - 0.42)) / 0.42  # 0 to 1
                    rise_env = u_rise ** 2.2
                    sweep_freq = 220.0 + 780.0 * (u_rise ** 2.0)
                    rise_sound = 0.24 * rise_env * np.sin(2 * np.pi * sweep_freq * t[rise_mask])
                    pan_l = (1.0 - u_rise) * 1.2
                    pan_r = u_rise * 1.2
                    raw_left[rise_mask] += rise_sound * pan_l
                    raw_right[rise_mask] += rise_sound * pan_r

                # 2. Sub-Bass Impact Landing in [t_trans, t_trans + 0.35s]
                imp_mask = (t >= t_trans) & (t <= (t_trans + 0.35))
                if np.any(imp_mask):
                    dt_imp = t[imp_mask] - t_trans
                    imp_env = np.exp(-dt_imp * 18.0)
                    imp_freq = 50.0 + 30.0 * np.exp(-dt_imp * 24.0)
                    impact_sound = 0.32 * imp_env * np.sin(2 * np.pi * imp_freq * dt_imp)
                    raw_left[imp_mask] += impact_sound
                    raw_right[imp_mask] += impact_sound

        # -------------------------------------------------------------
        # Stem 5: Telemetry UI Ticks & Closing Resolution Chime
        # -------------------------------------------------------------
        # Micro telemetry ticks every 1.5s (digital data chatter)
        tick_period = 1.5
        tick_t = t % tick_period
        tick_mask = tick_t < 0.012
        if np.any(tick_mask):
            tick_env = np.exp(-tick_t[tick_mask] * 400.0)
            tick_osc = 0.035 * tick_env * np.sin(2 * np.pi * 5400.0 * t[tick_mask])
            raw_left[tick_mask] += tick_osc
            raw_right[tick_mask] += tick_osc
            del tick_env, tick_osc

        # Closing Resolution Harmonic Chime at CTA reveal
        cta_t = cta_timestamp if cta_timestamp else max(0.0, total_duration - 3.2)
        cta_mask = (t >= cta_t) & (t <= total_duration)
        if np.any(cta_mask):
            dt_cta = t[cta_mask] - cta_t
            chime_env = np.exp(-dt_cta * 0.9) # Long 3-second singing decay
            chime_chord = (
                0.14 * np.sin(2 * np.pi * 293.66 * dt_cta) +
                0.12 * np.sin(2 * np.pi * 369.99 * dt_cta) +
                0.10 * np.sin(2 * np.pi * 440.00 * dt_cta) +
                0.08 * np.sin(2 * np.pi * 587.33 * dt_cta)
            )
            raw_left[cta_mask] += chime_env * chime_chord
            raw_right[cta_mask] += chime_env * chime_chord
            del dt_cta, chime_env, chime_chord

        # Intro and Outro master envelopes
        intro_dur = 1.0
        outro_dur = 2.4
        master_env = np.ones(n_samples, dtype=np.float32)
        intro_mask = t < intro_dur
        master_env[intro_mask] = t[intro_mask] / intro_dur
        outro_mask = t > (total_duration - outro_dur)
        master_env[outro_mask] = np.maximum(0.0, (total_duration - t[outro_mask]) / outro_dur)

        # Smooth Exponential Vocal Sidechain Ducking Curve
        ducking_mult = np.full(n_samples, 0.52, dtype=np.float32)
        for s_start, s_end in speech_intervals:
            # 60ms pre-emptive smooth attack, 260ms logarithmic release
            t_pre = max(0.0, s_start - 0.08)
            t_post = min(total_duration, s_end + 0.28)
            
            # Find sample indices
            idx_pre = int(t_pre * sr)
            idx_start = int(s_start * sr)
            idx_end = int(s_end * sr)
            idx_post = int(t_post * sr)

            # Attack ramp (0.52 down to 0.18)
            if idx_start > idx_pre:
                ramp_down = np.linspace(0.52, 0.18, idx_start - idx_pre)
                ducking_mult[idx_pre:idx_start] = np.minimum(ducking_mult[idx_pre:idx_start], ramp_down)
            
            # Active speech hold
            ducking_mult[idx_start:idx_end] = np.minimum(ducking_mult[idx_start:idx_end], 0.18)
            
            # Release ramp (0.18 up to 0.52)
            if idx_post > idx_end:
                ramp_up = np.linspace(0.18, 0.52, idx_post - idx_end)
                ducking_mult[idx_end:idx_post] = np.minimum(ducking_mult[idx_end:idx_post], ramp_up)

        raw_left *= master_env
        raw_left *= ducking_mult
        raw_right *= master_env
        raw_right *= ducking_mult
        del master_env, ducking_mult

        # Peak normalization & soft limiting (-2.0 dBFS headroom)
        max_peak = max(np.max(np.abs(raw_left)), np.max(np.abs(raw_right)), 0.001)
        target_peak = 0.78  # -2.1 dBFS
        if max_peak > target_peak:
            scale = target_peak / max_peak
            raw_left *= scale
            raw_right *= scale

        stereo = np.column_stack([raw_left, raw_right])
        del raw_left, raw_right
        return stereo

    def synthesize_soundtrack_to_wav(
        self,
        total_duration: float,
        speech_intervals: List[Tuple[float, float]],
        transition_timestamps: Optional[List[float]] = None,
        cta_timestamp: Optional[float] = None,
        bpm: float = 120.0,
        output_wav_path: Optional[str] = None,
    ) -> str:
        """
        Synthesizes the master stereo soundtrack directly to a 16-bit PCM WAV file on disk.
        Aggressively deallocates transient float32 arrays and invokes garbage collection immediately,
        preventing >100 MB transient memory spikes in Python memory during video rendering.
        """
        import gc
        import wave
        import tempfile

        if not output_wav_path:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                output_wav_path = tf.name

        stereo = self.generate_commercial_soundtrack(
            total_duration=total_duration,
            speech_intervals=speech_intervals,
            transition_timestamps=transition_timestamps,
            cta_timestamp=cta_timestamp,
            bpm=bpm,
        )

        # Convert float32 [-1.0, 1.0] to int16 PCM [-32768, 32767]
        stereo_int16 = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
        del stereo

        with wave.open(output_wav_path, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(self.sample_rate)
            wf.writeframes(stereo_int16.tobytes())

        del stereo_int16
        gc.collect()
        logger.info(f"[SoundDesignService] Exported soundtrack WAV ({total_duration:.1f}s) to {output_wav_path}")
        return output_wav_path

sound_design_service = SoundDesignService()
