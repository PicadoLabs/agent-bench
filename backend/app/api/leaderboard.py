from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.storage.database import get_db
from app.storage.repository import RunRepository

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("")
def get_leaderboard(db: Session = Depends(get_db)):
    """Fetch aggregated leaderboard rankings by Agent and Model."""
    repo = RunRepository(db)
    return repo.get_leaderboard()
