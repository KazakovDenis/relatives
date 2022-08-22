from fastapi import APIRouter

from . import tree


router = APIRouter(prefix='/ui')
router.include_router(tree.ui_router)
