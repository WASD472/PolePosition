from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/qualifying",
    tags=["qualifying"]
)




@router.get("/", response_model=list[schemas.QualifyingResultResponse])
def get_qualifying(session_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.QualifyingResult)
    if session_id:
        query = query.filter(models.QualifyingResult.session_id == session_id)
    return query.all()


@router.get("/{qualifyingresult_id}", response_model=schemas.QualifyingResultResponse)
def get_qualifying(qualifyingresult_id: int, db: Session = Depends(get_db)):
    qualifyingresult = db.query(models.QualifyingResult).filter(models.QualifyingResult.id == qualifyingresult_id).first()
    if not qualifyingresult:
        raise HTTPException(status_code=404, detail="Qualifying result not found")
    return qualifyingresult


@router.post("/", response_model=schemas.QualifyingResultResponse)
def create_qualifying(qualifyingresult: schemas.QualifyingResultBase, db: Session = Depends(get_db)):
    new = models.QualifyingResult(**qualifyingresult.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.delete("/{qualifyingresult_id}")
def delete_qualifying(qualifyingresult_id: int, db: Session = Depends(get_db)):
    qualifyingresult = db.query(models.QualifyingResult).filter(models.QualifyingResult.id == qualifyingresult_id).first()
    if not qualifyingresult:
        raise HTTPException(status_code=404, detail="Qualifying result not found")
    db.delete(qualifyingresult)
    db.commit()
    return {"message": f"Qualifying result {qualifyingresult_id} deleted"}