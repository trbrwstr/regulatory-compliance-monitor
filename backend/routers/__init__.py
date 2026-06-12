from routers.alerts import router as alerts_router
from routers.subscriptions import router as subscriptions_router
from routers.sources import router as sources_router
from routers.regulations import router as regulations_router

__all__ = ["alerts_router", "subscriptions_router", "sources_router", "regulations_router"]
