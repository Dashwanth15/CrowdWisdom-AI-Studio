import logging
from datetime import datetime, timezone
from typing import Optional, Set, List, Dict, Any
from bson import ObjectId
from database.connection import get_database

logger = logging.getLogger(__name__)

class AssetRegistryService:
    """
    Persistent Asset Usage Registry.
    Tracks asset allocations across campaigns, scripts, and scenes to prevent
    unintentional repetition, enforce diversity scoring, and manage asset cooldowns.
    """

    async def record_asset_usage(
        self,
        campaign_id: str,
        script_id: str,
        scene_number: int,
        asset_id: str,
        asset_type: str,
        filename: str,
        visual_treatment: str = "standard"
    ) -> None:
        """Records an asset allocation in MongoDB."""
        db = get_database()
        doc = {
            "campaign_id": str(campaign_id) if campaign_id else None,
            "script_id": str(script_id) if script_id else None,
            "scene_number": int(scene_number),
            "asset_id": str(asset_id),
            "asset_type": str(asset_type),
            "filename": str(filename),
            "visual_treatment": str(visual_treatment),
            "used_at": datetime.now(timezone.utc),
        }
        try:
            await db.asset_usage_registry.insert_one(doc)
            logger.debug(f"[AssetRegistry] Recorded usage: {filename} in campaign {campaign_id} scene {scene_number}")
        except Exception as e:
            logger.warning(f"[AssetRegistry] Failed to record usage: {e}")

    async def get_used_asset_ids_in_script(self, script_id: str) -> Set[str]:
        """Returns all asset filenames/IDs already used within the same script."""
        if not script_id:
            return set()
        db = get_database()
        try:
            cursor = db.asset_usage_registry.find({"script_id": str(script_id)}, {"filename": 1, "asset_id": 1})
            docs = await cursor.to_list(100)
            used = set()
            for d in docs:
                if d.get("filename"):
                    used.add(d["filename"])
                if d.get("asset_id"):
                    used.add(d["asset_id"])
            return used
        except Exception as e:
            logger.warning(f"[AssetRegistry] Error fetching script used assets: {e}")
            return set()

    async def get_recently_used_asset_ids(
        self,
        current_campaign_id: Optional[str] = None,
        lookback_campaigns: int = 3
    ) -> Set[str]:
        """
        Returns asset filenames/IDs used in recent campaigns to enforce cross-campaign diversity.
        Excludes the current campaign so regeneration has a clean comparison.
        """
        db = get_database()
        try:
            query: Dict[str, Any] = {}
            if current_campaign_id:
                query["campaign_id"] = {"$ne": str(current_campaign_id)}

            cursor = db.asset_usage_registry.find(query).sort("used_at", -1).limit(lookback_campaigns * 8)
            docs = await cursor.to_list(lookback_campaigns * 8)
            used = set()
            for d in docs:
                if d.get("filename"):
                    used.add(d["filename"])
                if d.get("asset_id"):
                    used.add(d["asset_id"])
            return used
        except Exception as e:
            logger.warning(f"[AssetRegistry] Error fetching recently used assets: {e}")
            return set()

    async def clear_script_usage(self, script_id: str) -> None:
        """Clears usage for a script upon explicit regeneration/re-render."""
        if not script_id:
            return
        db = get_database()
        try:
            await db.asset_usage_registry.delete_many({"script_id": str(script_id)})
            logger.info(f"[AssetRegistry] Cleared previous asset registry for script {script_id}")
        except Exception as e:
            logger.warning(f"[AssetRegistry] Error clearing script usage: {e}")

asset_registry = AssetRegistryService()

