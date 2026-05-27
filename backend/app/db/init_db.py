import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

# Añadir directorio raíz al path de Python para permitir importaciones correctas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import engine, Base, SessionLocal
from app.db.models import Caja, CategoriaGasto, FuenteIngreso, Gasto, Ingreso, ConciliacionMensual, ConciliacionCaja

def init_db():
    # 1. Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    print("Esquema de base de datos creado exitosamente.")

    db = SessionLocal()
    try:
        # Verificar y sembrar únicamente los registros de sistema requeridos para la conciliación
        cat_ajuste = db.query(CategoriaGasto).filter(CategoriaGasto.nombre == "Ajuste por Conciliación").first()
        if not cat_ajuste:
            cat_ajuste = CategoriaGasto(
                nombre="Ajuste por Conciliación", 
                descripcion="Ajustes automáticos de balance", 
                color="#6b7280", 
                activo=False
            )
            db.add(cat_ajuste)

        f_ajuste = db.query(FuenteIngreso).filter(FuenteIngreso.nombre == "Ajuste por Conciliación").first()
        if not f_ajuste:
            f_ajuste = FuenteIngreso(
                nombre="Ajuste por Conciliación", 
                descripcion="Ajustes automáticos de balance", 
                color="#6b7280", 
                activo=False
            )
            db.add(f_ajuste)

        db.commit()
        print("Base de datos inicializada limpia (registros de sistema configurados).")

    except Exception as e:
        db.rollback()
        print(f"Error durante la inicialización de la base de datos: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
