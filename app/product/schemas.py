from pydantic import BaseModel, Field
import uuid
from datetime import date

class ProductCreateModel(BaseModel):
    name: str = Field(default=None, max_length=64, min_length=1)
    category_id: uuid.UUID
    price: float = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=1024)
    created_at: date

