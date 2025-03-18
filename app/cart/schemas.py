import uuid
from decimal import Decimal
from pydantic import BaseModel, Field

class CreateCartModel(BaseModel):
    product_id: uuid.UUID
    price_at_purchase: Decimal = Field(default=0, max_digits=12, decimal_places=2)
