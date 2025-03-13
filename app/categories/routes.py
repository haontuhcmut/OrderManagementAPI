from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.categories.schemas import CategoryCreateModel
from app.auth.dependencies import RoleChecker, AccessTokenBearer, SessionDep
from app.categories.services import CategoryServices
from app.db.models import Category

access_token_bearer = AccessTokenBearer()
admin_role_checker = Depends(RoleChecker(["admin"]))
role_checker = Depends(RoleChecker(["admin", "user"]))
category_services = CategoryServices()

categories_route = APIRouter()


@categories_route.post("/", dependencies=[admin_role_checker])
async def create_category(
    category_data: CategoryCreateModel,
    _: Annotated[dict, Depends(access_token_bearer)],
    session: SessionDep,
):
    new_category = await category_services.create_category(category_data, session)
    return new_category


@categories_route.get("/", response_model=list[Category], dependencies=[role_checker])
async def get_all_categories(
    session: SessionDep, _: Annotated[dict, Depends(access_token_bearer)]
):
    categories = await category_services.get_categories(session)
    return categories


@categories_route.get("/{category_name}")
async def get_category_item(
    category_name: str,
    session: SessionDep,
    _: Annotated[dict, Depends(access_token_bearer)],
):
    category = await category_services.category_item(category_name, session)
    return category


@categories_route.patch(
    "/{category_name}", response_model=Category, dependencies=[admin_role_checker]
)
async def update_category(
    category_name: str,
    category_to_update: CategoryCreateModel,
    _: Annotated[dict, Depends(access_token_bearer)],
    session: SessionDep,
):
    updated_category = await category_services.update_category(
        category_name=category_name, update_data=category_to_update, session=session
    )

    if updated_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    else:
        return updated_category
