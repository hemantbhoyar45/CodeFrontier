from fastapi import APIRouter

from backend.app.api.v1.health import router as health_router
from backend.app.modules.audit.routes import router as audit_router
from backend.app.modules.auth.routes import router as auth_router
from backend.app.modules.documents.routes import router as documents_router
from backend.app.modules.dashboard.routes import router as dashboard_router
from backend.app.modules.handovers.routes import router as handovers_router
from backend.app.modules.integrations.routes import router as integrations_router
from backend.app.modules.knowledge.routes import router as knowledge_router
from backend.app.modules.organizations.routes import router as organizations_router
from backend.app.modules.projects.routes import router as projects_router
from backend.app.modules.reviews.routes import router as reviews_router
from backend.app.modules.users.routes import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(organizations_router)
api_router.include_router(users_router)
api_router.include_router(projects_router)
api_router.include_router(documents_router)
api_router.include_router(knowledge_router)
api_router.include_router(handovers_router)
api_router.include_router(audit_router)
api_router.include_router(dashboard_router)
api_router.include_router(reviews_router)
api_router.include_router(integrations_router)
