# Customer Data Pipeline System

A production-ready Dockerized data pipeline system with Flask mock server, FastAPI pipeline service, and PostgreSQL database.

## Architecture

- **Flask Mock Server** (Port 5000): Serves customer data from JSON file
- **FastAPI Pipeline Service** (Port 8000): Ingests data from Flask API and stores in PostgreSQL
- **PostgreSQL Database** (Port 5432): Stores customer records

## Project Structure

```
project-root/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── database.py
    ├── models/customer.py
    ├── services/ingestion.py
    ├── Dockerfile
    └── requirements.txt
```

## Prerequisites

- Docker
- Docker Compose

## Setup & Running

1. Build and start all services:
```bash
docker-compose up --build
```

2. Check service health:
```bash
curl http://localhost:5000/api/health
curl http://localhost:8000/api/health
```

## API Endpoints

### Flask Mock Server

#### Get paginated customers
```bash
curl http://localhost:5000/api/customers?page=1&limit=5
```

#### Get single customer by ID
```bash
curl http://localhost:5000/api/customers/1
```

#### Health check
```bash
curl http://localhost:5000/api/health
```

### FastAPI Pipeline Service

#### Ingest customers from Flask API
```bash
curl -X POST http://localhost:8000/api/ingest
```

#### Get paginated customers from database
```bash
curl http://localhost:8000/api/customers?page=1&limit=5
```

#### Get single customer by ID
```bash
curl http://localhost:8000/api/customers/1
```

#### Health check
```bash
curl http://localhost:8000/api/health
```

## Test Commands

Run these commands in order to test the complete pipeline:

```bash
# 1. Check Flask mock server health
curl http://localhost:5000/api/health

# 2. Get customers from Flask API (paginated)
curl http://localhost:5000/api/customers?page=1&limit=5

# 3. Ingest data into PostgreSQL via FastAPI
curl -X POST http://localhost:8000/api/ingest

# 4. Get customers from FastAPI (from database)
curl http://localhost:8000/api/customers?page=1&limit=5

# 5. Get specific customer from FastAPI
curl http://localhost:8000/api/customers/1
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:password@postgres:5432/customer_db`)

## Stopping Services

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```
