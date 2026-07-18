from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Admin

from backend.schemas import (
    IntelligenceQueryRequest,
    IntelligenceQueryResponse
)

from backend.intelligence.router import (
    route_intelligence_query
)

from utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/ai/intelligence",
    tags=["AI Intelligence Engine"]
)


@router.post(
    "/query",
    response_model=IntelligenceQueryResponse
)
def intelligence_query(
    request: IntelligenceQueryRequest,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return route_intelligence_query(
        question=request.question,
        db=db
    )