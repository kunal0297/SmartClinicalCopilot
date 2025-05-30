from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis import Redis
import iris

from app.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint that verifies the status of all dependencies.
    """
    health_status = {
        "status": "healthy",
        "dependencies": {
            "database": "healthy",
            "redis": "healthy",
            "iris": "healthy"
        }
    }

    # Check database connection
    try:
        db.execute("SELECT 1")
    except Exception as e:
        health_status["dependencies"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"

    # Check Redis connection
    try:
        redis = Redis.from_url(settings.REDIS_URL)
        redis.ping()
    except Exception as e:
        health_status["dependencies"]["redis"] = "unhealthy"
        health_status["status"] = "unhealthy"

    # Check IRIS connection
    try:
        iris_connection = iris.connect(
            host=settings.IRIS_HOST,
            port=settings.IRIS_PORT,
            namespace=settings.IRIS_NAMESPACE
        )
        iris_connection.close()
    except Exception as e:
        health_status["dependencies"]["iris"] = "unhealthy"
        health_status["status"] = "unhealthy"

    return health_status 