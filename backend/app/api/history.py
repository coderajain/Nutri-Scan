"""Paginated scan history and inspection repository (HIS-001 through HIS-005, NFR-PERF-006)."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.scan import Scan, ComplianceStatus
from app.schemas.scan import PaginatedScanHistoryResponse, ScanSummaryResponse
from app.api.deps import get_current_user
import math

router = APIRouter(prefix="/history", tags=["Scan History"])


@router.get("", response_model=PaginatedScanHistoryResponse)
def get_scan_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    product_name: Optional[str] = Query(None, description="Filter by product or brand name"),
    compliance_status: Optional[ComplianceStatus] = Query(None, description="Filter by compliance outcome"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves paginated scan history.
    Standard users see only their scans; Administrators see system-wide scans (DASH-005).
    """
    query = db.query(Scan)

    if current_user.role != UserRole.ADMINISTRATOR:
        query = query.filter(Scan.user_id == current_user.id)

    if product_name:
        search = f"%{product_name}%"
        query = query.filter(or_(Scan.product_name.ilike(search), Scan.brand_name.ilike(search)))

    if compliance_status:
        query = query.filter(Scan.compliance_status == compliance_status)

    total_count = query.count()
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1

    items = (
        query.order_by(Scan.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "items": items,
        "total": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }
