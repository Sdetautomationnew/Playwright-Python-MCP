from pydantic import BaseModel
from typing import List, Optional
from .product import Product


class Order(BaseModel):
    id: Optional[str] = None
    user_id: str
    products: List[Product]
    total_price: float
    status: str = "pending"