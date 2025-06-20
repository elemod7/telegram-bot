from .start import router as start_router
from .access import router as access_router
from .admin import router as admin_router
from .reports import router as reports_router
from .errors import router as errors_router
from .menu import router as menu_router
from .broadcast import router as broadcast_router
from .shutdown_notice import router as shutdown_router

__all__ = [
    "start_router",
    "access_router",
    "admin_router",
    "reports_router",
    "errors_router",
    "menu_router",
    "broadcast_router",
    "shutdown_router"
]
