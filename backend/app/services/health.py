from datetime import datetime, timezone


class HealthService:
    @staticmethod
    async def get_status() -> dict:
        return {"status": "ok", "timestamp": datetime.now(timezone.utc)}
