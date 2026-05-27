Título: Especificación de Requerimientos del Sistema
Autor: Antigravity (IA Analyst)
Fecha de Última Actualización: Miércoles, 20 de mayo de 2026
Versión: 0.1.0

# Especificación de Requerimientos del Sistema: CashFlow Personal Analyzer (CPA)

Este documento detalla los Requerimientos Funcionales (RF) y Requerimientos No Funcionales (RNF) para el sistema **CashFlow Personal Analyzer (CPA)**. Su objetivo es servir de guía técnica definitiva para los desarrolladores durante el diseño e implementación de las interfaces en Svelte, la API en FastAPI y el esquema en PostgreSQL, asegurando que se cumplan las necesidades financieras y operativas de Alejandro.

---

## 1. Requerimientos Funcionales (RF)

Los requerimientos funcionales especifican los comportamientos y servicios que el sistema debe proporcionar activamente a Alejandro.

### 1.1. Módulo de Gestión de Cajas (Cuentas/Bancos) - `RF-1`
* **`RF-1.1` Registro de Caja:** El sistema debe permitir registrar una nueva caja especificando obligatoriamente: Nombre (único), Tipo (Efectivo, Banco, Tarjeta, Otro) y Saldo Inicial.
* **`RF-1.2` Consulta de Saldos en Tiempo Real:** El sistema debe listar todas las cajas con sus respectivos saldos iniciales y saldos actuales calculados de forma dinámica.
* **`RF-1.3` Modificación de Cajas:** El sistema debe permitir editar el nombre y tipo de una caja existente. No se permitirá modificar el saldo actual de forma directa desde este módulo para no violar la integridad transaccional.
* **`RF-1.4` Baja Lógica de Cajas:** El sistema no debe permitir la eliminación física de cajas que cuenten con historial transaccional. En su lugar, implementará un estado lógico "Inactivo/Archivado" que la oculte de futuros registros pero preserve su historial para reportes.

### 1.2. Módulo de Registro de Gastos (Egresos) - `RF-2`
* **`RF-2.1` Registro Detallado de Gastos:** El sistema debe permitir guardar egresos individuales registrando obligatoriamente: Monto (positivo, decimal), Fecha (calendario), Categoría de Gasto, Caja de Origen y Descripción (opcional).
* **`RF-2.2` Actualización y Borrado de Gastos:** El sistema debe permitir modificar o eliminar transacciones de gasto. Al hacerlo, reajustará de manera automática y en tiempo real el saldo de la caja de origen afectada.
* **`RF-2.3` Consulta de Historial:** El sistema debe proporcionar una grilla o listado con el historial de gastos, ordenado de forma cronológica descendente, permitiendo filtrar por mes calendario, año, caja de origen y categoría.

### 1.3. Módulo de Registro de Ingresos - `RF-3`
* **`RF-3.1` Registro Detallado de Ingresos:** El sistema debe permitir guardar entradas de dinero individuales registrando obligatoriamente: Monto (positivo, decimal), Fecha (calendario), Fuente de Ingreso, Caja de Destino y Descripción (opcional).
* **`RF-3.2` Actualización y Borrado de Ingresos:** El sistema debe permitir modificar o eliminar transacciones de ingreso, recalculando instantáneamente el saldo de la caja de destino afectada.
* **`RF-3.3` Consulta de Historial:** El sistema debe proveer un listado del historial granular de ingresos con opciones de filtros por período mensual, caja de destino y fuente.

### 1.4. Módulo de Auditoría y Conciliación Mensual - `RF-4`
* **`RF-4.1` Interfaz de Conciliación de Fin de Mes:** Al término de cada mes calendario, el sistema debe proveer una vista donde el usuario introduce el recuento físico real del dinero que posee en cada una de sus cajas.
* **`RF-4.2` Cálculo Automático de Discrepancias:** El sistema debe calcular en tiempo real la diferencia para cada caja mediante la fórmula:
  $$\text{Diferencia} = \text{Saldo Real Declarado} - \text{Saldo Calculado por Sistema}$$
* **`RF-4.3` Generación Automática de Transacciones de Ajuste:** Si el usuario acepta la diferencia calculada en la conciliación:
  * Si la diferencia es negativa, el sistema creará automáticamente un Gasto con la categoría especial "Ajuste por Conciliación".
  * Si la diferencia es positiva, el sistema creará un Ingreso con la fuente especial "Ajuste por Conciliación".
* **`RF-4.4` Bloqueo de Períodos Conciliados (Inmutabilidad):** Una vez que un mes calendario es declarado como "Cerrado", el sistema debe bloquear cualquier operación de inserción, actualización o eliminación de transacciones (ingresos/gastos) cuya fecha pertenezca a dicho período para preservar la validez de las auditorías.

### 1.5. Módulo de Catálogos Dinámicos - `RF-5`
* **`RF-5.1` CRUD de Categorías de Gasto:** El usuario puede crear, ver, modificar y archivar categorías para clasificar egresos (ej. Alimentación, Ocio, Impuestos) asignándoles un color hexadecimal de identificación.
* **`RF-5.2` CRUD de Fuentes de Ingreso:** El usuario puede crear, ver, modificar y archivar fuentes para clasificar entradas (ej. Sueldo, Rendimientos) asignándoles un color hexadecimal.

### 1.6. Tablero Analítico y Reportes (Dashboard) - `RF-6`
* **`RF-6.1` Indicadores Financieros Clave (KPIs):** El Dashboard debe mostrar consolidados los siguientes valores del mes seleccionado:
  * **Ingreso Bruto Mensual:** Suma total de los montos de ingresos cargados.
  * **Ingreso Neto Mensual:** $\text{Ingreso Bruto} - \text{Gasto Total del mes}$.
  * **Ahorro Acumulado:** $\text{Ahorro Histórico Acumulado} + \text{Ingreso Neto del mes}$.
* **`RF-6.2` Comparativa MoM % (Month-over-Month):** El sistema calculará para cada categoría el porcentaje de variación de gasto comparando el mes actual con el mes inmediatamente anterior.
* **`RF-6.3` Promedio Mensual Histórico:** El sistema calculará el gasto promedio mensual acumulado por categoría desde el inicio del registro histórico.
* **`RF-6.4` Top de Gastos:** El sistema listará en orden descendente las 5 transacciones individuales de egreso de mayor monto del mes.
* **`RF-6.5` Gráficos de Evolución Dinámica:** Renderización interactiva de gráficos que expongan la evolución de gastos vs ingresos a lo largo del año.

---

## 2. Requerimientos No Funcionales (RNF)

Los requerimientos no funcionales definen los atributos de calidad, rendimiento y restricciones técnicas bajo los cuales debe operar la solución de software.

### 2.1. Usabilidad y UX - `RNF-1`
* **`RNF-1.1` Interfaz Web Adaptativa (Responsive):** La aplicación construida en **Svelte** debe ser completamente funcional e intuitiva en pantallas de teléfonos móviles (resolución mínima 360px de ancho) y pantallas de computadoras de escritorio.
* **`RNF-1.2` Inmediatez de Captura:** Los formularios rápidos de registro de gastos e ingresos deben estar accesibles a un máximo de 1 clic/toque desde la pantalla de inicio móvil, requiriendo menos de 3 clics en total para guardar la transacción.
* **`RNF-1.3` Visualización Gráfica:** Los gráficos interactivos deben redimensionarse automáticamente y ser legibles en pantallas pequeñas mediante gráficos simplificados (ej. ocultando leyendas largas).

### 2.2. Rendimiento y Concurrencia - `RNF-2`
* **`RNF-2.1` Tiempo de Respuesta de la API:** El backend desarrollado en **FastAPI** debe procesar y responder las peticiones JSON de transacciones en un tiempo menor a 200 milisegundos bajo condiciones normales de red local.
* **`RNF-2.2` Tiempo de Carga de Métricas:** El procesamiento de métricas analíticas complejas (MoM %, promedios, tops) no debe retrasar el renderizado inicial de la página por más de 500 milisegundos en el cliente web.
* **`RNF-2.3` Inicialización Liviana:** Al estar contenedorizado con **Docker**, el sistema completo backend + frontend + base de datos debe inicializarse y estar operativo en menos de 10 segundos tras ejecutar `docker-compose up`.

### 2.3. Confiabilidad e Integridad de Datos - `RNF-3`
* **`RNF-3.1` Integridad Referencial Estricta:** La base de datos **PostgreSQL** debe forzar restricciones FK con la regla `ON DELETE RESTRICT` para evitar la eliminación accidental de categorías, fuentes o cajas que dejen transacciones huérfanas en el historial.
* **`RNF-3.2` Consistencia de Saldos:** El saldo actual de las cajas calculado por el sistema debe coincidir matemáticamente con la suma de saldo inicial + ingresos - egresos. Bajo ninguna condición de error transaccional de red se permitirá la asincronía en este balance.
* **`RNF-3.3` Tolerancia a Fallos Transaccionales:** Los registros de transacciones e incrementos/decrementos de saldos de cajas deben ejecutarse dentro de un bloque transaccional ACID (`BEGIN TRANSACTION` ... `COMMIT`). Si ocurre un fallo en el proceso de actualización del saldo de caja, la inserción del gasto/ingreso debe hacer rollback.

### 2.4. Portabilidad y Despliegue - `RNF-4`
* **`RNF-4.1` Contenerización Homogénea:** El software debe empaquetarse de manera completa y aislada utilizando **Docker Compose**, separando los servicios de Frontend (Svelte en servidor estático), Backend (FastAPI en Uvicorn) y Base de Datos (PostgreSQL v15+).
* **`RNF-4.2` Compatibilidad de Navegadores:** El frontend de Svelte debe ser compatible con las versiones modernas de los navegadores web Google Chrome, Mozilla Firefox, Safari y Microsoft Edge.

### 2.5. Seguridad y Validación - `RNF-5`
* **`RNF-5.1` Validación de Entrada Estricta:** Todas las entradas de datos provenientes del frontend deben validarse de forma estricta tanto en el cliente como en el backend mediante modelos de **Pydantic** para evitar desbordamientos, inyección de scripts (XSS) y SQL Injections.
* **`RNF-5.2` Inmutabilidad Financiera:** La restricción física/lógica de inmutabilidad del historial para períodos en estado "Cerrado" debe validarse forzosamente a nivel del backend en FastAPI, rechazando peticiones HTTP POST/PUT/DELETE que intenten modificar transacciones de meses bloqueados.

---

| Versión | Fecha de Revisión | Autor | Revisor | Cambios Realizados |
| :--- | :--- | :--- | :--- | :--- |
| 0.1.0 | 20-05-2026 | Antigravity | Alejandro | Creación inicial del documento. |
