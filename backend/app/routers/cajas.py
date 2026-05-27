from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models import Caja, Gasto, Ingreso
from app.schemas.schemas import CajaCreate, CajaResponse, CajaUpdate

router = APIRouter(prefix="/cajas", tags=["Cajas"])

@router.post("/", response_model=CajaResponse, status_code=status.HTTP_201_CREATED)
def create_caja(caja_in: CajaCreate, db: Session = Depends(get_db)):
    # Validar que el nombre no esté duplicado
    db_caja = db.query(Caja).filter(Caja.nombre == caja_in.nombre).first()
    if db_caja:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una caja con el nombre '{caja_in.nombre}'."
        )
    
    new_caja = Caja(
        nombre=caja_in.nombre,
        tipo=caja_in.tipo,
        saldo_inicial=caja_in.saldo_inicial,
        saldo_actual=caja_in.saldo_inicial,  # Al crear, saldo actual = saldo inicial
        activo=caja_in.activo
    )
    db.add(new_caja)
    db.commit()
    db.refresh(new_caja)
    return new_caja

@router.get("/", response_model=List[CajaResponse])
def read_cajas(db: Session = Depends(get_db)):
    # Retorna solo las cajas activas por defecto
    return db.query(Caja).filter(Caja.activo == True).order_name().all() if hasattr(db.query(Caja), 'order_name') else db.query(Caja).filter(Caja.activo == True).order_by(Caja.nombre).all()

@router.get("/all", response_model=List[CajaResponse])
def read_all_cajas(db: Session = Depends(get_db)):
    # Retorna todas las cajas (activas e inactivas)
    return db.query(Caja).order_by(Caja.nombre).all()

@router.put("/{caja_id}", response_model=CajaResponse)
def update_caja(caja_id: str, caja_in: CajaUpdate, db: Session = Depends(get_db)):
    caja = db.query(Caja).filter(Caja.id == caja_id).first()
    if not caja:
        raise HTTPException(status_code=404, detail="Caja no encontrada.")
    
    if caja_in.nombre is not None:
        # Validar duplicados si cambia de nombre
        if caja_in.nombre != caja.nombre:
            duplicado = db.query(Caja).filter(Caja.nombre == caja_in.nombre).first()
            if duplicado:
                raise HTTPException(status_code=400, detail="Ya existe otra caja con ese nombre.")
            caja.nombre = caja_in.nombre
            
    if caja_in.tipo is not None:
        caja.tipo = caja_in.tipo
        
    if caja_in.activo is not None:
        caja.activo = caja_in.activo
        
    db.commit()
    db.refresh(caja)
    return caja

@router.delete("/{caja_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_caja(caja_id: str, db: Session = Depends(get_db)):
    caja = db.query(Caja).filter(Caja.id == caja_id).first()
    if not caja:
        raise HTTPException(status_code=404, detail="Caja no encontrada.")
    
    # Verificar si tiene transacciones vinculadas
    has_gastos = db.query(Gasto).filter(Gasto.caja_id == caja_id).first() is not None
    has_ingresos = db.query(Ingreso).filter(Ingreso.caja_id == caja_id).first() is not None
    
    if has_gastos or has_ingresos:
        # En vez de borrar físicamente, pasamos a inactiva
        caja.activo = False
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="La caja posee transacciones históricas vinculadas. Se ha desactivado lógicamente para preservar los reportes."
        )
        
    db.delete(caja)
    db.commit()
