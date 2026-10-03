from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/grandprix",
    tags=["grandprix"]
)

@router.get("/", response_model=list[schemas.GrandPrixResponse])
def get_grandprix(db: Session = Depends(get_db)):
    return db.query(models.GrandPrix).all()


@router.get("/{grandprix_id}", response_model=schemas.GrandPrixResponse)
def get_grandprixs(grandprix_id: int, db: Session = Depends(get_db)):
    grandprix = db.query(models.GrandPrix).filter(models.GrandPrix.id == grandprix_id).first()
    if not grandprix:
        raise HTTPException(status_code=404, detail="Grandprix not found")
    return grandprix


@router.post("/", response_model=schemas.GrandPrixResponse)
def create_grandprix(grandprix: schemas.GrandPrixBase, db: Session = Depends(get_db)):
    new = models.GrandPrix(**grandprix.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.delete("/{grandprix_id}")
def delete_grandprix(grandprix_id: int, db: Session = Depends(get_db)):
    grandprix = db.query(models.GrandPrix).filter(models.GrandPrix.id == grandprix_id).first()
    if not grandprix:
        raise HTTPException(status_code=404, detail="Grandprix not found")
    db.delete(grandprix)
    db.commit()
    return {"message": f"Grandprix {grandprix_id} deleted"}