import os
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, init_db
from models.customer import Customer
from services.ingestion import IngestionService

app = FastAPI(
    title="Customer Pipeline Service",
    description="Data pipeline service for customer data ingestion and retrieval",
    version="1.0.0"
)


class IngestResponse(BaseModel):
    status: str
    records_processed: int


class CustomerResponse(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    account_balance: float
    created_at: Optional[str] = None


class PaginatedCustomersResponse(BaseModel):
    data: list
    total: int
    page: int
    limit: int


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/api/health", methods=['GET'])
def health_check():
    return {"status": "healthy"}


@app.post("/api/ingest", response_model=IngestResponse)
def ingest_customers(db: Session = Depends(get_db)):
    try:
        ingestion_service = IngestionService()
        customers_data = ingestion_service.fetch_all_customers_from_api()
        
        if not customers_data:
            return IngestResponse(status="success", records_processed=0)
        
        records_processed = ingestion_service.ingest_customers(db, customers_data)
        
        return IngestResponse(status="success", records_processed=records_processed)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers", response_model=PaginatedCustomersResponse)
def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(Customer).count()
    
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()
    
    return PaginatedCustomersResponse(
        data=[customer.to_dict() for customer in customers],
        total=total,
        page=page,
        limit=limit
    )


@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
def get_customer_by_id(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer.to_dict()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
