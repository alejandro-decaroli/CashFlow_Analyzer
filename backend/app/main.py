from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import cajas, transacciones, conciliacion, dashboard

app = FastAPI(
    title="CashFlow Personal Analyzer API",
    description="Backend API relacional para auditoría de finanzas domésticas y conciliación de cajas.",
    version="1.0.0"
)

# Configurar middleware de CORS para habilitar la comunicación fluida con Svelte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Habilitar cualquier origen temporalmente para facilitar desarrollo local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers
app.include_router(cajas.router, prefix=settings.API_V1_STR)
app.include_router(transacciones.router, prefix=settings.API_V1_STR)
app.include_router(conciliacion.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "CashFlow Personal Analyzer API",
        "version": "1.0.0",
        "documentation": "/docs"
    }
