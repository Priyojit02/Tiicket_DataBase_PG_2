# Routes Package
from fastapi import APIRouter
from app.routes.auth_routes import router as auth_router
from app.routes.ticket_routes import router as ticket_router
from app.routes.user_routes import router as user_router
from app.routes.admin_routes import router as admin_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.email_routes import router as email_router


def register_routes(app):
    """Register all routes with the FastAPI app"""
    api_router = APIRouter(prefix="")
    
    api_router.include_router(auth_router)
    api_router.include_router(ticket_router)
    api_router.include_router(user_router)
    api_router.include_router(admin_router)
    api_router.include_router(analytics_router)
    api_router.include_router(email_router)
    
    app.include_router(api_router)


__all__ = [
    "register_routes",
    "auth_router",
    "ticket_router",
    "user_router",
    "admin_router",
    "analytics_router",
    "email_router"
]
