from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/standings",
    tags=["standings"]
)




@router.get("/drivers/", response_model=list[schemas.DriverStandingResponse])
def get_driverstandings(season: int = None, db: Session = Depends(get_db)):
    query = db.query(models.DriverStanding)
    if season:
        query = query.filter(models.DriverStanding.season == season)
    return query.all()


@router.get("/drivers/{standing_id}", response_model=schemas.DriverStandingResponse)
def get_driverstanding(standing_id: int, db: Session = Depends(get_db)):
    standing = db.query(models.DriverStanding).filter(models.DriverStanding.id == standing_id).first()
    if not standing:
        raise HTTPException(status_code=404, detail="DriverStanding not found")
    return standing


@router.post("/drivers/", response_model=schemas.DriverStandingResponse)
def create_driverstanding(standing: schemas.DriverStandingBase, db: Session = Depends(get_db)):
    new = models.DriverStanding(**standing.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.delete("/drivers/{standing_id}")
def delete_driverstanding(standing_id: int, db: Session = Depends(get_db)):
    standing = db.query(models.DriverStanding).filter(models.DriverStanding.id == standing_id).first()
    if not standing:
        raise HTTPException(status_code=404, detail="DriverStanding not found")
    db.delete(standing)
    db.commit()
    return {"message": f"DriverStanding {standing_id} deleted"}



@router.get("/constructors/", response_model=list[schemas.ConstructorStandingResponse])
def get_consntructorstandings(season: int = None, db: Session = Depends(get_db)):
    query = db.query(models.ConstructorStanding)
    if season:
        query = query.filter(models.ConstructorStanding.season == season)
    return query.all()


@router.get("/constructors/{standing_id}", response_model=schemas.ConstructorStandingResponse)
def get_constructorstanding(standing_id: int, db: Session = Depends(get_db)):
    constructor = db.query(models.ConstructorStanding).filter(models.ConstructorStanding.id == standing_id).first()
    if not constructor:
        raise HTTPException(status_code=404, detail="ConstructorStanding not found")
    return constructor


@router.post("/constructors/", response_model=schemas.ConstructorStandingResponse)
def create_constructorstanding(constructor: schemas.ConstructorStandingBase, db: Session = Depends(get_db)):
    new = models.ConstructorStanding(**constructor.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.delete("/constructors/{standing_id}")
def delete_constructorstanding(standing_id: int, db: Session = Depends(get_db)):
   constructor = db.query(models.ConstructorStanding).filter(models.ConstructorStanding.id == standing_id).first()
   if not constructor:
        raise HTTPException(status_code=404, detail="ConstructorStanding not found")
   db.delete(constructor)
   db.commit()
   return {"message": f"ConstructorStanding {standing_id} deleted"}