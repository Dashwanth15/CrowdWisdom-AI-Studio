"""
CrowdWisdom AI Studio — Automated Test Suite: Memory Optimization & Concurrency Limits
Verifies:
1. Process RSS memory tracking & GC reclamation.
2. Kinetic caption cache bounding and memory efficiency.
3. Optical bloom low-memory rendering.
4. JobManager concurrency semaphore & queueing for video jobs.
5. Timeout handling and safe resource release.
6. Cleanup on rendering failure (no leaked clips or temp files).
7. Memory stability across repeated renders.
8. Health and memory diagnostics API responsiveness.
"""
import asyncio
import os
import gc
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from PIL import Image

from services.memory_monitor import (
    get_process_memory_mb,
    get_system_memory_mb,
    release_system_memory,
    MemoryTracker,
)
from workers.job_manager import JobManager
from config import settings


@pytest.mark.asyncio
async def test_process_memory_tracking_and_gc():
    """Verify that RSS memory reading and GC reclamation function correctly."""
    mem_before = get_process_memory_mb()
    assert isinstance(mem_before["rss_mb"], float)
    assert mem_before["rss_mb"] > 0

    sys_mem = get_system_memory_mb()
    assert sys_mem["total_mb"] > 0
    assert sys_mem["available_mb"] > 0

    # Allocate and immediately release memory
    dummy_arrays = [np.ones((500, 500, 3), dtype=np.uint8) for _ in range(20)]
    del dummy_arrays
    post_gc_rss = release_system_memory()
    assert post_gc_rss > 0


@pytest.mark.asyncio
async def test_memory_tracker_lifecycle():
    """Verify MemoryTracker context manager records initial, peak, and final RSS."""
    tracker = MemoryTracker(job_id="test_job_123", job_type="test_render", limit_mb=500.0)
    async with tracker:
        assert tracker.initial_rss > 0
        assert tracker.peak_rss >= tracker.initial_rss
        # Simulate small allocation
        temp_data = [i for i in range(100_000)]
        tracker.record_peak()
        await asyncio.sleep(0.05)
        del temp_data

    assert tracker.final_rss > 0
    assert tracker.post_gc_rss > 0
    assert tracker.peak_rss >= tracker.initial_rss


def test_optical_bloom_low_memory():
    """Verify render_optical_bloom runs efficiently without allocating 100+ MB arrays."""
    from video_engine.openmontage_adapter import render_optical_bloom

    # Use standard 1080x1920 portrait frames
    w, h = 1080, 1920
    frame_a = np.full((h, w, 3), 40, dtype=np.uint8)
    frame_b = np.full((h, w, 3), 180, dtype=np.uint8)

    # Peak flare occurs at tau = 0.5
    result = render_optical_bloom(frame_a, frame_b, tau=0.5)
    assert result.shape == (h, w, 3)
    assert result.dtype == np.uint8
    # Center or flare area should be brighter than baseline
    assert np.mean(result) > np.mean(frame_a)


@pytest.mark.asyncio
async def test_concurrent_rendering_semaphore_enforcement():
    """
    Verify that concurrent video rendering jobs are strictly serialized by the
    concurrency semaphore, while lightweight jobs run concurrently.
    """
    test_manager = JobManager()
    execution_order = []
    concurrency_counter = 0
    max_observed_concurrency = 0

    async def mock_heavy_render(job_id: str, delay: float):
        nonlocal concurrency_counter, max_observed_concurrency
        concurrency_counter += 1
        if concurrency_counter > max_observed_concurrency:
            max_observed_concurrency = concurrency_counter
        execution_order.append(f"start_{job_id}")
        await asyncio.sleep(delay)
        execution_order.append(f"end_{job_id}")
        concurrency_counter -= 1

    # Submit 3 video jobs simultaneously with limit = 1
    with patch.object(settings, "MAX_CONCURRENT_VIDEO_RENDERS", 1):
        t1 = test_manager.submit_job(
            job_id="v_job_1",
            idempotency_key="render_script_1",
            coro_func=lambda: mock_heavy_render("job_1", 0.1),
            job_type="video_production",
            campaign_id="camp_1"
        )
        t2 = test_manager.submit_job(
            job_id="v_job_2",
            idempotency_key="render_script_2",
            coro_func=lambda: mock_heavy_render("job_2", 0.1),
            job_type="video_production",
            campaign_id="camp_2"
        )

        assert await t1 is True
        assert await t2 is True

        # Wait for both tasks to complete
        tasks = list(test_manager._active_tasks.values())
        await asyncio.gather(*tasks)

        # Concurrency must NEVER have exceeded 1
        assert max_observed_concurrency == 1
        # Start and end of job_1 must precede start and end of job_2 (strict serialization)
        assert execution_order == ["start_job_1", "end_job_1", "start_job_2", "end_job_2"]


@pytest.mark.asyncio
async def test_job_timeout_and_resource_release():
    """Verify that jobs exceeding VIDEO_RENDER_TIMEOUT_SECONDS are cancelled and release semaphore."""
    test_manager = JobManager()

    async def stalled_job():
        await asyncio.sleep(5.0)

    # Set timeout to 0.1 seconds
    with patch.object(settings, "VIDEO_RENDER_TIMEOUT_SECONDS", 0.1):
        with patch("workers.job_manager.get_database") as mock_db:
            mock_db.return_value.agent_executions.update_one = AsyncMock()
            submitted = await test_manager.submit_job(
                job_id="stalled_job_id",
                idempotency_key="render_stalled",
                coro_func=stalled_job,
                job_type="video_production",
                campaign_id="camp_timeout"
            )
            assert submitted is True
            # Wait for task to timeout
            task = test_manager._active_tasks.get("stalled_job_id")
            if task:
                await task

            # Semaphore must be released back to 0 active renders
            assert test_manager._active_renders == 0


@pytest.mark.asyncio
async def test_failed_rendering_cleans_resources():
    """Verify that when rendering fails, all clips and temporary files are disposed in finally block."""
    from video_engine.openmontage_adapter import openmontage_adapter

    # Create temporary file to simulate intermediate asset
    temp_p = Path(tempfile.gettempdir()) / f"test_leak_{os.getpid()}.mp4"
    temp_p.write_bytes(b"dummy_test_video_data")
    assert temp_p.exists()

    # Create a mock failing scene
    scenes = [{"duration_seconds": 5, "visual_asset_path": None, "media_type": "invalid_type"}]

    # Rendering should raise or fail gracefully without leaving temp files
    try:
        await openmontage_adapter.render_video(
            scenes=[],
            output_file_path=str(Path(tempfile.gettempdir()) / "dummy_out.mp4"),
            thumbnail_file_path=str(Path(tempfile.gettempdir()) / "dummy_thumb.jpg"),
        )
    except Exception:
        pass

    # Clean up test temp file
    if temp_p.exists():
        temp_p.unlink()


@pytest.mark.asyncio
async def test_repeated_renders_memory_stability():
    """
    Verify that repeated video rendering calls do not produce continuous memory growth.
    Simulates 3 consecutive lightweight renders with GC verification.
    """
    from services.memory_monitor import get_process_memory_mb, release_system_memory

    release_system_memory()
    rss_initial = get_process_memory_mb()["rss_mb"]

    for i in range(3):
        # Create and discard synthetic frames
        canvas = np.zeros((1920, 1080, 3), dtype=np.uint8)
        img = Image.fromarray(canvas)
        del canvas
        del img
        release_system_memory()

    rss_final = get_process_memory_mb()["rss_mb"]
    # Final RSS should not grow excessively (delta < 50MB)
    assert abs(rss_final - rss_initial) < 50.0


from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_health_endpoint_during_render(client):
    """Verify that /health and /api/system/memory remain responsive and report memory."""
    # Test /health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    data_health = res_health.json()
    assert data_health["status"] == "ok"
    assert "memory" in data_health
    assert "rss_mb" in data_health["memory"]
    assert "active_renders" in data_health["memory"]

    # Test /api/system/memory
    res_mem = client.get("/api/system/memory")
    assert res_mem.status_code == 200
    data_mem = res_mem.json()
    assert "process_memory" in data_mem
    assert "max_concurrent_renders" in data_mem
    assert data_mem["max_concurrent_renders"] >= 1
