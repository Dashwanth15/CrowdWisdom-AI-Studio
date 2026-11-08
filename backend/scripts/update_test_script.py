import asyncio
import sys
from pathlib import Path
from bson import ObjectId
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.connection import connect_to_mongo, close_mongo_connection, get_database

async def update_script():
    await connect_to_mongo()
    db = get_database()
    script_id = ObjectId('6aef2e9591eea0f23a8051eb')
    
    scenes = [
        {
            'scene_number': 1,
            'duration_seconds': 11,
            'scene_visual_type': 'human_cinematography',
            'media_type': 'ai_image',
            'visual_asset_path': 'backend/media/assets/fallback_library/human_marcus_options.jpg',
            'visual_asset_url': '/media/assets/fallback_library/human_marcus_options.jpg',
            'visual_asset_status': 'completed',
            'visual_asset_provider': 'verified_commercial_library',
            'camera_motion': 'slow_zoom_in',
            'transition': 'cinematic_crossfade',
            'visual_description': 'Intense male institutional options strategist in a modern glass office at dawn, intently reviewing market volatility.',
            'voiceover': 'Market makers love retail chaos. The more conflicting alerts you receive, the more emotional mistakes you make.',
            'on_screen_text': 'Conflicting Newsfeeds = Emotional Drawdowns',
            'audio_direction': 'Tense low-frequency drone with rapid ticker clicks'
        },
        {
            'scene_number': 2,
            'duration_seconds': 11,
            'scene_visual_type': 'human_cinematography',
            'media_type': 'ai_image',
            'visual_asset_path': 'backend/media/assets/fallback_library/human_dawn_workstation.jpg',
            'visual_asset_url': '/media/assets/fallback_library/human_dawn_workstation.jpg',
            'visual_asset_status': 'completed',
            'visual_asset_provider': 'verified_commercial_library',
            'camera_motion': 'pan_right',
            'transition': 'cinematic_crossfade',
            'visual_description': 'Professional quantitative analyst in a modern high-rise office at dawn intently studying live order flow and candlestick charts.',
            'voiceover': 'Institutional algorithms don\'t read sensational headlines. They measure aggregate crowd conviction and order flow skew.',
            'on_screen_text': 'Don\'t Trade the News. Trade Collective Conviction.',
            'audio_direction': 'Crescendo of distorted audio chatter cutting to dead silence'
        },
        {
            'scene_number': 3,
            'duration_seconds': 11,
            'scene_visual_type': 'product_demo',
            'media_type': 'product_demo',
            'product_demo_mode': 'hardware_projection',
            'visual_asset_path': 'backend/media/assets/fallback_library/platform_crowdwisdom_ui.jpg',
            'visual_asset_url': '/media/assets/fallback_library/platform_crowdwisdom_ui.jpg',
            'visual_asset_status': 'completed',
            'visual_asset_provider': 'dynamic_product_demo_canvas',
            'camera_motion': 'slow_zoom_in',
            'transition': 'cinematic_crossfade',
            'visual_description': 'Extreme close-up on executive tablet device on a boardroom desk displaying the animated CrowdPulse institutional conviction radar.',
            'voiceover': 'CrowdWisdom\'s Pro Crowd Bars aggregate real trader expectations, revealing true consensus before the market moves.',
            'on_screen_text': 'Pro Crowd Bars: Real-Time Trader Conviction',
            'audio_direction': 'Crisp harmonic synthesizer chord with clean UI haptic chime'
        },
        {
            'scene_number': 4,
            'duration_seconds': 12,
            'scene_visual_type': 'human_cinematography',
            'media_type': 'ai_image',
            'visual_asset_path': 'backend/media/assets/fallback_library/human_city_rooftop_terrace.jpg',
            'visual_asset_url': '/media/assets/fallback_library/human_city_rooftop_terrace.jpg',
            'visual_asset_status': 'completed',
            'visual_asset_provider': 'verified_commercial_library',
            'camera_motion': 'slow_zoom_in',
            'transition': 'fade_to_black',
            'visual_description': 'Professional portfolio executive standing calmly on a high-rise terrace overlooking the city skyline at dawn with complete clarity.',
            'voiceover': 'Stop feeding the noise machine. Trade what the data shows at CrowdWisdomTrading.com.',
            'on_screen_text': 'CrowdWisdomTrading.com — Trade What the Data Shows',
            'audio_direction': 'Triumphant musical resolution'
        }
    ]
    
    res = await db.scripts.update_one(
        {'_id': script_id},
        {'$set': {'scenes': scenes, 'status': 'approved', 'updated_at': datetime.now(timezone.utc)}}
    )
    print(f'Successfully updated script scenes: {res.modified_count}')
    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(update_script())

