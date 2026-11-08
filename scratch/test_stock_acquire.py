import asyncio
import sys
sys.path.insert(0, r"backend")
from services.visual_asset_service import VisualAssetService, STOCK_FOOTAGE_MANIFEST

async def main():
    service = VisualAssetService()
    print("Manifest count:", len(STOCK_FOOTAGE_MANIFEST))
    for m in STOCK_FOOTAGE_MANIFEST:
        print("  Manifest entry:", m["id"], m["filename"], m["tags"][:5])
    
    q1 = "Close-up macro of an intense trader's hands typing rapidly at a trading workstation amidst flashing sell-off candlestick monitors and conflicting financial news alerts."
    clip1 = await service._acquire_openmontage_stock_clip(q1, "9:16", "test_hash_1")
    print(f"\nQuery 1: {q1[:50]}...\n  -> Result: {clip1}")

    q4 = "Professional trader standing calmly by a floor-to-ceiling glass window in a modern financial office overlooking the city skyline at dawn, confident and decisive."
    clip4 = await service._acquire_openmontage_stock_clip(q4, "9:16", "test_hash_4")
    print(f"\nQuery 4: {q4[:50]}...\n  -> Result: {clip4}")

if __name__ == "__main__":
    asyncio.run(main())

