"""Common response models used across routes."""

from pydantic import BaseModel
from typing import Optional


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "OK"


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
