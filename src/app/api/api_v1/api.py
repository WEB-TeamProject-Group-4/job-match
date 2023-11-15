from fastapi import APIRouter
from app.api.api_v1.endpoints import users, login, utils

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(utils.router)