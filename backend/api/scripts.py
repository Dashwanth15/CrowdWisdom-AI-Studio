"""
CrowdWisdom AI Studio — Scripts API Routes
Script review, approval, rejection, and management.
"""
import os
import json
import logging
from datetime import datetime, timezone
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Response
from bson import ObjectId

from database.connection import get_database
from models.schemas import ScriptOut, ScriptStatus, SceneSpec
from api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scripts", tags=["Scripts"])


def _serialize_script(doc: dict) -> ScriptOut:
    title = doc.get("campaign_title") or doc.get("title")
    if not title:
        approach_str = str(doc.get("approach", "pain_point")).replace("_", " ").title()
        title = f"{approach_str} Concept"

    created_at = doc.get("created_at") or datetime.now(timezone.utc)
    updated_at = doc.get("updated_at") or created_at

    raw_hook = doc.get("visual_hook")
    if isinstance(raw_hook, dict):
        visual_hook = raw_hook.get("visual_description") or json.dumps(raw_hook)
    elif raw_hook is not None:
        visual_hook = str(raw_hook)
    else:
        visual_hook = None

    status_val = doc.get("status", "draft")
    valid_statuses = {s.value for s in ScriptStatus}
    if status_val not in valid_statuses:
        status_val = "draft"

    raw_scenes = doc.get("scenes", [])
    normalized_scenes = []
    for idx, sc in enumerate(raw_scenes if isinstance(raw_scenes, list) else [], 1):
        if isinstance(sc, dict):
            normalized_scenes.append(SceneSpec(
                scene_number=sc.get("scene_number", idx),
                duration_seconds=float(sc.get("duration_seconds", 5)),
                visual_description=sc.get("visual_description") or "Cinematic visualization",
                visual_asset_path=sc.get("visual_asset_path"),
                visual_asset_url=sc.get("visual_asset_url"),
                visual_asset_status=sc.get("visual_asset_status", "pending"),
                visual_asset_provider=sc.get("visual_asset_provider"),
                camera_direction=sc.get("camera_direction") or "Slow push-in",
                camera_motion=sc.get("camera_motion", "slow_zoom_in"),
                animation=sc.get("animation", "animated_charts"),
                voiceover=sc.get("voiceover") or "",
                on_screen_text=sc.get("on_screen_text") or "",
                audio_direction=sc.get("audio_direction") or "Subtle ambient synthesizer",
                transition=sc.get("transition") or "cinematic_crossfade",
                asset_references=sc.get("asset_references", [])
            ))

    # Normalize target audience
    raw_audience = doc.get("target_audience")
    if isinstance(raw_audience, list):
        target_audience_val = ", ".join(str(x) for x in raw_audience)
    elif raw_audience is not None:
        target_audience_val = str(raw_audience)
    else:
        target_audience_val = None

    return ScriptOut(
        id=str(doc["_id"]),
        campaign_id=doc.get("campaign_id", ""),
        approach=doc.get("approach", "pain_point"),
        status=status_val,
        version=doc.get("version", 1),
        title=title,
        campaign_title=title,
        target_audience=target_audience_val,
        pain_point=doc.get("pain_point"),
        marketing_angle=doc.get("marketing_angle"),
        core_message=doc.get("core_message"),
        unique_selling_proposition=doc.get("unique_selling_proposition"),
        emotional_direction=doc.get("emotional_direction"),
        visual_hook=visual_hook,
        full_script=doc.get("full_script"),
        scenes=normalized_scenes,
        voiceover_full=doc.get("voiceover_full"),
        on_screen_texts=doc.get("on_screen_texts", []),
        music_direction=doc.get("music_direction"),
        sound_effects=doc.get("sound_effects", []),
        call_to_action=doc.get("call_to_action"),
        estimated_duration_seconds=doc.get("estimated_duration_seconds"),
        research_references=doc.get("research_references", []),
        supporting_evidence=doc.get("supporting_evidence", []),
        approved_by=doc.get("approved_by"),
        approved_at=doc.get("approved_at"),
        rejection_reason=doc.get("rejection_reason"),
        created_at=created_at,
        updated_at=updated_at,
    )


@router.get("", response_model=List[ScriptOut])
async def list_scripts(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
    status: Optional[ScriptStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_database()
    query: dict = {}
    if campaign_id:
        query["campaign_id"] = campaign_id
    if status:
        query["status"] = status.value

    cursor = db.scripts.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)
    return [_serialize_script(d) for d in docs]


@router.get("/{script_id}", response_model=ScriptOut)
async def get_script(
    script_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(script_id):
        raise HTTPException(status_code=400, detail="Invalid script ID.")
    doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Script not found.")
    return _serialize_script(doc)


@router.get("/{script_id}/export")
async def export_script_json(
    script_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Export complete storyboard script in human-readable formatted JSON."""
    db = get_database()
    if not ObjectId.is_valid(script_id):
        raise HTTPException(status_code=400, detail="Invalid script ID.")

    doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Script not found.")

    serialized = _serialize_script(doc).model_dump(mode="json")
    export_payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "script_id": script_id,
        "script": serialized,
    }
    json_bytes = json.dumps(export_payload, indent=2).encode("utf-8")
    filename = f"script_{script_id}_{serialized.get('approach', 'storyboard')}.json"
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/{script_id}/approve", response_model=ScriptOut)
async def approve_script(
    script_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Approve a script for video production."""
    db = get_database()
    if not ObjectId.is_valid(script_id):
        raise HTTPException(status_code=400, detail="Invalid script ID.")

    doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Script not found.")

    # 1. Status Check: Do not approve scripts that are actively generating or failed
    status = doc.get("status", "draft")
    if status in ("generating", "running", "in_progress"):
        raise HTTPException(
            status_code=400,
            detail="Cannot approve script while generation is still in progress. Please wait for the script to finish.",
        )
    if status == "failed":
        raise HTTPException(
            status_code=400,
            detail="Cannot approve a failed script. Please regenerate the script first.",
        )

    # 2. Campaign Association Check
    if not doc.get("campaign_id"):
        raise HTTPException(
            status_code=400,
            detail="Validation Error: Script is not associated with any valid campaign.",
        )

    # 3. Title Check
    title = (doc.get("campaign_title") or doc.get("title") or "").strip()
    if not title or title.lower().startswith("untitled") or title.lower().startswith("generating"):
        raise HTTPException(
            status_code=400,
            detail="Validation Error: Script must have a valid title before it can be approved.",
        )

    # 4. Core Message Check
    core_msg = doc.get("core_message")
    if not core_msg or not str(core_msg).strip():
        raise HTTPException(
            status_code=400,
            detail="Validation Error: Script is missing its Core Message. Incomplete scripts cannot be approved.",
        )

    # 5. Storyboard Scenes Check (Minimum 3 required)
    scenes = doc.get("scenes", [])
    if not isinstance(scenes, list) or len(scenes) < 3:
        raise HTTPException(
            status_code=400,
            detail=f"Validation Error: Storyboard must have at least 3 fully specified scenes (found {len(scenes) if isinstance(scenes, list) else 0}). Incomplete scripts cannot be approved.",
        )

    # 6. Mandatory Scene Fields & Duration Validation
    total_dur = 0.0
    for idx, sc in enumerate(scenes, 1):
        if not isinstance(sc, dict):
            raise HTTPException(status_code=400, detail=f"Scene {idx} structure is invalid.")
        dur = sc.get("duration_seconds", 0)
        try:
            dur = float(dur)
        except (ValueError, TypeError):
            dur = 0.0

        if dur <= 0:
            raise HTTPException(status_code=400, detail=f"Scene {idx} duration must be a positive number.")
        total_dur += dur

        vis = (sc.get("visual_description") or "").strip()
        vo = (sc.get("voiceover") or "").strip()
        ost = (sc.get("on_screen_text") or "").strip()
        if not vis:
            raise HTTPException(
                status_code=400,
                detail=f"Scene {idx} is missing mandatory visual description.",
            )
        if not vo and not ost:
            raise HTTPException(
                status_code=400,
                detail=f"Scene {idx} is missing both voiceover narration and on-screen text.",
            )

    if total_dur < 10.0:
        raise HTTPException(
            status_code=400,
            detail=f"Validation Error: Total storyboard duration ({total_dur:.1f}s) is too short. Minimum duration is 10.0 seconds.",
        )

    # 7. Visual Assets Verification — Ensure scene visual assets exist before approving
    from services.visual_asset_service import visual_asset_service
    missing_assets = any(
        not sc.get("visual_asset_path") or not os.path.exists(str(sc.get("visual_asset_path")))
        for sc in scenes
    )
    if missing_assets:
        logger.info(f"[ScriptApproval] Generating missing scene visual assets for script {script_id}...")
        updated_scenes = await visual_asset_service.ensure_script_visual_assets(doc, db=db)
        doc["scenes"] = updated_scenes

    # Strict Validation Gate: Reject approval if any scene lacks a valid, resolvable asset
    failed_scenes = []
    for sc in doc.get("scenes", []):
        s_num = sc.get("scene_number", "?")
        m_type = sc.get("media_type")
        if m_type == "animated_chart":
            continue
        p = sc.get("visual_asset_path")
        if not p or not os.path.exists(str(p)) or sc.get("visual_asset_status") == "failed":
            failed_scenes.append(s_num)

    if failed_scenes:
        raise HTTPException(
            status_code=422,
            detail=f"Storyboard approval failed: Scene(s) {failed_scenes} visual assets could not be generated or resolved. Cannot approve storyboard with missing assets."
        )

    now = datetime.now(timezone.utc)
    await db.scripts.update_one(
        {"_id": ObjectId(script_id)},
        {
            "$set": {
                "status": "approved",
                "approved_by": str(current_user["_id"]),
                "approved_at": now,
                "rejection_reason": None,
                "updated_at": now,
            }
        },
    )

    # Update workflow task
    await db.workflow_tasks.update_one(
        {"campaign_id": doc["campaign_id"], "task_name": "Script Generation", "status": "awaiting_approval"},
        {"$set": {"status": "completed"}},
    )

    doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
    return _serialize_script(doc)


@router.post("/{script_id}/reject", response_model=ScriptOut)
async def reject_script(
    script_id: str,
    reason: str = Body(..., embed=True),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Reject a script with a reason."""
    db = get_database()
    if not ObjectId.is_valid(script_id):
        raise HTTPException(status_code=400, detail="Invalid script ID.")

    doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Script not found.")

    await db.scripts.update_one(
        {"_id": ObjectId(script_id)},
        {
            "$set": {
                "status": "rejected",
                "rejection_reason": reason,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
    return _serialize_script(doc)


@router.patch("/{script_id}", response_model=ScriptOut)
async def update_script(
    script_id: str,
    updates: dict = Body(...),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Update script content (scenes, voiceover, etc.)."""
    db = get_database()
    if not ObjectId.is_valid(script_id):
        raise HTTPException(status_code=400, detail="Invalid script ID.")

    # Only allow editing certain fields
    allowed_fields = {
        "scenes", "full_script", "voiceover_full", "on_screen_texts",
        "music_direction", "sound_effects", "call_to_action", "campaign_title",
        "marketing_angle", "core_message", "visual_hook",
    }
    safe_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    if not safe_updates:
        raise HTTPException(status_code=400, detail="No valid fields to update.")

    safe_updates["updated_at"] = datetime.now(timezone.utc)
    # Bump version on edit
    await db.scripts.update_one(
        {"_id": ObjectId(script_id)},
        {"$set": safe_updates, "$inc": {"version": 1}},
    )

    doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
    return _serialize_script(doc)


@router.delete("/clear-failed")
async def clear_failed_scripts(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Delete all failed or rejected script drafts to keep the database tidy."""
    db = get_database()
    res = await db.scripts.delete_many({"status": {"$in": ["failed", "rejected"]}})
    return {
        "message": f"Successfully deleted {res.deleted_count} failed/rejected scripts.",
        "deleted_count": res.deleted_count,
    }


@router.delete("/{script_id}")
async def delete_script(
    script_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Delete a script and its storyboard."""
    db = get_database()
    if not ObjectId.is_valid(script_id):
        raise HTTPException(status_code=400, detail="Invalid script ID.")

    script = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not script:
        raise HTTPException(status_code=404, detail="Script not found.")

    await db.scripts.delete_one({"_id": ObjectId(script_id)})
    return {"message": "Script deleted successfully.", "script_id": script_id}

