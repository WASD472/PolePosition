from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/circuits",
    tags=["circuits"]
)

@router.get("/", response_model=list[schemas.CircuitResponse])
def get_circuits(db: Session = Depends(get_db)):
    return db.query(models.Circuit).all()

@router.get("/{circuit_id}", response_model=schemas.CircuitResponse)
def get_circuit(circuit_id: int, db: Session = Depends(get_db)):
    circuit = db.query(models.Circuit).filter(models.Circuit.id == circuit_id).first()
    if not circuit:
        raise HTTPException(status_code=404, detail="Circut not found")
    return circuit

@router.post("/", response_model=schemas.CircuitResponse)
def create_circuit(circuit: schemas.CircuitBase, db: Session = Depends(get_db)):
    new = models.Circuit(**circuit.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.delete("/{circuit_id}")
def delete_circuit(circuit_id: int, db: Session = Depends(get_db)):
    circuit = db.query(models.Circuit).filter(models.Circuit.id == circuit_id).first()
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    db.delete(circuit)
    db.commit()
    return {"message": f"Circuit {circuit_id} deleted"}