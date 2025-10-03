from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import helpdesk
from app.schemas import helpdesk
from app.db.session import get_db

router = APIRouter(
    prefix="/escalations",
    tags=["Escalations"]
)


@router.post("/", response_model=helpdesk.EscalationOut)
def create_escalation(escalation: helpdesk.EscalationCreate, db: Session = Depends(get_db)):
    new_escalation = helpdesk.Escalation(
        title=escalation.title,
        description=escalation.description,
        priority=escalation.priority,
        status=escalation.status
    )
    db.add(new_escalation)
    db.commit()
    db.refresh(new_escalation)
    return new_escalation

@router.get("/", response_model=list[helpdesk.EscalationOut])
def get_escalations(db: Session = Depends(get_db)):
    return db.query(helpdesk.Escalation).all()

@router.get("/{escalation_id}", response_model=helpdesk.EscalationOut)
def get_escalation(escalation_id: int, db: Session = Depends(get_db)):
    return db.query(helpdesk.Escalation).filter(helpdesk.Escalation.id == escalation_id).first()

@router.put("/{escalation_id}", response_model=helpdesk.EscalationOut)
def update_escalation(escalation_id: int, escalation: helpdesk.EscalationCreate, db: Session = Depends(get_db)):
    db_escalation = db.query(helpdesk.Escalation).filter(helpdesk.Escalation.id == escalation_id).first()
    db_escalation.title = escalation.title
    db_escalation.description = escalation.description
    db_escalation.priority = escalation.priority
    db_escalation.status = escalation.status
    db.commit()
    db.refresh(db_escalation)
    return db_escalation
