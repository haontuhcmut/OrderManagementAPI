from pydantic import BaseModel
import uuid
from datetime import date

class ProductCreateModel(BaseModel):
    user_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    amount: float
    vat: float
    total: float
    created_at: date
