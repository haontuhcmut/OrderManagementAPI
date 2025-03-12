from typing import Annotated
from fastapi import APIRouter, Depends

from app.categories.schemas import CategoryCreateModel
from app.auth.dependencies import RoleChecker, AccessTokenBearer, SessionDep
from app.categories.services import CategoryServices
from app.db.models import Category

admin_role_checker = Depends(RoleChecker(["admin"]))
role_checker = Depends(RoleChecker(["admin", "user"]))
category_services = CategoryServices()

categories_routes = APIRouter()


@categories_routes.post("/category", dependencies=[admin_role_checker])
async def create_category(
    category_data: CategoryCreateModel,
    token_details: Annotated[dict, Depends(AccessTokenBearer())],
    session: SessionDep,
):
    new_category = await category_services.create_category(category_data, session)
    return new_category

@categories_routes.get("/get-categories", response_model=list[Category], dependencies=[role_checker])
async def get_all_categories(session: SessionDep, _: Annotated[bool, Depends(AccessTokenBearer)]):
    categories = await category_services.read_categories(session)
    return categories

@categories_routes.get("/category/{category_name}")
async def get_category_item(category_name: str, session: SessionDep):
    category = await category_services.category_item(category_name, session)
    return category

@categories_routes.patch("/category/")

