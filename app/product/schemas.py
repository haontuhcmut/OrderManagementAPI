from pydantic import BaseModel
import uuid

class ProductCreateModel(BaseModel):
    name: str
    category_id: uuid.UUID
    price: float