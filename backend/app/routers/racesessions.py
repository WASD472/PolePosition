from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/racesessions",
    tags=["racesessions"]
)




#Все сессии одного г.п
@router.get("/", response_model=list[schemas.RaceSessionResponse])
def get_sessions(grand_prix_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.RaceSession)
    if grand_prix_id:
        query = query.filter(models.RaceSession.grand_prix_id == grand_prix_id)
    return query.all()

#Возвращает 1 сессию г.п
@router.get("/{racesession_id}", response_model=schemas.RaceSessionResponse)
def get_racesession(racesession_id: int, db: Session = Depends(get_db)):
    racesession = db.query(models.RaceSession).filter(models.RaceSession.id == racesession_id).first()
    if not racesession:
        raise HTTPException(status_code=404, detail="RaceSession not found")
    return racesession


@router.post("/", response_model=schemas.RaceSessionResponse)
def create_racesession(racesession: schemas.RaceSessionBase, db: Session = Depends(get_db)):
    new = models.RaceSession(**racesession.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.delete("/{racesession_id}")
def delete_racesession(racesession_id: int, db: Session = Depends(get_db)):
    racesession = db.query(models.RaceSession).filter(models.RaceSession.id == racesession_id).first()
    if not racesession:
        raise HTTPException(status_code=404, detail="RaceSession not found")
    db.delete(racesession)
    db.commit()
    return {"message": f"RaceSession {racesession_id} deleted"}

