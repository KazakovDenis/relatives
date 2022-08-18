from fastapi import APIRouter

from . import persons


router = APIRouter(prefix='/api/v1')
router.include_router(persons.api_router)
