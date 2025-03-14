import uuid

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.categories.schemas import CategoryCreateModel
from app.auth.dependencies import RoleChecker, AccessTokenBearer, SessionDep
from app.categories.services import CategoryServices
from app.db.models import Category

access_token_bearer = AccessTokenBearer()
admin_role_checker = Depends(RoleChecker(["admin"]))
role_checker = Depends(RoleChecker(["admin", "user"]))
category_services = CategoryServices()

categories_route = APIRouter()


@categories_route.post("/", response_model=Category, dependencies=[admin_role_checker])
async def create_category(
    category_data: CategoryCreateModel,
    token_data: Annotated[dict, Depends(access_token_bearer)],
    session: SessionDep,
) -> dict:
    user_id = token_data.get("user_id")
    new_category = await category_services.create_category(
        category_data, user_id, session
    )
    return new_category


@categories_route.get("/", response_model=list[Category], dependencies=[role_checker])
async def get_all_categories(
    session: SessionDep, _: Annotated[dict, Depends(access_token_bearer)]
):
    categories = await category_services.get_categories(session)
    return categories


@categories_route.get(
    "/{category_id}", response_model=Category, dependencies=[role_checker]
)
async def get_category_item(
    category_id: str,
    session: SessionDep,
    _: Annotated[dict, Depends(access_token_bearer)],
):
    category = await category_services.category_item(category_id, session)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


@categories_route.put(
    "/{category_id}", response_model=Category, dependencies=[admin_role_checker]
)
async def update_category(
    category_id: str,
    category_data: CategoryCreateModel,
    _: Annotated[dict, Depends(access_token_bearer)],
    session: SessionDep,
):
    updated_category = await category_services.update_category(
        category_id, category_data, session
    )

    if updated_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    else:
        return updated_category


@categories_route.delete(
    "/category-delete/{category_id}",
    response_model=Category,
    dependencies=[admin_role_checker],
)
async def delete_category(
    category_id: str,
    session: SessionDep,
    _: Annotated[dict, Depends(access_token_bearer)],
):
    category_to_delete = await category_services.delete_category(category_id, session)
    if category_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return JSONResponse(
        content={
            "message": f"Category with the name {category_to_delete.name} is deleted"
        },
        status_code=status.HTTP_200_OK,
    )
