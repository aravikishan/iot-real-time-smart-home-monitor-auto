from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import uvicorn

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./smarthome.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String)
    last_active = Column(DateTime)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer)
    message = Column(String)
    timestamp = Column(DateTime)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed data
def seed_data(db: Session):
    if not db.query(User).first():
        user = User(name="John Doe", email="john@example.com", password_hash="hashedpassword")
        db.add(user)
        db.commit()
    if not db.query(Device).first():
        device = Device(name="Smart Light", status="Online", last_active=datetime.now())
        db.add(device)
        db.commit()
    if not db.query(Notification).first():
        notification = Notification(device_id=1, message="Device is online", timestamp=datetime.now())
        db.add(notification)
        db.commit()

# FastAPI app
app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "devices": devices})

@app.get("/devices", response_class=HTMLResponse)
async def devices_page(request: Request, db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return templates.TemplateResponse("devices.html", {"request": request, "devices": devices})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    user = db.query(User).first()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request, db: Session = Depends(get_db)):
    notifications = db.query(Notification).all()
    return templates.TemplateResponse("notifications.html", {"request": request, "notifications": notifications})

# API Endpoints
@app.get("/api/devices")
async def get_devices(db: Session = Depends(get_db)):
    return db.query(Device).all()

@app.post("/api/devices")
async def add_device(name: str, db: Session = Depends(get_db)):
    device = Device(name=name, status="Offline", last_active=datetime.now())
    db.add(device)
    db.commit()
    return {"message": "Device added successfully"}

@app.get("/api/user/profile")
async def get_user_profile(db: Session = Depends(get_db)):
    user = db.query(User).first()
    return user

@app.post("/api/user/profile")
async def update_user_profile(name: str, email: str, db: Session = Depends(get_db)):
    user = db.query(User).first()
    user.name = name
    user.email = email
    db.commit()
    return {"message": "Profile updated successfully"}

@app.get("/api/notifications")
async def get_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).all()

# Run app
if __name__ == "__main__":
    db = SessionLocal()
    seed_data(db)
    uvicorn.run(app, host="0.0.0.0", port=8000)
