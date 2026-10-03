from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/drivers",
    tags=["drivers"]
)

@router.get("/", response_model=list[schemas.DriverResponse])
def get_drivers(db: Session = Depends(get_db)):
    #Подсчет побед: топ-1
    wins_position = db.query(models.Result.driver_id, func.count(models.Result.id).label("wins")).join(
    models.RaceSession,
    models.Result.session_id == models.RaceSession.id).filter(models.RaceSession.type == "race", #Надо знать гонка или квала
                                                              models.Result.position == "1").group_by(
    models.Result.driver_id).subquery()


    #Подсчитываем подиумы
    podiums_position = db.query(models.Result.driver_id, func.count(models.Result.id).label("podiums")).join(
        models.RaceSession,
        models.Result.session_id == models.RaceSession.id).filter(models.RaceSession.type == "race",
                                                                  models.Result.position.in_(["1", "2", "3"])).group_by(
        models.Result.driver_id).subquery()


    drivers = db.query(models.Driver, func.coalesce(wins_position.c.wins, 0).label("wins"), #coalesce = SQL функция если значение NULL, то 0.
                                      func.coalesce(podiums_position.c.podiums, 0).label("podiums"),).outerjoin(
                                          wins_position, models.Driver.id == wins_position.c.driver_id).outerjoin(
                                              podiums_position, models.Driver.id == podiums_position.c.driver_id).all()


    #Преобразуем результат в список
    return [{
        "id": d.id,
        "first_name": d.first_name,
        "last_name": d.last_name,
        "nationality": d.nationality,
        "number": d.number,
        "code": d.code,
        "wins": wins,
        "podiums":podiums,
    }
    for d, wins, podiums in drivers]


@router.get("/{driver_id}", response_model=schemas.DriverResponse)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.post("/", response_model=schemas.DriverResponse)
def create_driver(driver: schemas.DriverBase, db: Session = Depends(get_db)):
    new = models.Driver(**driver.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.delete("/{driver_id}")
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    db.delete(driver)
    db.commit()
    return {"message": f"Driver {driver_id} deleted"}