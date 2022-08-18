from fastapi import APIRouter

from . import persons


router = APIRouter(prefix='/ui')
router.include_router(persons.ui_router)
