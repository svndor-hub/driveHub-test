from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List


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
    tasks: List[TaskCreate]


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


class DriverId(BaseModel):
    id: UUID
