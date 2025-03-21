from pydantic import BaseModel, Field

class CategoryCreateModel(BaseModel):
    name: str = Field(max_length=64, min_length=1)
