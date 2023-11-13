from fastapi import APIRouter
from app.api.api_v1.endpoints import users, login

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(login.router)