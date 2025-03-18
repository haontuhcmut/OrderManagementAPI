from pydantic import BaseModel, Field
import uuid
from datetime import date
from decimal import Decimal

class ProductCreateModel(BaseModel):
    sku: str = Field(default=None, max_length=64, min_length=1)
    description: str | None = Field(default=None, max_length=1024)
    price: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    stock: int
    category_id: uuid.UUID
    created_at: date



