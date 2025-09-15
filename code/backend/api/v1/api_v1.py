from fastapi import APIRouter
from api.v1.endpoints import heartbeat

api_v1_router = APIRouter()
api_v1_router.include_router(heartbeat.router, prefix="/health", tags=["health"])
