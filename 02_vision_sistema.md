Título: Visión del Sistema
Autor: Antigravity (IA Analyst)
Fecha de Última Actualización: Miércoles, 20 de mayo de 2026
Versión: 0.1.1

# Documento de Visión del Sistema: CashFlow Personal Analyzer (CPA)

## 1. Introducción
El presente documento describe la visión, el alcance, los objetivos y las restricciones de la aplicación **CashFlow Personal Analyzer (CPA)**. Este sistema nace para resolver las ineficiencias operativas y las limitaciones analíticas que Alejandro experimenta en la gestión diaria de las finanzas y el balance de cajas de su hogar utilizando planillas de Excel.

---

## 2. Declaración del Problema y Oportunidad

### 2.1. Declaración del Problema
| Elemento | Descripción |
| :--- | :--- |
| **El problema de...** | El registro repetitivo, aburrido y rígido de gastos e ingresos, junto al control ineficiente de múltiples cuentas físicas y bancarias. |
| **Afecta a...** | Alejandro y el control financiero diario de su hogar. |
| **El impacto es...** | Desmotivación para mantener actualizadas las finanzas, falta de visibilidad en tiempo real de saldos reales de cajas y dificultad para realizar análisis profundos sobre dónde se consume el dinero de mes a mes. |
| **Una solución exitosa sería...** | Una aplicación web responsive, ágil e intuitiva, que simplifique el registro inmediato de transacciones asociadas a cuentas/cajas concretas y automatice el cálculo de métricas complejas, tendencias de ahorro y procesos de conciliación mensual. |

---

## 3. Propósito y Objetivos del Sistema

### 3.1. Propósito General
Proporcionar a Alejandro una plataforma centralizada, intuitiva y accesible desde cualquier dispositivo móvil o de escritorio que facilite el registro continuo de flujos de efectivo (ingresos y gastos), permita gestionar de forma precisa los saldos de sus diversas "cajas" (cuentas bancarias, efectivo, tarjetas) y le brinde analíticas avanzadas para tomar decisiones financieras informadas de forma ágil.

### 3.2. Objetivos de Negocio (KPIs del Sistema)
* **Reducir el tiempo de registro:** Disminuir en más de un 60% el tiempo dedicado a registrar transacciones individuales en comparación con el proceso actual en Excel.
* **Consistencia de Cajas:** Lograr el 100% de precisión matemática en el cálculo del saldo consolidado e individual por caja.
* **Transparencia Analítica:** Automatizar la generación de reportes clave como el Top de Gastos y el incremento porcentual mes a mes (MoM %) por categoría sin requerir fórmulas complejas del usuario.

---

## 4. Alcance del Sistema (Scope)

### 4.1. Características Incluidas (In-Scope)
* **Módulo de Transacciones Detalladas:**
  * Registro histórico granular de Gastos (Monto, Fecha, Categoría, Caja de origen).
  * Registro histórico granular de Ingresos (Monto, Fecha, Fuente, Caja de destino).
  * CRUD completo (Crear, Leer, Actualizar, Eliminar) para todos los movimientos registrados.
* **Módulo de Cajas / Cuentas:**
  * CRUD completo de Cajas (ej. Efectivo, Banco Santa Fe, Tarjeta de Débito).
  * Cálculo dinámico y acumulado del saldo en tiempo real para cada Caja.
* **Módulo de Auditoría y Conciliación:**
  * Interfaz de cierre mensual donde el usuario introduce el recuento de dinero real/físico de cada caja.
  * Comparación automatizada contra el saldo del sistema e informe detallado de discrepancias (sobrantes/faltantes).
* **Módulo de Configuración Dinámica:**
  * CRUD de Categorías de Gasto.
  * CRUD de Fuentes de Ingreso.
* **Tablero de Control Analítico (Dashboard):**
  * Cálculo y visualización de: Ingreso Bruto, Ingreso Neto (Ingreso Bruto - Gasto Total) y Ahorro Acumulado (Ahorro del Mes Anterior + Ingreso Neto).
  * Variación porcentual de gastos categoría por categoría de un mes a otro (MoM %).
  * Promedio de gasto mensual histórico por categoría.
  * Ranking "Top de Gastos" mensuales ordenados por monto decreciente.
  * Gráficos dinámicos e interactivos de evolución temporal de costos e ingresos.

### 4.2. Características Excluidas (Out-of-Scope)
* **Integración Bancaria Automatizada:** El sistema no consumirá APIs directas de entidades bancarias para extraer transacciones; todo registro se mantendrá de forma manual/asistida por el usuario para garantizar simplicidad y privacidad.
* **Gestión Multiusuario / Permisos de Roles:** El sistema está diseñado estrictamente para un único usuario administrador (Alejandro). No se contempla soporte para múltiples cuentas independientes o jerarquías complejas.
* **Predicciones Financieras mediante IA avanzada:** No se realizarán proyecciones algorítmicas de mercado o recomendaciones de inversión automáticas en esta fase.

---

## 5. Perfil de Usuario
El sistema contará con un único actor principal:

### 5.1. Alejandro (Administrador Financiero del Hogar)
* **Rol:** Propietario de la información, encargado del registro diario, mantenimiento de catálogos (categorías, fuentes, cajas) y auditor del balance de cuentas.
* **Nivel Técnico:** Técnico-medio. Desea prescindir de la rigidez de las fórmulas de Excel, valorando una experiencia móvil optimizada, fluida y con datos consolidados automáticamente.

---

## 6. Restricciones y Requisitos Tecnológicos

### 6.1. Restricciones de Diseño e Interfaz
* **Diseño Web Adaptativo (Responsive):** La interfaz de usuario debe estar completamente optimizada para smartphones (para registro rápido en la marcha) y pantallas de escritorio (para análisis profundo en el dashboard).
* **Usabilidad e Inmediatez:** La acción de registrar un nuevo gasto/ingreso debe tomar menos de 3 clics desde la pantalla de inicio móvil.

### 6.2. Restricciones Tecnológicas
* **Arquitectura de Software:** Aplicación Web de una sola página (SPA) o Web App moderna basada en componentes, permitiendo transiciones y actualizaciones fluidas sin recargas completas.
* **Persistencia de Datos:** Base de datos relacional que garantice la integridad referencial (por ejemplo, evitar que se elimine una Caja si existen gastos asociados a ella sin su correspondiente reasignación).
* **Sincronización:** El mes financiero estará atado estrictamente al mes calendario (del día 1 al último día de cada mes).

### 6.3. Stack Tecnológico Seleccionado
Para satisfacer la modularidad, velocidad analítica y portabilidad responsive requeridas, el sistema se construirá sobre el siguiente stack:
* **Frontend:** **Svelte** (compilador JS ultra-ligero y reactivo, que asegura interfaces web rápidas y de excelente performance en dispositivos móviles de cualquier gama).
* **Backend:** **Python con FastAPI** (framework asíncrono de alto rendimiento, ideal para exponer endpoints rápidos, tipado estricto de datos con Pydantic y documentación interactiva automática con Swagger).
* **Base de Datos:** **PostgreSQL** (motor de base de datos relacional robusto, idóneo para asegurar la integridad referencial transaccional mediante llaves foráneas y optimizar búsquedas temporales a través de índices físicos).
* **Contenedores / Despliegue:** **Docker** (para empaquetar de forma homogénea tanto el backend, la base de datos como el servidor de frontend, facilitando despliegues locales idénticos a los de producción).

---

## 7. Supuestos y Dependencias
* Se asume que Alejandro cuenta con conexión a internet en sus dispositivos para acceder al sistema, aunque se valorará la capacidad de almacenamiento local para resiliencia offline.
* Los saldos iniciales de las cajas serán introducidos manualmente por Alejandro al momento de configurar el sistema por primera vez para asegurar una base de cálculo correcta.

---

| Versión | Fecha de Revisión | Autor | Revisor | Cambios Realizados |
| :--- | :--- | :--- | :--- | :--- |
| 0.1.0 | 20-05-2026 | Antigravity | Alejandro | Creación inicial del documento. |
| 0.1.1 | 20-05-2026 | Antigravity | Alejandro | Definición detallada del stack tecnológico del proyecto (Svelte, FastAPI, PostgreSQL, Docker). |

