from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    full_name: str
    disabled: Optional[bool] = False