from sqlalchemy.orm import Session
from schemas import UserRead, VehicleCreate, TaskCreate, DriverCreate
from models import Vehicle, Task, Driver
from typing import Optional


def driver_create(session: Session, driver: DriverCreate):

    # TODO: hash user password
    hashed_pw = driver.password

    db_user = Driver(
        id=driver.id,
        login=driver.login,
        password=hashed_pw,
        name=driver.name,
        surname=driver.surname,
        middle_name=driver.middle_name,
        address=driver.address,
        phone_number=driver.phone_number,
        license_code=driver.license_code,
        email=driver.email,
        tasks=driver.tasks
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


def vehicle_create(session: Session, vehicle: VehicleCreate):
    new_vehicle = Vehicle(
        id=vehicle.id,
        license_plate=vehicle.license_plate,
        make=vehicle.make,
        model=vehicle.model,
        type=vehicle.type,
        year=vehicle.year,
        driver=vehicle.driver_id
    )

    session.add(new_vehicle)
    session.commit()
    session.refresh(new_vehicle)

    return new_vehicle


def task_create(session: Session, task: TaskCreate):
    new_task = Task(description=task.description, status=task.status)

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task
