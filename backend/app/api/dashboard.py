"""Dashboard and inspection analytics endpoints (DASH-001, DASH-002, DASH-003, DASH-005)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.scan import Scan, ComplianceStatus, NutritionStatus
from app.schemas.dashboard import DashboardStats, ComplianceBreakdown, NutritionBreakdown
from app.schemas.scan import ScanSummaryResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Computes aggregated dashboard metrics for authorized scans."""
    query = db.query(Scan)
    if current_user.role != UserRole.ADMINISTRATOR:
        query = query.filter(Scan.user_id == current_user.id)

    total_scans = query.count()

    # Averages
    avg_comp = query.filter(Scan.compliance_score.isnot(None)).with_entities(func.avg(Scan.compliance_score)).scalar()
    avg_nutri = query.filter(Scan.nutrition_score.isnot(None)).with_entities(func.avg(Scan.nutrition_score)).scalar()

    # Compliance breakdown
    comp_breakdown = ComplianceBreakdown(
        compliant=query.filter(Scan.compliance_status == ComplianceStatus.COMPLIANT).count(),
        non_compliant=query.filter(Scan.compliance_status == ComplianceStatus.NON_COMPLIANT).count(),
        partial=query.filter(Scan.compliance_status == ComplianceStatus.PARTIAL).count(),
        manual_review_required=query.filter(Scan.has_font_size_flags == True).count(),
    )

    # Nutrition breakdown
    nutri_breakdown = NutritionBreakdown(
        excellent=query.filter(Scan.nutrition_status == NutritionStatus.EXCELLENT).count(),
        good=query.filter(Scan.nutrition_status == NutritionStatus.GOOD).count(),
        moderate=query.filter(Scan.nutrition_status == NutritionStatus.MODERATE).count(),
        high_risk=query.filter(Scan.nutrition_status == NutritionStatus.HIGH_RISK).count(),
        insufficient_data=query.filter(Scan.is_data_insufficient == True).count(),
    )

    # Recent scans (limit 5)
    recent = query.order_by(Scan.created_at.desc()).limit(5).all()

    return {
        "total_scans": total_scans,
        "average_compliance_score": round(float(avg_comp), 1) if avg_comp is not None else None,
        "average_nutrition_score": round(float(avg_nutri), 1) if avg_nutri is not None else None,
        "compliance_breakdown": comp_breakdown,
        "nutrition_breakdown": nutri_breakdown,
        "recent_scans": recent,
    }
