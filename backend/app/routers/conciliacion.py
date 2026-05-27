import calendar
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, datetime
from typing import List
from app.db.session import get_db
from app.db.models import (
    Caja, Gasto, Ingreso, ConciliacionMensual, ConciliacionCaja,
    CategoriaGasto, FuenteIngreso
)
from app.schemas.schemas import ConciliacionMensualResponse, ConciliacionMensualCreate

router = APIRouter(prefix="/conciliacion", tags=["Conciliación"])

# Helper para calcular el último día de un mes calendario
def obtener_ultimo_dia_mes(anio: int, mes: int) -> date:
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, ultimo_dia)

# Helper para calcular el saldo de sistema de una caja al cierre de un mes dado
def calcular_saldo_sistema_al_cierre(caja_id: str, anio: int, mes: int, db: Session) -> Decimal:
    caja = db.query(Caja).filter(Caja.id == caja_id).first()
    if not caja:
        raise HTTPException(status_code=404, detail="Caja no encontrada.")
    
    fin_mes = obtener_ultimo_dia_mes(anio, mes)
    
    # Sumar ingresos hasta el fin de ese mes
    ingresos_total = db.query(Ingreso).filter(
        Ingreso.caja_id == caja_id,
        Ingreso.fecha <= fin_mes
    ).all()
    suma_ingresos = sum(i.monto for i in ingresos_total)
    
    # Sumar gastos hasta el fin de ese mes
    gastos_total = db.query(Gasto).filter(
        Gasto.caja_id == caja_id,
        Gasto.fecha <= fin_mes
    ).all()
    suma_gastos = sum(g.monto for g in gastos_total)
    
    saldo_calculado = caja.saldo_inicial + Decimal(str(suma_ingresos)) - Decimal(str(suma_gastos))
    return Decimal(str(saldo_calculado))

@router.get("/history", response_model=List[ConciliacionMensualResponse])
def get_historial_conciliaciones(db: Session = Depends(get_db)):
    return db.query(ConciliacionMensual).order_by(
        ConciliacionMensual.anio.desc(),
        ConciliacionMensual.mes.desc()
    ).all()

@router.get("/calculate", status_code=status.HTTP_200_OK)
def get_calculo_saldos(mes: int, anio: int, db: Session = Depends(get_db)):
    # Validar si el mes ya está cerrado
    existente = db.query(ConciliacionMensual).filter(
        ConciliacionMensual.mes == mes,
        ConciliacionMensual.anio == anio
    ).first()
    
    cajas = db.query(Caja).filter(Caja.activo == True).all()
    resultados = []
    
    for c in cajas:
        saldo_calc = calcular_saldo_sistema_al_cierre(c.id, anio, mes, db)
        resultados.append({
            "caja_id": c.id,
            "caja_nombre": c.nombre,
            "caja_tipo": c.tipo,
            "saldo_calculado": saldo_calc,
            "ya_conciliado": existente is not None,
            "estado_periodo": existente.estado if existente else "ABIERTO"
        })
        
    return {
        "mes": mes,
        "anio": anio,
        "cajas": resultados
    }

@router.post("/submit", response_model=ConciliacionMensualResponse)
def submit_conciliacion(con_in: ConciliacionMensualCreate, db: Session = Depends(get_db)):
    # 1. Validar que no exista conciliación cerrada para el período
    existente = db.query(ConciliacionMensual).filter(
        ConciliacionMensual.mes == con_in.mes,
        ConciliacionMensual.anio == con_in.anio
    ).first()
    
    if existente and existente.estado == "CERRADO":
        raise HTTPException(
            status_code=400,
            detail=f"El período {con_in.mes}/{con_in.anio} ya está cerrado y conciliado."
        )
        
    # Obtener el último día del mes a conciliar para las fechas de transacciones de ajuste
    fecha_ajuste = obtener_ultimo_dia_mes(con_in.anio, con_in.mes)
    
    # 2. Si hay conciliación abierta, la reutilizamos; si no, creamos una nueva
    if existente:
        conciliacion = existente
        # Limpiar detalles anteriores si re-conciliamos
        db.query(ConciliacionCaja).filter(
            ConciliacionCaja.conciliacion_mensual_id == conciliacion.id
        ).delete()
    else:
        conciliacion = ConciliacionMensual(
            mes=con_in.mes,
            anio=con_in.anio,
            fecha_conciliacion=datetime.utcnow(),
            estado="CERRADO"
        )
        db.add(conciliacion)
        db.commit()
        db.refresh(conciliacion)
        
    # Buscar categorías especiales para los ajustes
    cat_ajuste = db.query(CategoriaGasto).filter(CategoriaGasto.nombre == "Ajuste por Conciliación").first()
    f_ajuste = db.query(FuenteIngreso).filter(FuenteIngreso.nombre == "Ajuste por Conciliación").first()
    
    if not cat_ajuste or not f_ajuste:
        raise HTTPException(
            status_code=500,
            detail="Falta configurar las categorías especiales de Ajuste en la base de datos."
        )
        
    # 3. Iterar por cada caja enviada
    for item in con_in.detalles:
        caja = db.query(Caja).filter(Caja.id == item.caja_id).first()
        if not caja:
            continue
            
        saldo_calc = calcular_saldo_sistema_al_cierre(caja.id, con_in.anio, con_in.mes, db)
        dif = item.saldo_real - saldo_calc
        ajustado = False
        
        # 4. Generar transacciones automáticas de ajuste si diferencia != 0
        if dif != 0:
            if dif > 0:
                # Sobrante -> Ingreso de ajuste
                nuevo_ingreso = Ingreso(
                    monto=dif,
                    fecha=fecha_ajuste,
                    descripcion=f"Ajuste automático por conciliación mensual {con_in.mes}/{con_in.anio}",
                    fuente_ingreso_id=f_ajuste.id,
                    caja_id=caja.id
                )
                db.add(nuevo_ingreso)
                # Actualizar el saldo actual de la caja
                caja.saldo_actual += dif
            else:
                # Faltante -> Gasto de ajuste
                monto_gasto = abs(dif)
                nuevo_gasto = Gasto(
                    monto=monto_gasto,
                    fecha=fecha_ajuste,
                    descripcion=f"Ajuste automático por conciliación mensual {con_in.mes}/{con_in.anio}",
                    categoria_gasto_id=cat_ajuste.id,
                    caja_id=caja.id
                )
                db.add(nuevo_gasto)
                # Actualizar el saldo actual de la caja
                caja.saldo_actual -= monto_gasto
                
            ajustado = True
            
        # Crear detalle de conciliación
        cc = ConciliacionCaja(
            conciliacion_mensual_id=conciliacion.id,
            caja_id=caja.id,
            saldo_calculado=saldo_calc,
            saldo_real=item.saldo_real,
            diferencia=dif,
            ajustado=ajustado
        )
        db.add(cc)
        
    conciliacion.estado = "CERRADO"
    conciliacion.fecha_conciliacion = datetime.utcnow()
    
    db.commit()
    db.refresh(conciliacion)
    return conciliacion
