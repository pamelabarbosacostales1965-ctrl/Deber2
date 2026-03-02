# Banco Fintech – Proyecto Académico

Este proyecto tiene como objetivo construir un **banco fintech** que cumpla
los requisitos funcionales, de arquitectura y de aprendizaje definidos por la cátedra.

---

## 1. Resumen del proyecto

Se desarrolla un banco fintech con las siguientes capacidades:

- Gestión de **clientes** y **cuentas (wallets)**.
- Ejecución de **transacciones**: depósito, retiro y transferencia.
- Aplicación de reglas de negocio configurables:
  - **Comisiones** (`fees`) por tipo de transacción.
  - **Reglas de fraude/riesgo** (límites, prevención de fraude, velocity checks).
- Backend con **FastAPI** y documentación Swagger.
- Frontend con **Streamlit** que consume la API.
- Despliegue mediante **Docker Compose** con PostgreSQL como base de datos.

Se aplican conceptos de SDLC, Git/GitHub, UML, OOP, patrones de diseño (creacionales, Strategy,
Facade), contenedores y arquitectura limpia/hexagonal.

---

## 2. Objetivos de aprendizaje

- Gestionar el proyecto con GitHub Projects (tablero ágil): issues, pull requests y code reviews.
- Diseñar con UML y modelar un dominio usando OOP (encapsulación, invariantes, estados).
- Implementar **arquitectura hexagonal** separando:
  - **Dominio:** entidades y reglas.
  - **Servicios:** casos de uso.
  - **Repositorios:** interfaces (`Protocol`) e implementaciones ORM.
  - **Aplicación:** API y DTOs.
- Aplicar patrones de diseño: creacionales, Strategy y Facade.
- Entregar un sistema completo (API + UI) ejecutable con Docker Compose.

---

## 3. Alcance funcional (MVP)

### 3.1 Entidades de dominio

- `Customer`: id, nombre, email, status.
- `Account`: id, customer_id, currency, balance, status.
- `Transaction`: id, tipo (DEPOSIT/WITHDRAW/TRANSFER), monto, currency, status, created_at.
- `LedgerEntry` (recomendado): id, account_id, transaction_id, dirección (DEBIT/CREDIT), monto.

Se puede trabajar con una sola moneda (USD), aunque debe estar modelada.

### 3.2 Casos de uso requeridos

- Crear cliente.
- Crear cuenta para un cliente.
- Depositar en una cuenta.
- Retirar de una cuenta (validar fondos).
- Transferir entre cuentas (operación atómica).
- Consultar saldo y detalles básicos de cuenta.
- Listar transacciones de una cuenta.

---

## 4. Reglas de negocio obligatorias

### 4.1 Comisiones (`Fees`) – Strategy

Implementar `FeeStrategy` con:

1. `NoFeeStrategy` (0 %).
2. `FlatFeeStrategy` (ej. USD 0.50).
3. `PercentFeeStrategy` (ej. 1.5 % del monto).
4. `TieredFeeStrategy` (monto bajo vs. alto).

Las comisiones se calculan al ejecutar deposit/withdraw/transfer, se reflejan en el ledger o se descuentan.

### 4.2 Reglas de riesgo/fraude – Strategy

`RiskStrategy` con:

- `MaxAmountRule`: límite por monto.
- `VelocityRule`: máximo de transacciones en X minutos.
- `DailyLimitRule`: suma diaria límite.

Si una regla falla, la transacción queda **REJECTED** con mensaje claro.

### 4.3 Estados y transiciones

- `AccountStatus`: ACTIVE / FROZEN / CLOSED.
- `TransactionStatus`: PENDING / APPROVED / REJECTED.

Reglas: no operar con fondos insuficientes o cuentas no activas; transferencias generan débito y crédito consistentes.

---

## 5. Arquitectura requerida (Hexagonal)

- `domain/`: entidades, enums y validaciones.
- `services/`: orquestación de casos de uso.
- `repositories/`: interfaces (`Protocol`) e implementaciones ORM (Postgres).
- `application/`: rutas FastAPI, DTOs Pydantic, Facade.
- `frontend/`: Streamlit que consume la API.

**Facade**: `BankingFacade` es el único punto de entrada desde la API con métodos como
`create_customer()`, `create_account()`, `deposit()`, `withdraw()`, `transfer()`,
`get_account()`, `list_transactions()`.

---

## 6. Patrones de diseño

- **Creacionales**: ejemplo `TransactionFactory` (Factory Method) y `TransferBuilder` o
  `TransactionBuilder` (Builder); documentar la elección.
- **Strategy**: `FeeStrategy` (4 implementaciones) y `RiskStrategy` (3 implementaciones).
- **Facade**: `BankingFacade`.

---

## 7. Backend: API, ORM y DTOs

### 7.1 API (FastAPI)

Endpoints mínimos:

- `POST /customers`
- `POST /accounts`
- `GET /accounts/{account_id}`
- `POST /transactions/deposit`
- `POST /transactions/withdraw`
- `POST /transactions/transfer`
- `GET /accounts/{account_id}/transactions`

DTOs Pydantic separados para request/response; no exponer modelos ORM.

### 7.2 Base de datos y ORM

- PostgreSQL en Docker Compose.
- ORM: SQLAlchemy o SQLModel.
- Opcional: Alembic para migraciones.

Persistir customers, accounts, transactions (y ledger). Repositorios con interfaz e implementación.

---

## 8. Frontend (Streamlit)

Permite crear clientes y cuentas, realizar operaciones, consultar saldo y transacciones.
Muestra errores de reglas (riesgo, insuficiencia de fondos). Consume únicamente la API.

---

## 9. DevOps: Docker Compose

`docker-compose.yml` debe levantar:

- `db` (PostgreSQL).
- Servicios de backend y frontend del proyecto.


