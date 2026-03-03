# Game Keys E-commerce Platform (Monorepo)

A professional e-commerce platform for selling digital game keys and licenses. 
The monorepo contains a set of microservices (FastAPI + PostgreSQL) with 
synchronous communication via REST and asynchronous domain events via 
Kafka. An API Gateway verifies JWTs, applies rate limiting, and routes requests.

---

## Table of Contents
- [Demo / Status](#demo--status)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Running Services](#running-services)
- [Testing](#testing)
- [API Conventions](#api-conventions)
- [Domain Events](#domain-events)
- [Security](#security)
- [Monitoring & Logging](#monitoring--logging)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Demo / Status
- Status: active development (v1.0.0).
- Test UI: simple static pages in `frontend/public` allow manual verification of payment flows (`index.html`, `success.html`, `cancel.html`).

## Key Features
- User registration and login (JWT) with roles: user/admin.
- Product catalog with filtering and sorting.
- Inventory and license keys lifecycle: available → reserved → assigned.
- Cart and order management; statuses: awaiting_payment, paid, failed, cancelled.
- Mock payments (Stripe-like): create transaction, simulated callback success/failure.
- Notifications (email/Discord) for key milestones.
- Sales reports: daily/monthly, top products, JSON/CSV export.

## Architecture
Microservices communicate via REST (synchronous) and a message broker Kafka for domain events. The Nginx gateway:
- verifies JWTs,
- adds `X-User-Id` and `X-User-Role` headers,
- enforces rate limiting,
- routes traffic to services.

Core events:
- `user_registered`, 
- `order_created`, 
- `order_paid`, 
- `order_failed`, 
- `order_cancelled`, 
- `product_created`, 
- `product_updated`.

## Repository Structure
```
/
├── services/
│   ├── auth/
│   ├── product-catalog/
│   ├── inventory/
│   ├── order/
│   ├── payment/
│   ├── notification/
│   ├── reporting/
│   └── api_gateway/
├── frontend/
├── dev/
└── infrastructure/
```

Each service (pattern):
```
service-name/
├── app/
│   ├── core/
│   ├── repositories/
│   ├── models/
│   ├── routes/
│   ├── middlewares/
│   ├── events/
│   │   ├── publishers/
│   │   └── subscribers/
│   ├── config/
│   └── index.ts
├── tests/
├── alembic/
├── Dockerfile
├── pyproject.toml
├── alembic.ini
└── docker-compose.yml
```

Note: All services are implemented in Python (FastAPI). The directory layout is kept consistent with the above pattern.

## Tech Stack
- Backend: Python, FastAPI
- Database: PostgreSQL (optional MongoDB for Reporting)
- Message Broker: Kafka
- Authentication: JWT (verified at the Gateway)
- ORM/DB: SQLAlchemy/Alembic (per service), validation with Pydantic
- Infrastructure: Nginx (API Gateway), Docker/Compose

## Requirements
- Python 3.13+
- Docker and Docker Compose (recommended for local development)
- PostgreSQL 14+ (if running services locally without Docker)
- Message broker Kafka for async events

## Quick Start
1. Clone the repository.
2. Configure environment variables for each service (via `.env`). Example:
   ```env
   NODE_ENV=development
   PORT=3000
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   JWT_SECRET=your-secret-key
   MESSAGE_BROKER_URL=amqp://localhost:5672
   GATEWAY_URL=http://localhost:8080
   ```
3. Start dependencies (PostgreSQL, RabbitMQ/Kafka, Nginx) locally or with containers.
4. Start selected services (see below).

## Environment Configuration
- Each service ships its own `docker-compose.yml` and DB migrations (`alembic`).
- Keep secrets (e.g., `JWT_SECRET`) in environment variables.
- The Gateway verifies JWT and forwards user context in headers; downstream microservices must not verify JWTs themselves.

## Running Services
Two typical modes:

- Docker Compose (recommended): from a service directory
  ```bash
  docker compose up --build
  ```

- Local (dev):
  ```bash
  # install dependencies (poetry or pip, depending on service)
  poetry install
  # run DB migrations
  alembic upgrade head
  # start API
  uvicorn app.core.main:app --reload --port 3000
  ```

Health checks: `GET /health` — every service should expose a health endpoint.

## Testing
- Unit: service logic and helpers.
- Integration: API endpoints and database operations.
- E2E: critical flows (order creation, payment).
- Events: publishing and subscription via the broker.

Run (example):
```bash
pytest -q
```

## API Conventions
- REST, JSON, statuses: 200/201/400/401/403/404/500.
- Error format: `{ "error": string, "message": string, "statusCode": number }`.
- User context: `X-User-Id`, `X-User-Role` headers added by the Gateway.
- Admin-only operations: check `X-User-Role === 'admin'` inside the service.

Login via Gateway (example):
```http
POST /login
{
  "email": "user@example.com",
  "password": "secret"
}
```
The frontend stores the returned JWT and includes it as `Authorization: Bearer <JWT>`.

## Domain Events
Event schema:
```ts
interface Event {
  eventId: string;
  eventType: string;
  timestamp: Date;
  payload: Record<string, any>;
}
```

Published events:
- `user_registered`: { userId, email }
- `order_created`: { orderId, userId, totalAmount, items }
- `order_paid`: { orderId, userId, paymentId, keys }
- `order_failed`: { orderId, userId, reason }
- `order_cancelled`: { orderId, userId }
- `product_created`: { productId, name, price }
- `product_updated`: { productId, changes }

## Security
- Passwords hashed with bcrypt (≥10 rounds).
- JWT secret stored in environment variables.
- Input validation on all endpoints.
- Rate limiting at the Gateway.
- Idempotency for event handling; retries + DLQ for failures.

## Monitoring & Logging
- Centralized logging (e.g., Python standard logging or Pino/Winston) with request correlation.
- Track service metrics and latency; monitor the message broker.

## Roadmap
- [ ] Integrate Redis for product catalog caching
- [ ] Admin dashboard
- [ ] E2E test suite leveraging dockerized services

## Contributing
Contributions are welcome. Before you start:
- Review the architecture and conventions in this README.
- Add tests for new/changed code.
- Keep code style and directory structure consistent with existing services.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

### Contact
- Author/Maintainer: BNBG
- Bug reports: GitHub Issues
