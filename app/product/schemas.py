from pydantic import BaseModel, Field
import uuid
from datetime import date

class ProductCreateModel(BaseModel):
    name: str = Field(max_length=32)
    category_id: uuid.UUID
    price: float = Field(default=0, ge=0)
    created_at: date

