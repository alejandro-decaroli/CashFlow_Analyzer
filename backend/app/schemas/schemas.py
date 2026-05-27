from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional

# --- CATEGORIAS ---
class CategoriaGastoBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    color: str = Field("#CCCCCC", max_length=7)
    activo: bool = True

class CategoriaGastoCreate(CategoriaGastoBase):
    pass

class CategoriaGastoResponse(CategoriaGastoBase):
    id: str

    class Config:
        from_attributes = True


# --- FUENTES ---
class FuenteIngresoBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    color: str = Field("#CCCCCC", max_length=7)
    activo: bool = True

class FuenteIngresoCreate(FuenteIngresoBase):
    pass

class FuenteIngresoResponse(FuenteIngresoBase):
    id: str

    class Config:
        from_attributes = True


# --- CAJAS ---
class CajaBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    tipo: str = Field(..., max_length=30)  # BANCO, EFECTIVO, TARJETA_DEBITO, OTRO
    saldo_inicial: Decimal = Field(default=Decimal("0.00"), ge=0)
    activo: bool = True

class CajaCreate(CajaBase):
    pass

class CajaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    tipo: Optional[str] = Field(None, max_length=30)
    activo: Optional[bool] = None

class CajaResponse(CajaBase):
    id: str
    saldo_actual: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# --- GASTOS ---
class GastoBase(BaseModel):
    monto: Decimal = Field(..., gt=0)
    fecha: date
    descripcion: Optional[str] = Field(None, max_length=255)
    categoria_gasto_id: str
    caja_id: str

class GastoCreate(GastoBase):
    pass

class GastoResponse(BaseModel):
    id: str
    monto: Decimal
    fecha: date
    descripcion: Optional[str]
    categoria_gasto_id: str
    caja_id: str
    created_at: datetime
    caja: CajaResponse
    categoria: CategoriaGastoResponse

    class Config:
        from_attributes = True


# --- INGRESOS ---
class IngresoBase(BaseModel):
    monto: Decimal = Field(..., gt=0)
    fecha: date
    descripcion: Optional[str] = Field(None, max_length=255)
    fuente_ingreso_id: str
    caja_id: str

class IngresoCreate(IngresoBase):
    pass

class IngresoResponse(BaseModel):
    id: str
    monto: Decimal
    fecha: date
    descripcion: Optional[str]
    fuente_ingreso_id: str
    caja_id: str
    created_at: datetime
    caja: CajaResponse
    fuente: FuenteIngresoResponse

    class Config:
        from_attributes = True


# --- CONCILIACIONES ---
class ConciliacionCajaInput(BaseModel):
    caja_id: str
    saldo_real: Decimal

class ConciliacionMensualCreate(BaseModel):
    mes: int = Field(..., ge=1, le=12)
    anio: int = Field(..., ge=2020)
    detalles: List[ConciliacionCajaInput]

class ConciliacionCajaResponse(BaseModel):
    id: str
    caja_id: str
    saldo_calculado: Decimal
    saldo_real: Decimal
    diferencia: Decimal
    ajustado: bool
    caja: CajaResponse

    class Config:
        from_attributes = True

class ConciliacionMensualResponse(BaseModel):
    id: str
    mes: int
    anio: int
    fecha_conciliacion: datetime
    estado: str
    detalles: List[ConciliacionCajaResponse]

    class Config:
        from_attributes = True


# --- TRANSACCIONES UNIFICADAS ---
class TransaccionBase(BaseModel):
    id: str
    tipo: str  # GASTO o INGRESO
    monto: Decimal
    fecha: date
    descripcion: Optional[str]
    caja_nombre: str
    caja_id: str
    categoria_o_fuente_nombre: str
    categoria_o_fuente_id: str
    color: str
