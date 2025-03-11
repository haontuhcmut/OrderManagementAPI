from typing import Annotated
from fastapi import APIRouter, Depends

from app.categories.schemas import CategoryCreateModel
from app.auth.dependencies import RoleChecker, AccessTokenBearer, SessionDep
from app.categories.services import CategoryServices

admin_role_checker = Depends(RoleChecker(["admin"]))
category_services = CategoryServices()

categories_routes = APIRouter()


@categories_routes.post("/", dependencies=[admin_role_checker])
async def create_category(
    category_data: CategoryCreateModel,
    token_details: Annotated[dict, Depends(AccessTokenBearer())],
    session: SessionDep,
):
    new_category = await category_services.create_category(category_data, session)
    return new_category
