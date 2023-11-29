import os
from typing import List
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

from sqlalchemy.orm import Session
from db import get_session, engine, Base
from schemas import VehicleCreate, TaskCreate, DriverCreate, DriverLogin, DriverId, AdminCreate
from crud import driver_create, vehicle_create, task_create
from models import Driver, Task, Admin, Vehicle


router = APIRouter()
load_dotenv()

SECRET = os.getenv("SECRET")
manager = LoginManager(SECRET, '/login')


@manager.user_loader()
def query_user(login: str):
    with Session(engine) as db:
        return db.query(Admin).filter_by(login=login).first()


# For admin/web

@router.post("/admin/create")
def create_admin(data: AdminCreate, session: Session = Depends(get_session)):
    new_admin = Admin(login=data.login, password=data.password)
    session.add(new_admin)
    session.commit()
    session.refresh(new_admin)


@router.post("/login")
def login_admin(data: OAuth2PasswordRequestForm = Depends()):
    login_adm = data.username
    password = data.password

    user = query_user(login_adm)
    if not user:
        raise InvalidCredentialsException
    elif password != user.password:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data={'sub': login_adm}
    )
    return {'access_token': access_token}


@router.post("/drivers/create", status_code=status.HTTP_201_CREATED, response_model=DriverCreate)
def create_user(driver: DriverCreate, session: Session = Depends(get_session), user=Depends(manager)):
    if session.query(Driver).filter_by(login=driver.login).first():
        raise HTTPException(status_code=400, detail=f"Driver {driver.login} already registered")

    return driver_create(session=session, driver=driver)


@router.get("/vehicles", response_model=List[VehicleCreate])
def get_vehicles(session: Session = Depends(get_session)):
    return session.query(Vehicle).all()


@router.get("/drivers", response_model=List[DriverCreate])
def get_drivers(session: Session = Depends(get_session)):
    return session.query(Driver).all()


@router.post("/vehicles/create", status_code=status.HTTP_201_CREATED, response_model=VehicleCreate)
def create_vehicle(vehicle: VehicleCreate, session: Session = Depends(get_session), user=Depends(manager)):
    return vehicle_create(session=session, vehicle=vehicle)


@router.get("/tasks", response_model=List[TaskCreate])
def get_tasks(session: Session = Depends(get_session)):
    return session.query(Task).all()


@router.post("/tasks/create", status_code=status.HTTP_201_CREATED, response_model=TaskCreate)
def create_task(task: TaskCreate, session: Session = Depends(get_session), user=Depends(manager)):
    return task_create(session=session, task=task)


# For driver app

@router.post("/login/driver", status_code=status.HTTP_200_OK, response_model=DriverCreate)
def login_driver(data: DriverLogin, session: Session = Depends(get_session)):
    login_drv = data.login
    password = data.password

    user = session.query(Driver).filter_by(login=login_drv).first()
    if not user:
        raise InvalidCredentialsException
    elif password != user.password:
        raise InvalidCredentialsException

    return user





@router.get("/tasks/all", status_code=status.HTTP_200_OK, response_model=List[TaskCreate])
def get_all_tasks(driver_in: DriverId, session: Session = Depends(get_session)):
    return session.query(Task).join(Driver).filter(Task.driver_id == driver_in).all()


@router.get("/tasks/complete", status_code=status.HTTP_200_OK, response_model=List[TaskCreate])
def get_completed_tasks(driver_in: DriverId, session: Session = Depends(get_session)):
    return session.query(Task).join(Driver).filter(Task.driver_id == driver_in).filter_by(status="complete")


@router.get("/info", status_code=status.HTTP_200_OK, response_model=DriverCreate)
def get_driver_info(driver_in: DriverId, session: Session = Depends(get_session)):
    return session.query(Driver).filter_by(id=driver_in)


@router.get("/")
async def root():
    return {"message": "Hello World"}
