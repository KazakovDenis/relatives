from fastapi import APIRouter

from . import auth, tree

router = APIRouter(prefix='/ui')
router.include_router(auth.ui_router)
router.include_router(tree.ui_router)
