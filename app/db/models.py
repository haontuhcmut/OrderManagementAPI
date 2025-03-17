import uuid
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column, Relationship, String, Numeric
from typing import Optional

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(default=None, index=True, unique=True)
    username: str = Field(default=None, index=True, unique=True)
    last_name: str = Field(default=None)
    first_name: str = Field(default=None)
    company: str | None = Field(default=None)
    hashed_password: str = Field(default=None, exclude=True)
    role: str = Field(
        sa_column=Column(String(255), server_default="user", nullable=False)
    )
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship
    categories: list["Category"] = Relationship(back_populates="user")
    products: list["Product"] = Relationship(back_populates="user")
    carts: list["Cart"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(..., nullable=False, unique=True)
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    user: User | None = Relationship(back_populates="categories")
    products: list["Product"] = Relationship(back_populates="category")


class Cart(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    user: User | None = Relationship(back_populates="carts")
    cart_items: list["CartItem"] = Relationship(back_populates="cart")

class CartItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    quantity: int = Field(default=0, nullable=False)
    price_at_purchase: Decimal = Field(default=0.00, sa_column_kwargs={"type_": Numeric(10, 2)})
    product_id: uuid.UUID | None = Field(default=None, foreign_key="product.id")
    cart_id: uuid.UUID | None = Field(default=None, foreign_key="cart.id")

    product: Optional["Product"] = Relationship(back_populates="cart_items")
    cart: Optional["Cart"] = Relationship(back_populates="cart_items")

class Product(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    SKU: str = Field(default=None, unique=True, nullable=False)
    description: str = Field(default=None, max_length=1024)
    price: Decimal = Field(default=0.00, sa_column_kwargs={"type_": Numeric(10, 2)})
    stock: int = Field(default=None)
    category_id: uuid.UUID | None = Field(default=None, foreign_key="category.id")
    created_at: date
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    category: Category | None = Relationship(back_populates="products")
    user: User | None = Relationship(back_populates="products")
    cart_items: list[CartItem] = Relationship(back_populates="product")


