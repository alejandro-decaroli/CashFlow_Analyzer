# CashFlow Personal Analyzer (CPA) 📈

**CashFlow Personal Analyzer (CPA)** es una aplicación web de finanzas personales diseñada para reemplazar sistemas de contabilidad domésticos basados en planillas tradicionales (como Excel), ofreciendo un entorno relacional, seguro, inmutable y visualmente impactante.

Desarrollada bajo una estética oscura moderna con efectos de **glassmorphism**, CPA te permite gestionar tus cuentas ("cajas"), clasificar tus ingresos y gastos de forma granular, visualizar análisis en tiempo real mediante widgets y gráficos dinámicos, y realizar un riguroso proceso de **auditoría y conciliación mensual** para mantener la consistencia entre tus registros y tu dinero real.

---

## 🎯 El Problema que Resuelve

Llevar el control financiero en Excel o planillas manuales presenta tres grandes problemas operativos:
1. **Falta de Trazabilidad y Consistencia:** Es sumamente fácil alterar celdas históricas accidentalmente, lo que destruye el balance acumulado y dificulta rastrear discrepancias pasadas.
2. **Saldos Negativos Silenciosos:** Las hojas de cálculo permiten registrar egresos sin validar si la cuenta de origen realmente posee fondos, desvirtuando el estado real del efectivo o cuentas bancarias.
3. **Ausencia de Auditoría de Cierre:** No existe una metodología clara para validar el saldo teórico de la planilla contra el dinero real físico o bancario al cierre de cada mes, permitiendo que "desaparezca" dinero sin explicación.

### ¿Cómo lo soluciona CPA?
* **Inmutabilidad por Conciliación:** Al final de cada mes calendario, CPA te guía a través de un **Reconciliation Wizard** (asistente de conciliación) para declarar el dinero real físico/bancario. Una vez consolidado y cerrado el período, las transacciones del mes se vuelven de **sólo lectura**, protegiendo tu historial de alteraciones accidentales.
* **Auto-Ajustes de Auditoría:** Si existen diferencias menores entre el saldo real y el del sistema al cerrar el mes, CPA calcula y registra automáticamente ajustes equilibrantes etiquetados bajo la categoría de sistema especial "Ajuste por Conciliación".
* **Prevención Activa de Saldos Negativos:** El sistema impide de forma estricta (tanto en la interfaz web como a nivel de API en el servidor) el registro de cualquier egreso que supere el saldo actual disponible de la caja emisora, informando explícitamente la situación al usuario.
* **Validación de Datos Sólida:** El saldo inicial de las cajas creadas se valida de manera mandatoria para evitar importes negativos durante el registro de cuentas.

---

## 🛠️ Stack Tecnológico Utilizado

CPA está construido con tecnologías modernas y robustas de extremo a extremo:

* **Core & Logic (Frontend):** [Svelte 5](https://svelte.dev/) con Vite. Ofrece reactividad ultra-rápida, un tamaño de paquete mínimo y un rendimiento de renderizado excepcional en clientes web y dispositivos móviles.
* **Aesthetics (CSS):** Vanilla CSS premium adaptativo (Responsive), diseñado con variables del sistema para colores, gradientes vibrantes y desenfoques radiales de alta fidelidad.
* **Backend API (Servidor):** [FastAPI (Python 3.11)](https://fastapi.tiangolo.com/) y Uvicorn. Un framework asíncrono de alto rendimiento, autodocumentado y validado de forma estricta mediante **Pydantic**.
* **ORM & Database:** [SQLAlchemy](https://www.sqlalchemy.org/) para el mapeo relacional y [PostgreSQL 15](https://www.postgresql.org/) como motor relacional transaccional robusto con restricciones físicas estrictas (`ON DELETE RESTRICT`).
* **Environment & Deployment:** [Docker](https://www.docker.com/) y **Docker Compose** para orquestar la aplicación en contenedores aislados y reproducibles en menos de 10 segundos.

---

## 📦 Requisitos Previos

Asegúrate de tener instalados en tu sistema local:
* **Docker** (v20.10+)
* **Docker Compose** (v2.0+)

---

## 🚀 Instalación y Despliegue en 2 Pasos

Toda la aplicación está automatizada para ejecutarse en contenedores Docker mediante hot-reload en desarrollo.

### Paso 1: Levantar los contenedores
Abre una terminal en la raíz del proyecto y ejecuta el siguiente comando para construir e iniciar los servicios de base de datos, backend y frontend:

```bash
docker compose up --build -d
```

Este comando:
1. Descargará y levantará el servidor **PostgreSQL 15** en el puerto `5432`.
2. Compilará la imagen de **FastAPI** y lanzará el servidor en el puerto `8000`.
3. Compilará el servidor de desarrollo de **Svelte/Vite** y lo iniciará en el puerto `5173`.
4. Creará automáticamente las tablas relacionales y sembrará los registros obligatorios del sistema de manera limpia.

### Paso 2: Acceder a la aplicación
Una vez completado el inicio, abre tu navegador favorito y accede a:

* **Aplicación Web (UI):** [http://localhost:5173](http://localhost:5173)
* **Documentación Interactiva de la API (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

Para detener los servicios, simplemente ejecuta:
```bash
docker compose down
```

---

## 💡 Guía de Uso del Sistema

Para comenzar a operar con tus finanzas limpias en CPA, te sugerimos seguir este flujo:

1. **Configura tus Catálogos:** Ve a la sección **Catálogos** en la barra de navegación. Configura tus categorías de gasto (ej. Comida, Alquiler, Impuestos) y tus fuentes de ingreso (ej. Sueldo Principal, Freelance) asignándoles colores para identificarlos rápidamente en los gráficos.
2. **Crea tus Cajas:** Navega a la sección **Cajas** y agrega tus cuentas (ej. Banco Santa Fe, Efectivo Billetera, Tarjeta de Débito) definiendo un **saldo inicial mayor o igual a 0**. El sistema no te permitirá saldo negativo inicial.
3. **Registra tus Movimientos:**
   * Haz clic en **Registrar Ingreso** para acreditar dinero a una de tus cajas en base a tus fuentes creadas.
   * Haz clic en **Registrar Gasto** para debitar egresos. Si intentas ingresar un gasto mayor al saldo actual disponible de la caja seleccionada, la app te informará que no posees fondos suficientes y detendrá la operación.
4. **Visualiza el Dashboard:** Consulta en tiempo real tus métricas de Ingreso Bruto, Gasto Total, Ahorro Acumulado, la tendencia de ingresos vs gastos en el gráfico de contraste máximo y tu ranking de top 5 mayores consumos mensuales.
5. **Realiza tu Conciliación:** Al finalizar el mes, accede a la sección **Auditoría**. Selecciona el mes y año a auditar, presiona "Iniciar Auditoría", cuenta tus saldos reales y decláralos en la grilla. Presiona "Confirmar y Cerrar Período" en el diálogo premium estilizado. El sistema aplicará los auto-ajustes necesarios y blindará el mes contra alteraciones accidentales futuras.

## Fotos

<img width="1894" height="2673" alt="Screenshot 2026-05-27 at 15-53-52 CashFlow Analyzer — Finanzas Personales" src="https://github.com/user-attachments/assets/e40efb76-cd76-4347-a6e0-9f22b114c93f" />
<img width="1895" height="1272" alt="Screenshot 2026-05-27 at 14-15-59 CashFlow Analyzer — Finanzas Personales" src="https://github.com/user-attachments/assets/5e52a0bd-455d-4abe-91ad-0eb2b7fa5396" />
<img width="1896" height="588" alt="Screenshot 2026-05-27 at 14-16-13 CashFlow Analyzer — Finanzas Personales" src="https://github.com/user-attachments/assets/419e57c1-fb96-43e2-8fe7-fd232c16b186" />
<img width="1895" height="1026" alt="Screenshot 2026-05-27 at 14-16-45 CashFlow Analyzer — Finanzas Personales" src="https://github.com/user-attachments/assets/0662230a-90f4-4f68-b4d0-d748385f7bbc" />
<img width="1820" height="473" alt="Screenshot 2026-05-27 at 14-17-07 CashFlow Analyzer — Finanzas Personales" src="https://github.com/user-attachments/assets/9010b7e7-be80-498d-bd95-2fd0d04bd76e" />
<img width="1896" height="936" alt="Screenshot 2026-05-27 at 14-17-12 CashFlow Analyzer — Finanzas Personales" src="https://github.com/user-attachments/assets/7df52a87-5162-4a7b-aad7-dab4268abedd" />

