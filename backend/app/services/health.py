import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class HealthService:
    @staticmethod
    async def get_status() -> dict:
        status = {"status": "ok", "timestamp": datetime.now(timezone.utc)}
        logger.debug("Generated health status %s", status)
        return status
