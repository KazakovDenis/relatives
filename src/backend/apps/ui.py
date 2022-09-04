from fastapi import APIRouter

from . import auth, core


router = APIRouter(prefix='/ui')
router.include_router(auth.ui_router)
router.include_router(core.ui_router)
