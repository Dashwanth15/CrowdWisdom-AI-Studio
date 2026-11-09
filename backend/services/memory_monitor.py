"""
CrowdWisdom AI Studio — Production Memory Monitoring & Resource Management Service
Tracks process RSS/VMS memory, detects allocation spikes during video rendering,
enforces memory thresholds, and ensures prompt garbage collection and OS heap return.
"""
import os
import gc
import sys
import ctypes
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("memory_monitor")

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


def get_process_memory_mb() -> Dict[str, float]:
    """
    Returns current process memory in megabytes (MB).
    rss: Resident Set Size (physical memory occupied)
    vms: Virtual Memory Size (total virtual address space)
    """
    if _HAS_PSUTIL:
        try:
            proc = psutil.Process()
            mem = proc.memory_info()
            return {
                "rss_mb": round(mem.rss / (1024 * 1024), 2),
                "vms_mb": round(mem.vms / (1024 * 1024), 2),
            }
        except Exception as e:
            logger.debug(f"psutil memory read failed: {e}")

    # Fallback for standard environments
    return {"rss_mb": 0.0, "vms_mb": 0.0}


def get_system_memory_mb() -> Dict[str, float]:
    """Returns system-wide total and available memory in MB."""
    if _HAS_PSUTIL:
        try:
            vm = psutil.virtual_memory()
            return {
                "total_mb": round(vm.total / (1024 * 1024), 2),
                "available_mb": round(vm.available / (1024 * 1024), 2),
                "used_percent": round(vm.percent, 1),
            }
        except Exception as e:
            logger.debug(f"psutil system memory read failed: {e}")

    return {"total_mb": 0.0, "available_mb": 0.0, "used_percent": 0.0}


def release_system_memory() -> float:
    """
    Forces Python cyclic garbage collection and instructs the OS C-library (glibc on Linux)
    to release unused dynamic memory arenas back to the kernel.
    Returns post-release RSS in MB.
    """
    # 1. Force cyclic garbage collection across all 3 generations
    collected = gc.collect()
    logger.debug(f"[MemoryMonitor] Python GC collected {collected} unreachable objects.")

    # 2. Instruct glibc (Linux container on Render) to trim freed pages
    if sys.platform.startswith("linux"):
        try:
            libc = ctypes.CDLL("libc.so.6")
            if hasattr(libc, "malloc_trim"):
                libc.malloc_trim(0)
                logger.debug("[MemoryMonitor] glibc malloc_trim(0) called successfully.")
        except Exception as trim_err:
            logger.debug(f"[MemoryMonitor] glibc malloc_trim notice: {trim_err}")

    post_mem = get_process_memory_mb()
    return post_mem["rss_mb"]


class MemoryTracker:
    """
    Context manager for measuring and logging memory consumption during heavy workloads.
    Tracks initial RSS, peak RSS, final RSS, and net memory delta.
    """

    def __init__(self, job_id: str, job_type: str = "video_rendering", limit_mb: float = 450.0):
        self.job_id = job_id
        self.job_type = job_type
        self.limit_mb = limit_mb
        self.initial_rss = 0.0
        self.peak_rss = 0.0
        self.final_rss = 0.0
        self.post_gc_rss = 0.0
        self._sampling = False
        self._sample_task: Optional[asyncio.Task] = None

    async def __aenter__(self):
        # Force baseline cleanup before measuring
        release_system_memory()
        mem = get_process_memory_mb()
        self.initial_rss = mem["rss_mb"]
        self.peak_rss = self.initial_rss

        logger.info(
            f"[MEMORY_MONITOR] Job '{self.job_id}' started | "
            f"Type: {self.job_type} | Initial RSS: {self.initial_rss:.1f} MB | "
            f"Limit: {self.limit_mb:.0f} MB"
        )

        # Launch periodic background sampler during execution
        self._sampling = True
        self._sample_task = asyncio.create_task(self._sampler_loop())
        return self

    async def _sampler_loop(self):
        """Samples RSS memory every 500ms to catch transient peaks."""
        while self._sampling:
            try:
                mem = get_process_memory_mb()
                rss = mem["rss_mb"]
                if rss > self.peak_rss:
                    self.peak_rss = rss
                    if self.peak_rss >= self.limit_mb * 0.90:
                        logger.warning(
                            f"[MEMORY_ALERT] Job '{self.job_id}' approaching limit! "
                            f"Current RSS: {rss:.1f} MB / Limit: {self.limit_mb:.0f} MB"
                        )
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception:
                break

    def record_peak(self, current_rss: Optional[float] = None):
        """Explicitly record or update peak RSS from a synchronous thread."""
        if current_rss is None:
            current_rss = get_process_memory_mb()["rss_mb"]
        if current_rss > self.peak_rss:
            self.peak_rss = current_rss

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._sampling = False
        if self._sample_task and not self._sample_task.done():
            self._sample_task.cancel()
            try:
                await self._sample_task
            except asyncio.CancelledError:
                pass

        # Capture final memory before explicit GC
        self.final_rss = get_process_memory_mb()["rss_mb"]
        if self.final_rss > self.peak_rss:
            self.peak_rss = self.final_rss

        # Perform comprehensive GC and malloc trim
        self.post_gc_rss = release_system_memory()

        delta_mb = round(self.post_gc_rss - self.initial_rss, 2)
        status = "FAILED" if exc_type else "COMPLETED"

        log_level = logging.WARNING if self.peak_rss >= self.limit_mb * 0.85 else logging.INFO
        logger.log(
            log_level,
            f"[MEMORY_MONITOR] Job '{self.job_id}' {status} | "
            f"Initial: {self.initial_rss:.1f} MB | Peak: {self.peak_rss:.1f} MB | "
            f"Final: {self.final_rss:.1f} MB | Post-GC: {self.post_gc_rss:.1f} MB | "
            f"Net Delta: {'+' if delta_mb >= 0 else ''}{delta_mb:.1f} MB"
        )


memory_monitor_service = {
    "get_process_memory_mb": get_process_memory_mb,
    "get_system_memory_mb": get_system_memory_mb,
    "release_system_memory": release_system_memory,
    "MemoryTracker": MemoryTracker,
}

