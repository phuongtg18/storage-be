from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Item
from app.schemas import DashboardRead
from app.security import get_current_admin
from app.services.inventory import item_status

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_admin)])

@router.get("", response_model=DashboardRead)
def dashboard(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    counts = {"IN_STOCK": 0, "RUNNING_LOW": 0, "CRITICAL_OUT": 0}
    for item in items:
        counts[item_status(item)] += 1
    return DashboardRead(
        total_items=len(items),
        in_stock=counts["IN_STOCK"],
        running_low=counts["RUNNING_LOW"],
        critical_out=counts["CRITICAL_OUT"],
        total_quantity=sum(item.quantity for item in items),
    )
