Título: Lista de Casos de Uso
Autor: Antigravity (IA Analyst)
Fecha de Última Actualización: Miércoles, 20 de mayo de 2026
Versión: 0.1.0

# Especificación de Casos de Uso: CashFlow Personal Analyzer (CPA)

Este documento detalla los Casos de Uso (CU) del sistema, describiendo cómo el usuario interactúa con la aplicación para gestionar sus finanzas y realizar la auditoría de cajas.

---

## 1. Mapa de Casos de Uso

```mermaid
usecaseDiagram
    actor Alejandro as "Alejandro (Administrador)"

    Alejandro --> CU01 : "Administrar Cajas (CRUD)"
    Alejandro --> CU02 : "Registrar Gasto (Historial)"
    Alejandro --> CU03 : "Registrar Ingreso (Historial)"
    Alejandro --> CU04 : "Conciliar Balance de Cajas"
    Alejandro --> CU05 : "Visualizar Tablero Analítico"
    Alejandro --> CU06 : "Administrar Catálogos (CRUD)"
```

---

## 2. Detalle de Casos de Uso

### CU-01: Administrar Cajas (Cuentas/Bancos)
* **Actor Principal:** Alejandro.
* **Descripción:** Permite crear, visualizar, modificar o dar de baja las "cajas" (cuentas, bancos o efectivo físico) desde las cuales se gestiona el dinero.
* **Precondiciones:** El usuario ha iniciado sesión en la aplicación web.
* **Flujo Principal:**
  1. El usuario navega a la sección "Mis Cajas/Cuentas".
  2. El sistema muestra la lista de cajas existentes, indicando nombre, tipo y saldo calculado actual.
  3. El usuario selecciona "Crear Nueva Caja".
  4. El usuario completa el formulario: Nombre de la caja (ej. Banco Santa Fe, Efectivo Bolsillo), Tipo (Banco, Efectivo, Tarjeta) y Saldo Inicial.
  5. El usuario guarda los cambios.
  6. El sistema valida los datos (nombre único, saldo inicial numérico mayor o igual a 0).
  7. El sistema almacena la nueva caja y actualiza la lista en pantalla mostrando el saldo inicial como saldo actual.
* **Flujos Alternativos:**
  * **4.a. Modificar Caja:** El usuario puede seleccionar una caja existente y cambiar su nombre o tipo. No se permite modificar directamente el saldo actual desde esta sección para preservar la trazabilidad histórica.
  * **4.b. Dar de Baja (Eliminar) Caja:** El usuario solicita eliminar una caja. Si la caja contiene transacciones históricas asociadas (gastos o ingresos), el sistema bloquea la eliminación física y sugiere archivar/inactivar la caja para evitar la pérdida de integridad referencial histórica.
* **Postcondiciones:** La caja queda registrada y disponible para asociarle egresos e ingresos.

---

### CU-02: Registrar Gasto (Historial granular)
* **Actor Principal:** Alejandro.
* **Descripción:** Permite registrar un egreso individual, deduciéndolo de una caja específica y asociándolo a una categoría.
* **Precondiciones:** Debe existir al menos una Caja registrada y una Categoría de Gasto configurada.
* **Flujo Principal:**
  1. El usuario pulsa el botón rápido "Registrar Gasto" (disponible desde la barra de accesos rápidos).
  2. El sistema despliega el formulario de registro de egreso.
  3. El usuario completa los campos:
     * **Monto:** Valor decimal mayor a 0.
     * **Fecha:** Por defecto la fecha actual, modificable mediante calendario.
     * **Categoría:** Selección de una lista desplegable (ej. Comida, Alquiler, Servicios).
     * **Caja de Origen:** Selección de la caja desde donde saldrá el dinero.
     * **Descripción/Nota:** Texto opcional.
  4. El usuario confirma el registro.
  5. El sistema valida que los campos requeridos estén completos y correctos.
  6. El sistema almacena el gasto en el historial de transacciones.
  7. El sistema debita automáticamente el monto del gasto del saldo actual de la **Caja de Origen** seleccionada.
  8. El sistema muestra un mensaje de confirmación de registro exitoso.
* **Flujos Alternativos:**
  * **5.a. Saldo de Caja Insuficiente:** Si el monto del gasto es mayor al saldo actual de la Caja de Origen seleccionada:
    1. El sistema muestra una alerta de advertencia: *"Esta transacción dejará la caja en saldo negativo. ¿Deseas continuar?"*.
    2. Si el usuario confirma, el sistema registra la transacción y calcula el saldo negativo correspondiente.
    3. Si el usuario cancela, se retorna al formulario sin alterar los saldos.
* **Postcondiciones:** El gasto queda almacenado con fecha y hora, y el saldo de la caja de origen se reduce.

---

### CU-03: Registrar Ingreso (Historial granular)
* **Actor Principal:** Alejandro.
* **Descripción:** Permite registrar un ingreso de dinero individual, sumándolo a una caja específica y asociándolo a una fuente.
* **Precondiciones:** Debe existir al menos una Caja registrada y una Fuente de Ingreso configurada.
* **Flujo Principal:**
  1. El usuario pulsa el botón rápido "Registrar Ingreso".
  2. El sistema despliega el formulario de registro de ingreso.
  3. El usuario completa los campos:
     * **Monto:** Valor decimal mayor a 0.
     * **Fecha:** Por defecto la fecha actual, modificable mediante calendario.
     * **Fuente:** Selección de una lista desplegable (ej. Sueldo, Freelance, Rendimientos).
     * **Caja de Destino:** Selección de la caja donde ingresará el dinero.
     * **Descripción/Nota:** Texto opcional.
  4. El usuario confirma el registro.
  5. El sistema valida los datos ingresados.
  6. El sistema almacena el ingreso en el historial de transacciones.
  7. El sistema incrementa automáticamente el monto del ingreso en el saldo actual de la **Caja de Destino** seleccionada.
  8. El sistema muestra un mensaje de confirmación exitoso.
* **Postcondiciones:** El ingreso queda almacenado en el historial, y el saldo de la caja de destino se incrementa.

---

### CU-04: Conciliar Balance de Cajas (Auditoría de Fin de Mes)
* **Actor Principal:** Alejandro.
* **Descripción:** Permite auditar y ajustar los saldos calculados por el sistema de cada caja contra el recuento real de dinero físico y bancario al cierre del mes calendario.
* **Precondiciones:** El usuario está al finalizar o iniciar un mes y desea realizar la reconciliación del período anterior.
* **Flujo Principal:**
  1. El usuario ingresa al módulo de "Conciliación Mensual".
  2. El sistema presenta una tabla detallando:
     * Lista de Cajas activas.
     * Saldo Calculado por el Sistema en la fecha de cierre.
     * Campo vacío de "Saldo Real Físico/Bancario".
  3. El usuario cuenta su dinero físico y revisa sus cuentas bancarias, e introduce en la columna "Saldo Real" el monto correspondiente a cada caja.
  4. El sistema calcula dinámicamente la discrepancia para cada caja en tiempo real:
     $$\text{Diferencia} = \text{Saldo Real} - \text{Saldo Calculado}$$
  5. Si todas las diferencias son igual a $0.00$, el sistema muestra el estado "Conciliado Exitosamente".
  6. El usuario hace clic en "Cerrar Período".
  7. El sistema almacena el estado de conciliación del mes y bloquea las transacciones de ese período para evitar ediciones accidentales.
* **Flujos Alternativos:**
  * **4.a. Existencia de Discrepancias (Diferencia $\neq 0$):**
    1. Si una caja presenta diferencia negativa (ej. faltante de efectivo de -$10.00$) o positiva (ej. sobrante de $5.00$):
    2. El sistema resalta el registro en rojo/amarillo y habilita la opción: "Crear Ajuste Automático".
    3. Si el usuario acepta, el sistema genera automáticamente un **Gasto de Ajuste** (para faltantes) o un **Ingreso de Ajuste** (para sobrantes) con la descripción "Ajuste por Conciliación Mensual - [Nombre Caja]" para forzar a que el saldo del sistema coincida con el saldo real.
    4. El usuario confirma y el período se cierra con balance equilibrado.
* **Postcondiciones:** Se guarda un histórico de conciliaciones y el saldo del sistema se ajusta para reflejar la realidad física de las cajas.

---

### CU-05: Visualizar Tablero Analítico y Métricas (Dashboard)
* **Actor Principal:** Alejandro.
* **Descripción:** Muestra los resultados agregados de las finanzas del mes seleccionado y tendencias históricas en base al registro transaccional.
* **Precondiciones:** Existen transacciones registradas en el sistema.
* **Flujo Principal:**
  1. El usuario accede a la pantalla de "Dashboard".
  2. Por defecto, el sistema muestra la información del mes calendario actual.
  3. El sistema procesa y renderiza los siguientes widgets dinámicos:
     * **Métricas Principales:**
       * **Ingreso Bruto Mensual:** Suma de ingresos del mes actual.
       * **Ingreso Neto Mensual:** $\text{Ingreso Bruto} - \text{Gasto Total}$.
       * **Ahorro Acumulado:** $\text{Ahorro Histórico Anterior} + \text{Ingreso Neto Actual}$.
     * **Comparación MoM % (Month over Month) por Categoría:** Una tabla o listado interactivo que compara los gastos del mes actual con el anterior para cada categoría, mostrando la variación porcentual (ej. *"Comida: +12% respecto al mes anterior"*).
     * **Promedio de Gasto Mensual:** Cálculo promedio histórico acumulado para cada categoría de egreso.
     * **Top Gastos Mensuales:** Ranking ordenado descendentemente con los 5 o 10 gastos individuales más altos del mes.
     * **Gráfico de Evolución Temporal:** Gráfico interactivo de barras apiladas o líneas mostrando la evolución de costos totales vs ingresos totales a lo largo de los últimos 6 o 12 meses.
  4. El usuario puede cambiar el filtro de mes/año para auditar períodos históricos.
* **Postcondiciones:** Visualización clara de estadísticas e indicadores de rendimiento financiero.

---

### CU-06: Administrar Catálogos (CRUD de Categorías e Ingresos)
* **Actor Principal:** Alejandro.
* **Descripción:** Permite configurar las opciones disponibles para clasificar gastos e ingresos (Categorías y Fuentes de Ingresos).
* **Precondiciones:** El usuario ha iniciado sesión.
* **Flujo Principal:**
  1. El usuario navega a "Configuración > Catálogos".
  2. El usuario selecciona la pestaña "Categorías de Gasto" o "Fuentes de Ingreso".
  3. El sistema muestra los ítems existentes en formato de lista interactiva.
  4. El usuario puede:
     * **Crear Nuevo Ítem:** Completa nombre, descripción y opcionalmente un color identificativo. El sistema valida que no exista un duplicado y lo agrega.
     * **Modificar Ítem:** Edita el nombre o propiedades de la categoría. Las transacciones históricas se vinculan automáticamente al nombre actualizado.
     * **Eliminar Ítem:** Si la categoría o fuente tiene transacciones históricas enlazadas, el sistema advierte que eliminarlas afectaría el reporte analítico y ofrece la opción de "Fusionar con otra Categoría" o "Archivar/Ocultar" para registros futuros sin destruir datos antiguos.
* **Postcondiciones:** Los catálogos quedan actualizados para su uso inmediato en los formularios de registro de transacciones.

---

| Versión | Fecha de Revisión | Autor | Revisor | Cambios Realizados |
| :--- | :--- | :--- | :--- | :--- |
| 0.1.0 | 20-05-2026 | Antigravity | Alejandro | Creación inicial del documento. |
