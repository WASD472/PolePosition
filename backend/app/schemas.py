from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class CircuitBase(BaseModel):
    name: str
    locality: str
    country: str

class CircuitResponse(CircuitBase):
    id: int


class GrandPrixBase(BaseModel):
    season: int
    round: int
    name: str
    circuit_id: int
    date: date
    time: time

class GrandPrixResponse(GrandPrixBase):
    id: int


class RaceSessionBase(BaseModel):
    grand_prix_id: int
    type: str
    name: str
    date: date
    time: time


class RaceSessionResponse(RaceSessionBase):
    id: int


class DriverBase(BaseModel):
    first_name: str
    last_name: str
    nationality: str
    number: str
    code: str
    wins: int = 0
    podiums: int = 0

class DriverResponse(DriverBase):
    id: int


class ConstructorBase(BaseModel):
    name: str
    short_name: str
    country: str

class ConstructorResponse(ConstructorBase):
    id: int


class ResultBase(BaseModel):
    session_id: int
    driver_id: int
    constructor_id: int
    position: str
    grid: Optional[int] = None
    laps: Optional[int] = None
    points: float
    time: Optional[str] = None
    status: str
    fastest_lap: bool

class ResultResponse(ResultBase):
    id: int


class DriverStandingBase(BaseModel):
    season: int
    round: int
    position: str
    driver_id: int
    points: float


class DriverStandingResponse(DriverStandingBase):
    id: int


class ConstructorStandingBase(BaseModel):
    season: int
    round: int
    position: str
    constructor_id: int
    points: float

class ConstructorStandingResponse(ConstructorStandingBase):
    id: int


class QualifyingResultBase(BaseModel):
    session_id: int
    driver_id: int
    constructor_id: int
    position: str
    q1: Optional[str] = None
    q2: Optional[str] = None
    q3: Optional[str] = None

class QualifyingResultResponse(QualifyingResultBase):
    id: int