"""
CrowdWisdom AI Studio — MongoDB Database Connection
Uses motor (async MongoDB driver) with beanie ODM.
"""
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import settings, mask_connection_url

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """Initialize MongoDB connection on application startup."""
    global _client, _db
    masked_url = mask_connection_url(settings.MONGODB_URL)
    try:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=50,
        )
        _db = _client[settings.MONGODB_DB_NAME]
        # Verify connection
        await _client.admin.command("ping")
        logger.info(f"Connected to MongoDB ({settings.MONGODB_DB_NAME}) at {masked_url}")
        await _ensure_indexes()
    except Exception as e:
        sanitized_error = mask_connection_url(str(e))
        logger.error(f"Failed to connect to MongoDB ({masked_url}): {sanitized_error}")
        raise RuntimeError(f"MongoDB connection failed ({masked_url}): {sanitized_error}") from None


async def close_mongo_connection() -> None:
    """Close MongoDB connection on application shutdown."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """Return the active database instance, lazily connecting if necessary."""
    global _client, _db
    if _db is None:
        masked_url = mask_connection_url(settings.MONGODB_URL)
        try:
            _client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
            )
            _db = _client[settings.MONGODB_DB_NAME]
        except Exception as e:
            sanitized = mask_connection_url(str(e))
            logger.error(f"Lazy connection to MongoDB failed ({masked_url}): {sanitized}")
            raise RuntimeError(f"Database not initialized ({masked_url}): {sanitized}") from None
    return _db


async def _ensure_indexes() -> None:
    """Create indexes for all collections."""
    db = get_database()
    # Users
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    # Campaigns
    await db.campaigns.create_index("owner_id")
    await db.campaigns.create_index("status")
    await db.campaigns.create_index("created_at")
    # Agent executions
    await db.agent_executions.create_index("campaign_id")
    await db.agent_executions.create_index("agent_type")
    await db.agent_executions.create_index("status")
    await db.agent_executions.create_index("created_at")
    # Research jobs
    await db.research_jobs.create_index("campaign_id")
    await db.research_jobs.create_index("status")
    # Advertisements
    await db.advertisements.create_index("campaign_id")
    await db.advertisements.create_index("research_job_id")
    await db.advertisements.create_index([("advertiser", 1), ("ad_id", 1)], unique=True)
    # Scripts
    await db.scripts.create_index("campaign_id")
    await db.scripts.create_index("status")
    # Video jobs
    await db.video_jobs.create_index("campaign_id")
    await db.video_jobs.create_index("script_id")
    await db.video_jobs.create_index("status")
    # Workflow tasks
    await db.workflow_tasks.create_index("campaign_id")
    await db.workflow_tasks.create_index("status")
    # Execution logs
    await db.execution_logs.create_index("execution_id")
    await db.execution_logs.create_index("campaign_id")
    await db.execution_logs.create_index("created_at")
    # Integrations
    await db.integrations.create_index("provider_name", unique=True)
    logger.info("MongoDB indexes ensured.")

