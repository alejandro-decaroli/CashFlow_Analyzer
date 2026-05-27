Título: Minuta de Reunión y Acuerdos Iniciales
Autor: Antigravity (IA Analyst)
Fecha de Última Actualización: Miércoles, 20 de mayo de 2026
Versión: 0.1.0

# Minuta de Reunión: Sistema de Finanzas Personales y Control de Cajas

## 1. Información General de la Sesión
* **Fecha:** Miércoles, 20 de mayo de 2026
* **Participantes:** 
  * Alejandro (Dueño del Problema / Cliente)
  * Antigravity (Senior Systems Analyst / IA Analyst)
* **Objetivo:** Analizar el flujo actual de finanzas en Excel, documentar puntos de dolor, definir requerimientos para una nueva solución de software y establecer acuerdos iniciales de diseño.

---

## 2. Contexto del Proceso Actual (As-Is)
Alejandro gestiona las finanzas de su hogar utilizando una planilla de cálculo de Excel estructurada de la siguiente manera:
1. **Registro de Gastos:** Una tabla donde registra los egresos mensuales organizados por categorías.
2. **Registro de Ingresos:** Una tabla donde registra los ingresos mensuales por fuentes.
3. **Métricas de Control Mensual:** 
   * **Ingreso Bruto Mensual:** Suma total de los ingresos del mes.
   * **Ingreso Neto Mensual:** Calculado como la diferencia real de balance entre los ingresos brutos y los gastos del período.
   * **Ahorro Acumulado:** Suma del ingreso neto del mes actual más el ahorro consolidado del mes anterior.
4. **Visualización:** Gráficos sencillos para observar la evolución mensual de costos e ingresos.
5. **Control de "Cajas" (Cuentas/Bancos):** Alejandro utiliza una tabla para llevar el balance de sus "cajas" (ej. efectivo, banco "Santa Fe", etc.). Los ingresos se depositan en una caja específica y los gastos se debitan de otra.
6. **Auditoría y Conciliación:** Al final de cada mes calendario, Alejandro realiza un recuento físico/digital del dinero real en cada caja y lo compara con el saldo registrado en su planilla Excel para verificar que coincidan (auditoría).

---

## 3. Puntos de Dolor Identificados
* **Operación Tediosa:** El registro manual de gastos e ingresos en Excel resulta aburrido, repetitivo y propenso a errores de captura, lo que desalienta la constancia en el control financiero.
* **Limitación Analítica:** Dificultad para extraer valor y patrones avanzados de los datos históricos. La visualización en Excel es rígida y cuesta responder preguntas clave como:
  * ¿Cuánto varió el gasto en una categoría de un mes a otro en términos de porcentaje (MoM %)?
  * ¿Cuál es el promedio histórico de gasto por categoría?
  * ¿Cuáles son las transacciones que representan el "Top de Gastos" del mes?
* **Rastreo de Cajas:** El balance y la conciliación mensual de cajas se torna complejo al no existir un historial transaccional enlazado directamente con los flujos de dinero de cada cuenta.

---

## 4. Acuerdos y Decisiones de Diseño (To-Be)
Se tomaron las siguientes decisiones de diseño para el desarrollo de los artefactos de análisis del nuevo sistema de software:

* **4.1. Definición Matemática Consolidada:**
  Se establece que los cálculos financieros se regirán por las siguientes fórmulas estándares:
  $$\text{Ingreso Neto} = \text{Ingreso Bruto} - \text{Gasto Total}$$
  $$\text{Ahorro Acumulado} = \text{Ahorro del Mes Anterior} + \text{Ingreso Neto del Mes Actual}$$

* **4.2. Enfoque Tecnológico y Accesibilidad:**
  El sistema se diseñará como una **Aplicación Web Adaptativa (Responsive)**. Esto permitirá a Alejandro registrar gastos e ingresos al instante desde su teléfono móvil y, simultáneamente, analizar visualmente sus datos mediante gráficos avanzados en su computadora.

* **4.3. Gestión Dinámica y CRUD Completo:**
  El sistema será dinámico. El usuario tendrá autonomía total para crear, modificar y eliminar:
  * Categorías de gastos.
  * Fuentes de ingresos.
  * Cajas (Cuentas/Bancos).
  * Transacciones de gastos e ingresos.

* **4.4. Historial Transaccional Detallado:**
  Se mantendrá un registro granular histórico tanto de gastos como de ingresos. Cada transacción guardará de forma obligatoria:
  * Fecha de la transacción.
  * Monto.
  * Categoría de Gasto o Fuente de Ingreso.
  * Caja afectada (origen/destino del dinero).

* **4.5. Período de Cierre y Conciliación:**
  El período financiero coincidirá con el **mes calendario**. Al finalizar el mes, el sistema proporcionará un módulo de conciliación para contrastar el saldo calculado por el sistema para cada caja con el saldo real reportado por el usuario.

---

## 5. Próximos Pasos
1. Diseñar la **Visión del Sistema** detallando alcance, limitaciones y restricciones físicas/lógicas.
2. Elaborar la **Lista de Casos de Uso** estructurados.
3. Modelar el **Dominio del Sistema** (Entidades y relaciones).
4. Generar el **Esquema de Base de Datos** físico y relacional para garantizar la persistencia de las transacciones y las cajas.

---

| Versión | Fecha de Revisión | Autor | Revisor | Cambios Realizados |
| :--- | :--- | :--- | :--- | :--- |
| 0.1.0 | 20-05-2026 | Antigravity | Alejandro | Creación inicial del documento. |
