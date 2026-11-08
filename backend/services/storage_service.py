"""
CrowdWisdom AI Studio — Storage Abstraction Service
Provides a unified interface for media and asset persistence,
supporting local filesystem storage and future S3-compatible object storage.
"""
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, BinaryIO
from config import settings
import logging

logger = logging.getLogger(__name__)


class BaseStorageService(ABC):
    """Abstract storage interface for all video, audio, image, and JSON assets."""

    @abstractmethod
    async def save_file(
        self,
        file_path_relative: str,
        content: bytes,
        mime_type: Optional[str] = None
    ) -> str:
        """Saves file content and returns its public or relative access URL/path."""
        pass

    @abstractmethod
    async def get_file_path(self, file_path_relative: str) -> Optional[str]:
        """Resolves local absolute path for direct file reading or ffmpeg/moviepy access."""
        pass

    @abstractmethod
    async def delete_file(self, file_path_relative: str) -> bool:
        """Deletes a file if present."""
        pass

    @abstractmethod
    async def file_exists(self, file_path_relative: str) -> bool:
        """Checks if a file exists."""
        pass

    @abstractmethod
    def get_url(self, file_path_relative: str) -> str:
        """Returns browser-accessible URL for the asset."""
        pass


class LocalStorageService(BaseStorageService):
    """Local filesystem storage implementation."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.MEDIA_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Ensure subdirectories exist
        (self.base_dir / "videos").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "thumbnails").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "assets").mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        file_path_relative: str,
        content: bytes,
        mime_type: Optional[str] = None
    ) -> str:
        target = self.base_dir / file_path_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(content)
        return self.get_url(file_path_relative)

    async def get_file_path(self, file_path_relative: str) -> Optional[str]:
        target = self.base_dir / file_path_relative
        if target.exists():
            return str(target)
        return None

    async def delete_file(self, file_path_relative: str) -> bool:
        target = self.base_dir / file_path_relative
        if target.exists():
            try:
                target.unlink()
                return True
            except Exception as e:
                logger.error(f"Failed to delete {target}: {e}")
                return False
        return False

    async def file_exists(self, file_path_relative: str) -> bool:
        return (self.base_dir / file_path_relative).exists()

    def get_url(self, file_path_relative: str) -> str:
        # Normalizes to /api/media/{category}/{filename}
        clean_path = file_path_relative.replace("\\", "/").lstrip("/")
        return f"/api/media/{clean_path}"

    async def prune_prescaled_cache(self, max_age_hours: int = 12, dry_run: bool = False) -> dict:
        """
        Safely prunes intermediate FFmpeg fast-prescaling MP4 files older than max_age_hours.
        These are reconstructed automatically on demand during video rendering.
        """
        import time
        reclaimed_bytes = 0
        pruned_files = []
        now = time.time()
        cutoff = now - (max_age_hours * 3600)

        stock_dir = self.base_dir / "assets" / "stock_footage"
        if stock_dir.exists():
            for p in stock_dir.glob("prescaled_*.mp4"):
                try:
                    st = p.stat()
                    if st.st_mtime <= cutoff or max_age_hours == 0:
                        reclaimed_bytes += st.st_size
                        pruned_files.append(str(p.name))
                        if not dry_run:
                            p.unlink()
                            logger.info(f"[StorageLifecycle] Pruned prescaled cache: {p.name}")
                except Exception as e:
                    logger.warning(f"[StorageLifecycle] Error checking {p.name}: {e}")

        return {
            "pruned_count": len(pruned_files),
            "reclaimed_bytes": reclaimed_bytes,
            "reclaimed_mb": round(reclaimed_bytes / (1024 * 1024), 2),
            "dry_run": dry_run,
            "files": pruned_files,
        }

    async def prune_test_renders(self, max_age_hours: int = 24, dry_run: bool = False) -> dict:
        """
        Safely prunes ad-hoc developer test renders from backend/media/test_renders.
        Never affects production video jobs in backend/media/videos/.
        """
        import time
        reclaimed_bytes = 0
        pruned_files = []
        now = time.time()
        cutoff = now - (max_age_hours * 3600)

        test_dir = self.base_dir / "test_renders"
        if test_dir.exists():
            for p in test_dir.iterdir():
                if p.is_file():
                    try:
                        st = p.stat()
                        if st.st_mtime <= cutoff or max_age_hours == 0:
                            reclaimed_bytes += st.st_size
                            pruned_files.append(str(p.name))
                            if not dry_run:
                                p.unlink()
                                logger.info(f"[StorageLifecycle] Pruned test render: {p.name}")
                    except Exception as e:
                        logger.warning(f"[StorageLifecycle] Error pruning test render {p.name}: {e}")

        return {
            "pruned_count": len(pruned_files),
            "reclaimed_bytes": reclaimed_bytes,
            "reclaimed_mb": round(reclaimed_bytes / (1024 * 1024), 2),
            "dry_run": dry_run,
            "files": pruned_files,
        }

    def get_storage_breakdown(self) -> dict:
        """Calculates storage consumption across subdirectories."""
        breakdown = {}
        total = 0
        if self.base_dir.exists():
            for d in self.base_dir.iterdir():
                if d.is_dir():
                    sz = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
                    cnt = sum(1 for f in d.rglob("*") if f.is_file())
                    breakdown[d.name] = {
                        "size_mb": round(sz / (1024 * 1024), 2),
                        "file_count": cnt,
                    }
                    total += sz
        return {
            "base_dir": str(self.base_dir),
            "total_size_mb": round(total / (1024 * 1024), 2),
            "subdirectories": breakdown,
        }


class S3StorageService(BaseStorageService):
    """
    S3-compatible object storage (AWS S3, Cloudflare R2, MinIO).
    Extensible implementation when S3 credentials are configured in environment.
    """

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        region: str = "us-east-1"
    ):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.region = region
        self.local_cache = Path(settings.MEDIA_DIR) / "_cache"
        self.local_cache.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        file_path_relative: str,
        content: bytes,
        mime_type: Optional[str] = None
    ) -> str:
        # Cache locally first, then upload to S3 client
        cache_target = self.local_cache / file_path_relative
        cache_target.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_target, "wb") as f:
            f.write(content)
        logger.info(f"[S3Storage] Saved {file_path_relative} to cache. Ready for S3 put_object.")
        return self.get_url(file_path_relative)

    async def get_file_path(self, file_path_relative: str) -> Optional[str]:
        cache_target = self.local_cache / file_path_relative
        if cache_target.exists():
            return str(cache_target)
        return None

    async def delete_file(self, file_path_relative: str) -> bool:
        cache_target = self.local_cache / file_path_relative
        if cache_target.exists():
            cache_target.unlink()
        return True

    async def file_exists(self, file_path_relative: str) -> bool:
        return (self.local_cache / file_path_relative).exists()

    def get_url(self, file_path_relative: str) -> str:
        return f"/api/media/{file_path_relative}"


# Default storage singleton
storage_service: BaseStorageService = LocalStorageService()

