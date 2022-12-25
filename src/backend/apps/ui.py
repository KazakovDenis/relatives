"""UI modules will be removed when frontend is ready."""
from fastapi import APIRouter

from . import auth, core


router = APIRouter(prefix='/ui')
router.include_router(auth.ui_router)
router.include_router(core.ui_router)
