from api.v1.endpoints import calls, heartbeat, realtime
from fastapi import APIRouter

api_v1_router = APIRouter()
api_v1_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_v1_router.include_router(heartbeat.router, prefix="/health", tags=["health"])
api_v1_router.include_router(realtime.router, prefix="/realtime", tags=["realtime"])
