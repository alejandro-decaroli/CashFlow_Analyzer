import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Numeric, Date, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

class Caja(Base):
    __tablename__ = "cajas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), unique=True, nullable=False)
    tipo = Column(String(30), nullable=False)  # BANCO, EFECTIVO, TARJETA_DEBITO, OTRO
    saldo_inicial = Column(Numeric(12, 2), nullable=False, default=0.00)
    saldo_actual = Column(Numeric(12, 2), nullable=False, default=0.00)
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    gastos = relationship("Gasto", back_populates="caja", cascade="all, delete-orphan")
    ingresos = relationship("Ingreso", back_populates="caja", cascade="all, delete-orphan")
    conciliaciones = relationship("ConciliacionCaja", back_populates="caja", cascade="all, delete-orphan")


class CategoriaGasto(Base):
    __tablename__ = "categorias_gastos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)
    color = Column(String(7), nullable=False, default="#CCCCCC")
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    gastos = relationship("Gasto", back_populates="categoria")


class FuenteIngreso(Base):
    __tablename__ = "fuentes_ingresos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)
    color = Column(String(7), nullable=False, default="#CCCCCC")
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    ingresos = relationship("Ingreso", back_populates="fuente")


class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    monto = Column(Numeric(12, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    descripcion = Column(String(255), nullable=True)
    categoria_gasto_id = Column(String(36), ForeignKey("categorias_gastos.id", ondelete="RESTRICT"), nullable=False)
    caja_id = Column(String(36), ForeignKey("cajas.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    caja = relationship("Caja", back_populates="gastos")
    categoria = relationship("CategoriaGasto")


class Ingreso(Base):
    __tablename__ = "ingresos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    monto = Column(Numeric(12, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    descripcion = Column(String(255), nullable=True)
    fuente_ingreso_id = Column(String(36), ForeignKey("fuentes_ingresos.id", ondelete="RESTRICT"), nullable=False)
    caja_id = Column(String(36), ForeignKey("cajas.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    caja = relationship("Caja", back_populates="ingresos")
    fuente = relationship("FuenteIngreso")


class ConciliacionMensual(Base):
    __tablename__ = "conciliaciones_mensuales"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mes = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    fecha_conciliacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    estado = Column(String(30), nullable=False, default="ABIERTO")  # ABIERTO, CERRADO

    __table_args__ = (UniqueConstraint("mes", "anio", name="unique_mes_anio"),)

    detalles = relationship("ConciliacionCaja", back_populates="conciliacion", cascade="all, delete-orphan")


class ConciliacionCaja(Base):
    __tablename__ = "conciliaciones_cajas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conciliacion_mensual_id = Column(String(36), ForeignKey("conciliaciones_mensuales.id", ondelete="CASCADE"), nullable=False)
    caja_id = Column(String(36), ForeignKey("cajas.id", ondelete="RESTRICT"), nullable=False)
    saldo_calculado = Column(Numeric(12, 2), nullable=False)
    saldo_real = Column(Numeric(12, 2), nullable=False)
    diferencia = Column(Numeric(12, 2), nullable=False)
    ajustado = Column(Boolean, nullable=False, default=False)

    __table_args__ = (UniqueConstraint("conciliacion_mensual_id", "caja_id", name="unique_conciliacion_caja"),)

    conciliacion = relationship("ConciliacionMensual", back_populates="detalles")
    caja = relationship("Caja", back_populates="conciliaciones")
