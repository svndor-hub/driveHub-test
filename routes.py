import os
from typing import List
from dotenv import load_dotenv
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

from sqlalchemy.orm import Session
from db import get_session, engine, Base
from schemas import VehicleCreate, TaskCreate, DriverCreate, DriverLogin, AdminCreate, VehicleRead, Fuel, Fueling, MaintenanceCreate, MaintenanceReturn
from crud import driver_create, vehicle_create, task_create
from models import Driver, Task, Admin, Vehicle, VehicleFueling, FuelingPerson, VehicleMaintenance


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


@router.get("/vehicles", response_model=List[VehicleRead])
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


@router.put("/tasks/assign", status_code=status.HTTP_201_CREATED, response_model=TaskCreate)
def assign_task(driver: UUID, task: UUID, session: Session = Depends(get_session), user=Depends(manager)):
    drv = session.query(Driver).filter_by(id=driver).first()
    tsk = session.query(Task).filter_by(id=task).first()

    tsk.driver = drv
    drv.tasks.append(tsk)

    session.commit()

    return tsk


@router.put("/vehicles/assign", status_code=status.HTTP_201_CREATED, response_model=VehicleCreate)
def assign_vehicle(driver: UUID, vehicle: UUID, session: Session = Depends(get_session), user=Depends(manager)):
    drv = session.query(Driver).filter_by(id=driver).first()
    vhcl = session.query(Vehicle).filter_by(id=vehicle).first()

    vhcl.driver = drv
    drv.vehicle = vhcl

    session.commit()

    return vhcl


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
def get_all_tasks(driver_in: UUID, session: Session = Depends(get_session)):
    return session.query(Task).join(Driver).filter(Task.driver_id == driver_in).all()


@router.put("/tasks/update", status_code=status.HTTP_200_OK, response_model=TaskCreate)
def update_task_status(driver_in: UUID, task: UUID, status: str, session: Session = Depends(get_session)):
    if status != 'complete' and status != 'active':
        raise HTTPException(status_code=400, detail='Status should be "active" or "complete"')

    task = session.query(Task).join(Driver).filter(Task.driver_id == driver_in, Task.id == task).first()
    task.status = status
    session.commit()

    return task


@router.get("/tasks/complete", status_code=status.HTTP_200_OK, response_model=List[TaskCreate])
def get_completed_tasks(driver_in: UUID, session: Session = Depends(get_session)):
    return session.query(Task).join(Driver).filter(Task.driver_id == driver_in).filter_by(status="complete")


@router.get("/info", status_code=status.HTTP_200_OK, response_model=DriverCreate)
def get_driver_info(driver_in: UUID, session: Session = Depends(get_session)):
    return session.query(Driver).filter_by(id=driver_in).first()


@router.post("/fuel", status_code=status.HTTP_200_OK, response_model=Fueling)
def fuel_vehicle(data: Fuel, session: Session = Depends(get_session)):
    vehicle = session.query(Vehicle).filter_by(license_plate=data.vehicle_plate).first()
    fueling_person = session.query(FuelingPerson).filter_by(name=data.fueling_person_name).first()
    fueling = VehicleFueling(
        vehicle=vehicle,
        datetime=data.datetime,
        fuelamount=data.fuelamount,
        cost=data.cost,
        gas_station=data.gas_station,
        fueling_person=fueling_person
    )

    session.add(fueling)
    session.commit()
    session.refresh(fueling)

    fueling_person.fuelings.append(fueling)
    vehicle.fueling = fueling
    session.commit()

    return fueling


@router.post("/maintenance", status_code=status.HTTP_200_OK, response_model=MaintenanceReturn)
def maintenance(data: MaintenanceCreate, session: Session = Depends(get_session)):
    vehicle = session.query(Vehicle).filter_by(license_plate=data.vehicle_plate).first()
    report = VehicleMaintenance(
        vehicle=vehicle,
        service_type=data.service_type,
        date=data.date,
        cost=data.cost
    )

    session.add(report)
    session.commit()
    session.refresh(report)

    vehicle.maintenance.append(report)
    session.commit()

    return report


@router.get("/")
async def root():
    return {"message": "Hello World"}