from pydantic import BaseModel

class ProductCreateModel(BaseModel):
    name: str
    category_id: str
    price: float