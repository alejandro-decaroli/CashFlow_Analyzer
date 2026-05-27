from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.db.session import get_db
from app.db.models import Gasto, Ingreso, Caja, CategoriaGasto, FuenteIngreso, ConciliacionMensual
from app.schemas.schemas import (
    GastoCreate, GastoResponse, IngresoCreate, IngresoResponse,
    CategoriaGastoCreate, CategoriaGastoResponse, FuenteIngresoCreate, FuenteIngresoResponse,
    TransaccionBase
)

router = APIRouter(prefix="/transacciones", tags=["Transacciones"])

# Helper para verificar si un período mensual calendario ya está cerrado
def verificar_periodo_cerrado(fecha: date, db: Session):
    mes = fecha.month
    anio = fecha.year
    conciliacion = db.query(ConciliacionMensual).filter(
        ConciliacionMensual.mes == mes,
        ConciliacionMensual.anio == anio
    ).first()
    if conciliacion and conciliacion.estado == "CERRADO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El período {mes}/{anio} se encuentra cerrado por conciliación mensual. Las transacciones son de sólo lectura."
        )

# --- ENDPOINTS CATEGORIAS DE GASTOS ---
@router.post("/categorias", response_model=CategoriaGastoResponse, status_code=status.HTTP_201_CREATED)
def create_categoria(cat_in: CategoriaGastoCreate, db: Session = Depends(get_db)):
    duplicado = db.query(CategoriaGasto).filter(CategoriaGasto.nombre == cat_in.nombre).first()
    if duplicado:
        raise HTTPException(status_code=400, detail="Ya existe una categoría de gasto con este nombre.")
    cat = CategoriaGasto(nombre=cat_in.nombre, descripcion=cat_in.descripcion, color=cat_in.color, activo=cat_in.activo)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/categorias", response_model=List[CategoriaGastoResponse])
def read_categorias(db: Session = Depends(get_db)):
    return db.query(CategoriaGasto).filter(CategoriaGasto.activo == True).order_by(CategoriaGasto.nombre).all()

@router.get("/categorias/all", response_model=List[CategoriaGastoResponse])
def read_all_categorias(db: Session = Depends(get_db)):
    return db.query(CategoriaGasto).order_by(CategoriaGasto.nombre).all()

@router.delete("/categorias/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(cat_id: str, db: Session = Depends(get_db)):
    cat = db.query(CategoriaGasto).filter(CategoriaGasto.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")
    
    # Comprobar si tiene gastos asociados
    has_gastos = db.query(Gasto).filter(Gasto.categoria_gasto_id == cat_id).first() is not None
    if has_gastos:
        # Soft-delete lógico
        cat.activo = False
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="La categoría contiene gastos históricos vinculados. Se ha archivado para preservar reportes."
        )
    db.delete(cat)
    db.commit()


# --- ENDPOINTS FUENTES DE INGRESOS ---
@router.post("/fuentes", response_model=FuenteIngresoResponse, status_code=status.HTTP_201_CREATED)
def create_fuente(fuente_in: FuenteIngresoCreate, db: Session = Depends(get_db)):
    duplicado = db.query(FuenteIngreso).filter(FuenteIngreso.nombre == fuente_in.nombre).first()
    if duplicado:
        raise HTTPException(status_code=400, detail="Ya existe una fuente de ingresos con este nombre.")
    fuente = FuenteIngreso(nombre=fuente_in.nombre, descripcion=fuente_in.descripcion, color=fuente_in.color, activo=fuente_in.activo)
    db.add(fuente)
    db.commit()
    db.refresh(fuente)
    return fuente

@router.get("/fuentes", response_model=List[FuenteIngresoResponse])
def read_fuentes(db: Session = Depends(get_db)):
    return db.query(FuenteIngreso).filter(FuenteIngreso.activo == True).order_by(FuenteIngreso.nombre).all()

@router.get("/fuentes/all", response_model=List[FuenteIngresoResponse])
def read_all_fuentes(db: Session = Depends(get_db)):
    return db.query(FuenteIngreso).order_by(FuenteIngreso.nombre).all()

@router.delete("/fuentes/{fuente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuente(fuente_id: str, db: Session = Depends(get_db)):
    fuente = db.query(FuenteIngreso).filter(FuenteIngreso.id == fuente_id).first()
    if not fuente:
        raise HTTPException(status_code=404, detail="Fuente de ingresos no encontrada.")
    
    has_ingresos = db.query(Ingreso).filter(Ingreso.fuente_ingreso_id == fuente_id).first() is not None
    if has_ingresos:
        fuente.activo = False
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="La fuente contiene ingresos históricos vinculados. Se ha archivado para preservar reportes."
        )
    db.delete(fuente)
    db.commit()


# --- ENDPOINTS GASTOS ---
@router.post("/gastos", response_model=GastoResponse, status_code=status.HTTP_201_CREATED)
def create_gasto(gasto_in: GastoCreate, db: Session = Depends(get_db)):
    verificar_periodo_cerrado(gasto_in.fecha, db)
    
    caja = db.query(Caja).filter(Caja.id == gasto_in.caja_id).first()
    if not caja:
        raise HTTPException(status_code=404, detail="Caja seleccionada no existe.")
    if not caja.activo:
        raise HTTPException(status_code=400, detail="La caja seleccionada no está activa.")
        
    if caja.saldo_actual < gasto_in.monto:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente en la caja '{caja.nombre}'. El saldo disponible es ${caja.saldo_actual:.2f} y el gasto propuesto es ${gasto_in.monto:.2f}."
        )
        
    cat = db.query(CategoriaGasto).filter(CategoriaGasto.id == gasto_in.categoria_gasto_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría seleccionada no existe.")
    
    # Crear gasto
    gasto = Gasto(
        monto=gasto_in.monto,
        fecha=gasto_in.fecha,
        descripcion=gasto_in.descripcion,
        categoria_gasto_id=gasto_in.categoria_gasto_id,
        caja_id=gasto_in.caja_id
    )
    db.add(gasto)
    
    # Restar saldo de la caja afectada
    caja.saldo_actual -= gasto_in.monto
    
    db.commit()
    db.refresh(gasto)
    return gasto

@router.delete("/gastos/{gasto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gasto(gasto_id: str, db: Session = Depends(get_db)):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado.")
    
    verificar_periodo_cerrado(gasto.fecha, db)
    
    # Devolver el dinero a la caja
    caja = db.query(Caja).filter(Caja.id == gasto.caja_id).first()
    if caja:
        caja.saldo_actual += gasto.monto
        
    db.delete(gasto)
    db.commit()


# --- ENDPOINTS INGRESOS ---
@router.post("/ingresos", response_model=IngresoResponse, status_code=status.HTTP_201_CREATED)
def create_ingreso(ingreso_in: IngresoCreate, db: Session = Depends(get_db)):
    verificar_periodo_cerrado(ingreso_in.fecha, db)
    
    caja = db.query(Caja).filter(Caja.id == ingreso_in.caja_id).first()
    if not caja:
        raise HTTPException(status_code=404, detail="Caja seleccionada no existe.")
    if not caja.activo:
        raise HTTPException(status_code=400, detail="La caja seleccionada no está activa.")
        
    fuente = db.query(FuenteIngreso).filter(FuenteIngreso.id == ingreso_in.fuente_ingreso_id).first()
    if not fuente:
        raise HTTPException(status_code=404, detail="Fuente seleccionada no existe.")
        
    ingreso = Ingreso(
        monto=ingreso_in.monto,
        fecha=ingreso_in.fecha,
        descripcion=ingreso_in.descripcion,
        fuente_ingreso_id=ingreso_in.fuente_ingreso_id,
        caja_id=ingreso_in.caja_id
    )
    db.add(ingreso)
    
    # Acreditar saldo de la caja afectada
    caja.saldo_actual += ingreso_in.monto
    
    db.commit()
    db.refresh(ingreso)
    return ingreso

@router.delete("/ingresos/{ingreso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingreso(ingreso_id: str, db: Session = Depends(get_db)):
    ingreso = db.query(Ingreso).filter(Ingreso.id == ingreso_id).first()
    if not ingreso:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado.")
    
    verificar_periodo_cerrado(ingreso.fecha, db)
    
    # Restar el dinero de la caja
    caja = db.query(Caja).filter(Caja.id == ingreso.caja_id).first()
    if caja:
        caja.saldo_actual -= ingreso.monto
        
    db.delete(ingreso)
    db.commit()


# --- FEED DE TRANSACCIONES UNIFICADO ---
@router.get("/feed", response_model=List[TransaccionBase])
def get_transacciones_feed(db: Session = Depends(get_db)):
    gastos = db.query(Gasto).all()
    ingresos = db.query(Ingreso).all()
    
    feed = []
    
    for g in gastos:
        feed.append(TransaccionBase(
            id=g.id,
            tipo="GASTO",
            monto=g.monto,
            fecha=g.fecha,
            descripcion=g.descripcion,
            caja_nombre=g.caja.nombre,
            caja_id=g.caja_id,
            categoria_o_fuente_nombre=g.categoria.nombre,
            categoria_o_fuente_id=g.categoria_gasto_id,
            color=g.categoria.color
        ))
        
    for i in ingresos:
        feed.append(TransaccionBase(
            id=i.id,
            tipo="INGRESO",
            monto=i.monto,
            fecha=i.fecha,
            descripcion=i.descripcion,
            caja_nombre=i.caja.nombre,
            caja_id=i.caja_id,
            categoria_o_fuente_nombre=i.fuente.nombre,
            categoria_o_fuente_id=i.fuente_ingreso_id,
            color=i.fuente.color
        ))
        
    # Ordenar por fecha descendente
    feed.sort(key=lambda t: t.fecha, reverse=True)
    return feed
