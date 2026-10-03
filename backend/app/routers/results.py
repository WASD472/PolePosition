from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/results",
    tags=["results"]
)




@router.get("/", response_model=list[schemas.ResultResponse])
def get_results(session_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Result)
    if session_id:
        query = query.filter(models.Result.session_id == session_id)
    return query.all()


@router.get("/{result_id}", response_model=schemas.ResultResponse)
def get_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Result).filter(models.Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.post("/", response_model=schemas.ResultResponse)
def create_result(result: schemas.ResultBase, db: Session = Depends(get_db)):
    new = models.Result(**result.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.delete("/{result_id}")
def delete_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Result).filter(models.Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    db.delete(result)
    db.commit()
    return {"message": f"Result {result_id} deleted"}