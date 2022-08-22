from fastapi import APIRouter

from . import tree


router = APIRouter(prefix='/api/v1')
router.include_router(tree.api_router)
