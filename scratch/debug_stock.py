import asyncio
import sys
sys.path.insert(0, r"backend")
from services.visual_asset_service import VisualAssetService, STOCK_FOOTAGE_MANIFEST

async def debug_clip(query):
    service = VisualAssetService()
    print(f"\n--- Debugging: {query[:50]} ---")
    val_rel = service.validate_visual_relevance(query)
    print("validate_visual_relevance:", val_rel)
    
    # Check active_stock_dir
    from config import settings
    from pathlib import Path
    stock_dirs = [
        service.stock_dir,
        service.assets_dir / "stock_footage",
        Path("media") / "assets" / "stock_footage",
        Path("backend") / "media" / "assets" / "stock_footage",
        Path(settings.MEDIA_DIR) / "assets" / "stock_footage",
        Path(__file__).parent.parent / "media" / "assets" / "stock_footage",
        Path(__file__).parent.parent.parent / "media" / "assets" / "stock_footage",
    ]
    print("Checking stock_dirs:")
    for d in stock_dirs:
        mp4s = list(d.glob("*.mp4")) if d.exists() and d.is_dir() else []
        print(f"  {d}: exists={d.exists()}, mp4s={len(mp4s)}")

q1 = "Close-up macro of an intense trader's hands typing rapidly at a trading workstation amidst flashing sell-off candlestick monitors and conflicting financial news alerts."
asyncio.run(debug_clip(q1))

