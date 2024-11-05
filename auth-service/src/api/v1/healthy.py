from fastapi import APIRouter, Depends
from schemas import ResponseMessage
from services.healthy import HealthCheckService, get_health_check_service

router = APIRouter()


@router.get("/live/", response_model=ResponseMessage)
async def liveness_check():
    return ResponseMessage(message="Service is alive")


@router.get("/ready/")
async def readiness_check(
    health_service: HealthCheckService = Depends(get_health_check_service),
):
    return {
        "Database status": await health_service.check_database(),
        "Cache status": await health_service.check_cache(),
    }
