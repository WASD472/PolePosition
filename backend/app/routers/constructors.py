from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas


router = APIRouter(
    prefix="/constructors",
    tags=["constructors"]
)

@router.get("/", response_model=list[schemas.ConstructorResponse])
def get_constructors(db: Session = Depends(get_db)):
    return db.query(models.Constructor).all()

@router.get("/{constructor_id}", response_model=schemas.ConstructorResponse)
def get_constructor(constructor_id: int, db: Session = Depends(get_db)):
    constructor = db.query(models.Constructor).filter(models.Constructor.id == constructor_id).first()
    if not constructor:
        raise HTTPException(status_code=404, detail="Constructor not found")
    return constructor

@router.post("/", response_model=schemas.ConstructorResponse)
def create_constructor(constructor: schemas.ConstructorBase, db: Session = Depends(get_db)):
    new = models.Constructor(**constructor.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.delete("/{constructor_id}")
def delete_constructor(constructor_id: int, db: Session = Depends(get_db)):
    constructor = db.query(models.Constructor).filter(models.Constructor.id == constructor_id).first()
    if not constructor:
        raise HTTPException(status_code=404, detail="Constructor not found")
    db.delete(constructor)
    db.commit()
    return {"message": f"Constructor {constructor_id} deleted"} 