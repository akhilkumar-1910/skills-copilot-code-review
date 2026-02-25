"""
Endpoints for announcements in the High School Management System API
"""


from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer

from ..database import announcements_collection

from .auth import check_session

router = APIRouter(
    prefix="/announcement",
    tags=["announcement"]
)


class AnnouncementModel(BaseModel):
    message: str
    start_date: Optional[datetime] = None
    end_date: datetime
    active: bool = True

class AnnouncementOutModel(AnnouncementModel):
    id: str = Field(alias="_id")

def require_auth(username: str = Depends(check_session)):
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return username



# Get all announcements (for management UI)
@router.get("/all", response_model=List[AnnouncementOutModel])
def list_announcements(username: str = Depends(require_auth)):
    docs = list(announcements_collection.find())
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs

# Get current active announcements (for display)
@router.get("")
def get_active_announcements():
    now = datetime.utcnow()
    announcements = list(announcements_collection.find({
        "active": True,
        "$or": [
            {"start_date": None},
            {"start_date": {"$lte": now}}
        ],
        "end_date": {"$gte": now}
    }))
    for a in announcements:
        a["_id"] = str(a["_id"])
    return announcements

# Add new announcement
@router.post("", response_model=AnnouncementOutModel)
def create_announcement(announcement: AnnouncementModel, username: str = Depends(require_auth)):
    if not announcement.end_date:
        raise HTTPException(status_code=400, detail="Expiration date required.")
    doc = announcement.dict()
    result = announcements_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc

# Update announcement
@router.put("/{announcement_id}", response_model=AnnouncementOutModel)
def update_announcement(announcement_id: str, announcement: AnnouncementModel, username: str = Depends(require_auth)):
    if not announcement.end_date:
        raise HTTPException(status_code=400, detail="Expiration date required.")
    result = announcements_collection.find_one_and_update(
        {"_id": announcement_id},
        {"$set": announcement.dict()},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Announcement not found.")
    result["_id"] = str(result["_id"])
    return result

# Delete announcement
@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, username: str = Depends(require_auth)):
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found.")
    return {"success": True}
