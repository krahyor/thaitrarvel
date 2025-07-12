from fastapi import APIRouter
from . import user_router
from . import authentication_router
from . import province_tax_router

router = APIRouter(prefix="/v1")
router.include_router(user_router.router)
router.include_router(authentication_router.router)
router.include_router(province_tax_router.router)
