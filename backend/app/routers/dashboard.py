from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import extract
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any
from app.db.session import get_db
from app.db.models import Caja, Gasto, Ingreso, CategoriaGasto, FuenteIngreso

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Helper para traducir mes a etiqueta en español
def obtener_nombre_mes(n: int) -> str:
    nombres = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    return nombres.get(n, str(n))

@router.get("/kpis", status_code=status.HTTP_200_OK)
def get_kpis(mes: int, anio: int, db: Session = Depends(get_db)):
    # 1. Ingreso Bruto Mensual
    ingresos = db.query(Ingreso).filter(
        extract('month', Ingreso.fecha) == mes,
        extract('year', Ingreso.fecha) == anio
    ).all()
    ingreso_bruto = sum(i.monto for i in ingresos)
    
    # 2. Gasto Total Mensual
    gastos = db.query(Gasto).filter(
        extract('month', Gasto.fecha) == mes,
        extract('year', Gasto.fecha) == anio
    ).all()
    gasto_total = sum(g.monto for g in gastos)
    
    # 3. Ingreso Neto Mensual (Balance)
    ingreso_neto = Decimal(str(ingreso_bruto)) - Decimal(str(gasto_total))
    
    # 4. Ahorro Acumulado (Suma de saldos actuales de todas las cajas)
    cajas = db.query(Caja).all()
    ahorro_acumulado = sum(c.saldo_actual for c in cajas)
    
    return {
        "ingreso_bruto": ingreso_bruto,
        "gasto_total": gasto_total,
        "ingreso_neto": ingreso_neto,
        "ahorro_acumulado": ahorro_acumulado
    }

@router.get("/mom", status_code=status.HTTP_200_OK)
def get_mom(mes: int, anio: int, db: Session = Depends(get_db)):
    # Calcular mes anterior
    if mes == 1:
        mes_ant = 12
        anio_ant = anio - 1
    else:
        mes_ant = mes - 1
        anio_ant = anio
        
    categorias = db.query(CategoriaGasto).filter(CategoriaGasto.activo == True).all()
    resultados = []
    
    for cat in categorias:
        if cat.nombre == "Ajuste por Conciliación":
            continue
            
        # Gastos mes actual
        gastos_act = db.query(Gasto).filter(
            Gasto.categoria_gasto_id == cat.id,
            extract('month', Gasto.fecha) == mes,
            extract('year', Gasto.fecha) == anio
        ).all()
        suma_act = sum(g.monto for g in gastos_act)
        
        # Gastos mes anterior
        gastos_ant = db.query(Gasto).filter(
            Gasto.categoria_gasto_id == cat.id,
            extract('month', Gasto.fecha) == mes_ant,
            extract('year', Gasto.fecha) == anio_ant
        ).all()
        suma_ant = sum(g.monto for g in gastos_ant)
        
        # Calcular variación porcentual
        if suma_ant > 0:
            var_pct = ((suma_act - suma_ant) / suma_ant) * 100
        elif suma_act > 0:
            var_pct = 100.00
        else:
            var_pct = 0.00
            
        resultados.append({
            "categoria_id": cat.id,
            "categoria_nombre": cat.nombre,
            "color": cat.color,
            "gasto_mes_actual": suma_act,
            "gasto_mes_anterior": suma_ant,
            "variacion_porcentual": round(var_pct, 2)
        })
        
    return resultados

@router.get("/averages", status_code=status.HTTP_200_OK)
def get_averages(db: Session = Depends(get_db)):
    # Contar total de meses con transacciones para el promedio
    todas_transacciones = db.query(Gasto.fecha).all() + db.query(Ingreso.fecha).all()
    meses_unicos = set()
    for t in todas_transacciones:
        meses_unicos.add((t.fecha.year, t.fecha.month))
        
    total_meses = len(meses_unicos) if len(meses_unicos) > 0 else 1
    
    categorias = db.query(CategoriaGasto).filter(CategoriaGasto.activo == True).all()
    resultados = []
    
    for cat in categorias:
        if cat.nombre == "Ajuste por Conciliación":
            continue
            
        gastos = db.query(Gasto).filter(Gasto.categoria_gasto_id == cat.id).all()
        total_gastado = sum(g.monto for g in gastos)
        promedio = Decimal(str(total_gastado)) / Decimal(str(total_meses))
        
        resultados.append({
            "categoria_id": cat.id,
            "categoria_nombre": cat.nombre,
            "color": cat.color,
            "total_gastado_historico": total_gastado,
            "promedio_mensual": round(promedio, 2)
        })
        
    return resultados

@router.get("/top-expenses", status_code=status.HTTP_200_OK)
def get_top_expenses(mes: int, anio: int, db: Session = Depends(get_db)):
    top = db.query(Gasto).filter(
        extract('month', Gasto.fecha) == mes,
        extract('year', Gasto.fecha) == anio
    ).order_by(Gasto.monto.desc()).limit(5).all()
    
    resultados = []
    for g in top:
        resultados.append({
            "id": g.id,
            "monto": g.monto,
            "fecha": g.fecha,
            "descripcion": g.descripcion,
            "caja_nombre": g.caja.nombre,
            "categoria_nombre": g.categoria.nombre,
            "color": g.categoria.color
        })
    return resultados

@router.get("/charts", status_code=status.HTTP_200_OK)
def get_charts_data(db: Session = Depends(get_db)):
    # Recopilar datos históricos de los últimos 6 meses (Marzo a Agosto 2026, por ejemplo)
    # Para simplificar y hacerlo flexible, buscaremos los últimos 6 meses basándonos en las transacciones
    todas_transacciones = db.query(Gasto.fecha).all() + db.query(Ingreso.fecha).all()
    meses_unicos = sorted(list(set((t.fecha.year, t.fecha.month) for t in todas_transacciones)), reverse=True)[:6]
    meses_unicos.reverse()  # Orden cronológico
    
    resultados = []
    
    for (anio, mes) in meses_unicos:
        ingresos = db.query(Ingreso).filter(
            extract('month', Ingreso.fecha) == mes,
            extract('year', Ingreso.fecha) == anio
        ).all()
        suma_ing = sum(i.monto for i in ingresos)
        
        gastos = db.query(Gasto).filter(
            extract('month', Gasto.fecha) == mes,
            extract('year', Gasto.fecha) == anio
        ).all()
        suma_gas = sum(g.monto for g in gastos)
        
        resultados.append({
            "mes": mes,
            "anio": anio,
            "label": f"{obtener_nombre_mes(mes)} {anio}",
            "ingresos": suma_ing,
            "gastos": suma_gas
        })
        
    return resultados
