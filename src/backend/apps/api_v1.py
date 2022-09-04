from fastapi import APIRouter

from . import auth, core


router = APIRouter(prefix='/api/v1')
router.include_router(auth.api_router)
router.include_router(core.api_router)
