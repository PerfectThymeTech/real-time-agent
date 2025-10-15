from api.v1.endpoints import heartbeat, realtime
from fastapi import APIRouter

api_v1_router = APIRouter()
api_v1_router.include_router(heartbeat.router, prefix="/health", tags=["health"])
api_v1_router.include_router(realtime.router, prefix="/realtime", tags=["realtime"])
