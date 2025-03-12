from typing import Optional
import uuid
from datetime import datetime, timezone, timedelta
from sqlmodel import SQLModel, Field, Column, Relationship, String


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(default=None, index=True)
    username: str = Field(default=None, index=True)
    last_name: str = Field(default=None)
    first_name: str = Field(default=None)
    company: str | None = Field(default=None)
    hashed_password: str = Field(default=None, exclude=True)
    role: str = Field(sa_column=Column(String(255), server_default="user", nullable=False))
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    results: list["Result"] = Relationship(back_populates="users")
    purchase: Optional["Purchase"] = Relationship(back_populates="users")


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(default=None, nullable=False, unique=True)

    products: list["Product"] = Relationship(back_populates="category")

#
class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(default=None, index=True)
    category_id: uuid.UUID = Field(default=None, foreign_key="categories.id")
    price: float = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    category: Category | None = Relationship(back_populates="products")
    results: list["Result"] = Relationship(back_populates="products")
    purchase: Optional["Purchase"] = Relationship(back_populates="products")


class Result(SQLModel, table=True):
    __tablename__ = "results"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    product_id: uuid.UUID = Field(default=None, foreign_key="products.id")
    user_id: uuid.UUID = Field(default=None, foreign_key="users.id")
    result: float = Field(default=None)
    unit: str = Field(default=None)
    method: str = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    users: User | None = Relationship(back_populates="results")
    products: Product | None = Relationship(back_populates="results")


class Purchase(SQLModel, table=True):
    __tablename__ = "purchase"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(default=None, foreign_key="users.id")
    product_id: uuid.UUID = Field(default=None, foreign_key="products.id")
    quantity: int = Field(default=None)
    amount: float = Field(default=None)
    vat: float = Field(default=None)
    total: float = Field(default=None)
    created_at: datetime = Field(default_factory= lambda : datetime.now(timezone.utc))

    users: User | None = Relationship(back_populates="purchase")
    products: list["Product"] = Relationship(back_populates="purchase")