from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Circuit(Base):
    __tablename__ = "circuits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    locality = Column(String)
    country = Column(String)
    length = Column(Float, nullable=True)          # длина круга в км
    laps = Column(Integer, nullable=True)          # число кругов
    first_gp_year = Column(Integer, nullable=True) # год первого ГП
    description = Column(String, nullable=True)    # короткое описание

class GrandPrix(Base):
    __tablename__ = "grandprix"

    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer)
    round = Column(Integer)
    name = Column(String)
    circuit_id = Column(Integer, ForeignKey("circuits.id"))
    date = Column(Date)
    time = Column(Time)


class RaceSession(Base):
    __tablename__ = "racesessions"

    id = Column(Integer, primary_key=True)
    grand_prix_id = Column(Integer, ForeignKey("grandprix.id"))
    type = Column(String)
    name = Column(String)
    date = Column(Date)
    time = Column(Time)


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    nationality = Column(String)
    number = Column(String)
    code = Column(String)


class Constructor(Base):
    __tablename__ = "constructors"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    short_name = Column(String)
    country = Column(String)


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("racesessions.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    constructor_id = Column(Integer, ForeignKey("constructors.id"))
    position = Column(String)
    grid = Column(Integer)
    laps = Column(Integer)
    points = Column(Float)
    time = Column(String)
    status = Column(String)
    fastest_lap = Column(Boolean)


class DriverStanding(Base):
    __tablename__ = "driverstandings"

    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer)
    round = Column(Integer)
    position = Column(String)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    points = Column(Float)


class ConstructorStanding(Base):
    __tablename__ = "constructorstandings"

    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer)
    round = Column(Integer)
    position = Column(String)
    constructor_id = Column(Integer, ForeignKey("constructors.id"))
    points = Column(Float)



class QualifyingResult(Base):
    __tablename__ = "qualifyingresults"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("racesessions.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    constructor_id = Column(Integer, ForeignKey("constructors.id"))
    position = Column(String)
    q1 = Column(String, nullable=True)
    q2 = Column(String, nullable=True)
    q3 = Column(String, nullable=True)
