from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime, date


class AdminCreate(BaseModel):
    login: str
    password: str


class UserRead(BaseModel):
    id: UUID
    login: str

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    id: UUID
    description: str
    status: str
    route: str


class DriverCreate(BaseModel):
    id: UUID
    login: str
    password: str
    name: str
    surname: str
    middle_name: Optional[str] = None
    address: str
    phone_number: str
    license_code: str
    email: Optional[str] = None


class VehicleCreate(BaseModel):
    id: UUID
    license_plate: str
    make: str
    model: str
    type: str
    year: int


class VehicleRead(BaseModel):
    id: UUID
    license_plate: str
    make: str
    model: str
    type: str
    year: int
    driver: Optional[DriverCreate] = None


class DriverLogin(BaseModel):
    login: str
    password: str


class Fuel(BaseModel):
    vehicle_plate: str
    datetime: datetime
    fuelamount: float
    cost: float
    gas_station: str
    fueling_person_name: str


class FuelingPersonCreate(BaseModel):
    name: str


class Fueling(BaseModel):
    vehicle: VehicleCreate
    datetime: datetime
    fuelamount: float
    cost: float
    gas_station: str
    fueling_person: FuelingPersonCreate


class MaintenanceCreate(BaseModel):
    vehicle_plate: str
    service_type: str
    date: date
    cost: float


class MaintenanceReturn(BaseModel):
    vehicle: VehicleCreate
    service_type: str
    date: date
    cost: float
