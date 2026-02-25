"""
Endpoints for announcements in the High School Management System API
"""

from fastapi import APIRouter
from typing import Optional

from ..database import announcements_collection

router = APIRouter(
    prefix="/announcement",
    tags=["announcement"]
)


@router.get("")
def get_announcement() -> Optional[dict]:
    """
    Get the current active announcement, if any.
    Returns the announcement message and optional end_date.
    """
    announcement = announcements_collection.find_one({"active": True})
    if not announcement:
        return None
    return {"message": announcement["message"], "end_date": announcement.get("end_date")}
