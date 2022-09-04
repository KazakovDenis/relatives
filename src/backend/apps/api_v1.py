from fastapi import APIRouter

from . import auth, tree


router = APIRouter(prefix='/api/v1')
router.include_router(auth.api_router)
router.include_router(tree.api_router)
