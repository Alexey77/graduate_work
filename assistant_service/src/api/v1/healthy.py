from fastapi import APIRouter, Depends, status

from schemes import ResponseMessage
from services.healthy import HealthCheckService, get_health_check_service

router = APIRouter()


@router.get("/live",
            status_code=status.HTTP_200_OK,
            response_model=ResponseMessage)
async def liveness_check(service: HealthCheckService = Depends(get_health_check_service)):
    return ResponseMessage(message="Service is running")
