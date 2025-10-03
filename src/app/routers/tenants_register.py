from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.tenants_schemas import TenantResponse
from app.models.tenants_models import Tenant 
import shutil, os
from app.db.session import get_db

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=TenantResponse)
def create_tenant(
    first_name: str = Form(...),
    last_name: str = Form(...),
    mobile: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    profession: str = Form(...),
    gender: str = Form(...),
    pan: str = Form(...),
    aadhar: str = Form(...),
    room_number: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    panPic: UploadFile = File(None),
    aadharPic: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    pan_pic_path, aadhar_pic_path = None, None

    if panPic:
        pan_pic_path = os.path.join(UPLOAD_DIR, panPic.filename)
        with open(pan_pic_path, "wb") as buffer:
            shutil.copyfileobj(panPic.file, buffer)

    if aadharPic:
        aadhar_pic_path = os.path.join(UPLOAD_DIR, aadharPic.filename)
        with open(aadhar_pic_path, "wb") as buffer:
            shutil.copyfileobj(aadharPic.file, buffer)

    tenant = Tenant(
        first_name=first_name,
        last_name=last_name,
        mobile=mobile,
        email=email,
        address=address,
        profession=profession,
        gender=gender,
        pan=pan,
        aadhar=aadhar,
        room_number=room_number,
        username=username,
        password=password,
        pan_pic=pan_pic_path,
        aadhar_pic=aadhar_pic_path,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

@router.get("/", response_model=list[TenantResponse])
def get_tenants(db: Session = Depends(get_db)):
    return db.query(Tenant).all()

@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: int, db: Session = Depends(get_db)):
    return db.query(Tenant).filter(Tenant.id == tenant_id).first()
