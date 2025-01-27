from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class Blog_schema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[datetime] = None



