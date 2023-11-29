import uuid
import enum
from db import Base, engine
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)


class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    license_plate = Column(String(8), nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    type = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    driver_id = Column(UUID, ForeignKey('driver.id'))
    driver = relationship('Driver', back_populates='vehicle')


class Driver(Base):
    __tablename__ = 'driver'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    middle_name = Column(String)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    license_code = Column(String, nullable=False)
    email = Column(String)
    vehicle = relationship('Vehicle', back_populates='driver')
    tasks = relationship('Task', back_populates='driver')


class Status(str, enum.Enum):
    active = "active"
    complete = "complete"


StatusType = ENUM(
    Status,
    name="status",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class Task(Base):
    __tablename__ = 'task'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    description = Column(String, nullable=False)
    status = Column(StatusType, nullable=False)
    driver_id = Column(UUID, ForeignKey('driver.id'))
    driver = relationship('Driver', back_populates='tasks')


Base.metadata.create_all(engine)
