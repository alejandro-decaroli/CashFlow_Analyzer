import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

# Añadir directorio raíz al path de Python para permitir importaciones correctas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import engine, Base, SessionLocal
from app.db.models import Caja, CategoriaGasto, FuenteIngreso, Gasto, Ingreso, ConciliacionMensual, ConciliacionCaja

def init_db():

    pass
    # 1. Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    print("Esquema de base de datos creado exitosamente.")

    db = SessionLocal()
    try:
        # Verificar si ya existen datos para evitar duplicar
        if db.query(Caja).first() is not None:
            print("La base de datos ya contiene información. Omitiendo la siembra de datos semilla.")
            return

        print("Iniciando la siembra de datos semilla...")

        # 2. Crear Cajas / Cuentas
        caja_efectivo = Caja(
            nombre="Efectivo Bolsillo",
            tipo="EFECTIVO",
            saldo_inicial=Decimal("1500.00"),
            saldo_actual=Decimal("200.00"),  # Calculado al final de las transacciones
            activo=True
        )
        caja_banco = Caja(
            nombre="Banco Santa Fe",
            tipo="BANCO",
            saldo_inicial=Decimal("50000.00"),
            saldo_actual=Decimal("124700.00"),
            activo=True
        )
        caja_tarjeta = Caja(
            nombre="Tarjeta de Débito",
            tipo="TARJETA_DEBITO",
            saldo_inicial=Decimal("12000.00"),
            saldo_actual=Decimal("500.00"),
            activo=True
        )
        db.add_all([caja_efectivo, caja_banco, caja_tarjeta])
        db.commit()

        # 3. Crear Categorías de Gastos
        cat_comida = CategoriaGasto(nombre="Comida / Supermercado", descripcion="Alimentos y compras de despensa", color="#ef4444")
        cat_alquiler = CategoriaGasto(nombre="Alquiler / Vivienda", descripcion="Pago de alquiler y expensas", color="#3b82f6")
        cat_servicios = CategoriaGasto(nombre="Servicios (Luz, Internet)", descripcion="Luz, gas, agua, internet, telefonía", color="#f59e0b")
        cat_transporte = CategoriaGasto(nombre="Transporte", descripcion="Sube, combustible, taxis", color="#10b981")
        cat_ocio = CategoriaGasto(nombre="Ocio y Salidas", descripcion="Restaurantes, cine, hobbies", color="#8b5cf6")
        cat_ajuste = CategoriaGasto(nombre="Ajuste por Conciliación", descripcion="Ajustes automáticos de balance", color="#6b7280", activo=False)
        db.add_all([cat_comida, cat_alquiler, cat_servicios, cat_transporte, cat_ocio, cat_ajuste])
        db.commit()

        # 4. Crear Fuentes de Ingresos
        f_sueldo = FuenteIngreso(nombre="Sueldo Principal", descripcion="Cobro de haberes mensuales en relación de dependencia", color="#10b981")
        f_freelance = FuenteIngreso(nombre="Freelance / Desarrollos", descripcion="Proyectos independientes de programación", color="#14b8a6")
        f_inversiones = FuenteIngreso(nombre="Rendimientos / Inversiones", descripcion="Intereses de plazos fijos, dividendos", color="#6366f1")
        f_ajuste = FuenteIngreso(nombre="Ajuste por Conciliación", descripcion="Ajustes automáticos de balance", color="#6b7280", activo=False)
        db.add_all([f_sueldo, f_freelance, f_inversiones, f_ajuste])
        db.commit()

        # 5. Transacciones - MARZO 2026
        transacciones_marzo = [
            # Ingresos
            Ingreso(monto=Decimal("45000.00"), fecha=date(2026, 3, 1), descripcion="Cobro Haberes Marzo", fuente=f_sueldo, caja=caja_banco),
            Ingreso(monto=Decimal("8000.00"), fecha=date(2026, 3, 15), descripcion="Maquetado Landing Page", fuente=f_freelance, caja=caja_banco),
            Ingreso(monto=Decimal("3000.00"), fecha=date(2026, 3, 25), descripcion="Rendimientos Plazo Fijo", fuente=f_inversiones, caja=caja_efectivo),
            # Gastos
            Gasto(monto=Decimal("22000.00"), fecha=date(2026, 3, 3), descripcion="Alquiler Depto", categoria=cat_alquiler, caja=caja_banco),
            Gasto(monto=Decimal("4500.00"), fecha=date(2026, 3, 5), descripcion="Facturas Luz + Internet", categoria=cat_servicios, caja=caja_banco),
            Gasto(monto=Decimal("1000.00"), fecha=date(2026, 3, 10), descripcion="Verdulería", categoria=cat_comida, caja=caja_efectivo),
            Gasto(monto=Decimal("800.00"), fecha=date(2026, 3, 12), descripcion="Carga de SUBE", categoria=cat_transporte, caja=caja_efectivo),
            Gasto(monto=Decimal("3000.00"), fecha=date(2026, 3, 20), descripcion="Cena Cumpleaños", categoria=cat_ocio, caja=caja_tarjeta),
            Gasto(monto=Decimal("2000.00"), fecha=date(2026, 3, 7), descripcion="Supermercado Semanal 1", categoria=cat_comida, caja=caja_tarjeta),
            Gasto(monto=Decimal("2000.00"), fecha=date(2026, 3, 14), descripcion="Supermercado Semanal 2", categoria=cat_comida, caja=caja_tarjeta),
            Gasto(monto=Decimal("2000.00"), fecha=date(2026, 3, 21), descripcion="Supermercado Semanal 3", categoria=cat_comida, caja=caja_tarjeta),
            Gasto(monto=Decimal("2000.00"), fecha=date(2026, 3, 28), descripcion="Supermercado Semanal 4", categoria=cat_comida, caja=caja_tarjeta)
        ]
        db.add_all(transacciones_marzo)

        # 6. Transacciones - ABRIL 2026
        transacciones_abril = [
            # Ingresos
            Ingreso(monto=Decimal("45000.00"), fecha=date(2026, 4, 1), descripcion="Cobro Haberes Abril", fuente=f_sueldo, caja=caja_banco),
            Ingreso(monto=Decimal("12000.00"), fecha=date(2026, 4, 10), descripcion="Desarrollo Dashboard API", fuente=f_freelance, caja=caja_banco),
            Ingreso(monto=Decimal("10000.00"), fecha=date(2026, 4, 15), descripcion="Cobro freelance diseño", fuente=f_freelance, caja=caja_tarjeta),
            # Gastos
            Gasto(monto=Decimal("22000.00"), fecha=date(2026, 4, 3), descripcion="Alquiler Depto", categoria=cat_alquiler, caja=caja_banco),
            Gasto(monto=Decimal("4800.00"), fecha=date(2026, 4, 5), descripcion="Facturas Luz + Agua", categoria=cat_servicios, caja=caja_banco),
            Gasto(monto=Decimal("1000.00"), fecha=date(2026, 4, 12), descripcion="Carga Combustible", categoria=cat_transporte, caja=caja_efectivo),
            Gasto(monto=Decimal("1200.00"), fecha=date(2026, 4, 14), descripcion="Almuerzo rotisería", categoria=cat_comida, caja=caja_efectivo),
            Gasto(monto=Decimal("4000.00"), fecha=date(2026, 4, 18), descripcion="Entradas Recital", categoria=cat_ocio, caja=caja_tarjeta),
            Gasto(monto=Decimal("2000.00"), fecha=date(2026, 4, 7), descripcion="Supermercado Semanal 1", categoria=cat_comida, caja=caja_tarjeta),
            Gasto(monto=Decimal("2000.00"), fecha=date(2026, 4, 14), descripcion="Supermercado Semanal 2", categoria=cat_comida, caja=caja_tarjeta),
            Gasto(monto=Decimal("2000.00"), fecha=date(2026, 4, 21), descripcion="Supermercado Semanal 3", categoria=cat_comida, caja=caja_tarjeta)
        ]
        db.add_all(transacciones_abril)

        # 7. Transacciones - MAYO 2026
        transacciones_mayo = [
            # Ingresos
            Ingreso(monto=Decimal("45000.00"), fecha=date(2026, 5, 1), descripcion="Cobro Haberes Mayo", fuente=f_sueldo, caja=caja_banco),
            Ingreso(monto=Decimal("4000.00"), fecha=date(2026, 5, 12), descripcion="Rendimientos Fondo Común", fuente=f_inversiones, caja=caja_tarjeta),
            # Gastos
            Gasto(monto=Decimal("22000.00"), fecha=date(2026, 5, 3), descripcion="Alquiler Depto", categoria=cat_alquiler, caja=caja_banco),
            Gasto(monto=Decimal("5000.00"), fecha=date(2026, 5, 5), descripcion="Facturas Servicios", categoria=cat_servicios, caja=caja_banco),
            Gasto(monto=Decimal("300.00"), fecha=date(2026, 5, 10), descripcion="Viaje SUBE", categoria=cat_transporte, caja=caja_efectivo),
            Gasto(monto=Decimal("1500.00"), fecha=date(2026, 5, 15), descripcion="Cine + Pochoclos", categoria=cat_ocio, caja=caja_tarjeta),
            Gasto(monto=Decimal("3000.00"), fecha=date(2026, 5, 14), descripcion="Compra Carnicería", categoria=cat_comida, caja=caja_tarjeta)
        ]
        db.add_all(transacciones_mayo)

        db.commit()

        # 8. Conciliaciones pasadas
        # Marzo 2026 (Cerrada sin discrepancias)
        conciliacion_marzo = ConciliacionMensual(
            mes=3,
            anio=2026,
            fecha_conciliacion=datetime(2026, 3, 31, 23, 30),
            estado="CERRADO"
        )
        db.add(conciliacion_marzo)
        db.commit()

        cc_marzo_efectivo = ConciliacionCaja(
            conciliacion_mensual_id=conciliacion_marzo.id,
            caja_id=caja_efectivo.id,
            saldo_calculado=Decimal("2700.00"),
            saldo_real=Decimal("2700.00"),
            diferencia=Decimal("0.00"),
            ajustado=False
        )
        cc_marzo_banco = ConciliacionCaja(
            conciliacion_mensual_id=conciliacion_marzo.id,
            caja_id=caja_banco.id,
            saldo_calculado=Decimal("76500.00"),
            saldo_real=Decimal("76500.00"),
            diferencia=Decimal("0.00"),
            ajustado=False
        )
        cc_marzo_tarjeta = ConciliacionCaja(
            conciliacion_mensual_id=conciliacion_marzo.id,
            caja_id=caja_tarjeta.id,
            saldo_calculado=Decimal("1000.00"),
            saldo_real=Decimal("1000.00"),
            diferencia=Decimal("0.00"),
            ajustado=False
        )
        db.add_all([cc_marzo_efectivo, cc_marzo_banco, cc_marzo_tarjeta])

        # Abril 2026 (Cerrada sin discrepancias)
        conciliacion_abril = ConciliacionMensual(
            mes=4,
            anio=2026,
            fecha_conciliacion=datetime(2026, 4, 30, 23, 45),
            estado="CERRADO"
        )
        db.add(conciliacion_abril)
        db.commit()

        cc_abril_efectivo = ConciliacionCaja(
            conciliacion_mensual_id=conciliacion_abril.id,
            caja_id=caja_efectivo.id,
            saldo_calculado=Decimal("500.00"),
            saldo_real=Decimal("500.00"),
            diferencia=Decimal("0.00"),
            ajustado=False
        )
        cc_abril_banco = ConciliacionCaja(
            conciliacion_mensual_id=conciliacion_abril.id,
            caja_id=caja_banco.id,
            saldo_calculado=Decimal("106700.00"),
            saldo_real=Decimal("106700.00"),
            diferencia=Decimal("0.00"),
            ajustado=False
        )
        cc_abril_tarjeta = ConciliacionCaja(
            conciliacion_mensual_id=conciliacion_abril.id,
            caja_id=caja_tarjeta.id,
            saldo_calculado=Decimal("1000.00"),
            saldo_real=Decimal("1000.00"),
            diferencia=Decimal("0.00"),
            ajustado=False
        )
        db.add_all([cc_abril_efectivo, cc_abril_banco, cc_abril_tarjeta])

        db.commit()
        print("Siembra de datos semilla completada exitosamente.")

    except Exception as e:
        db.rollback()
        print(f"Error durante la inicialización de la base de datos: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
