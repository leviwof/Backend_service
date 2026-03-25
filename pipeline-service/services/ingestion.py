import requests
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.customer import Customer


class IngestionService:
    def __init__(self, mock_api_url: str = "http://mock-server:5000"):
        self.mock_api_url = mock_api_url
    
    def fetch_all_customers_from_api(self) -> List[Dict[str, Any]]:
        all_customers = []
        page = 1
        limit = 100
        
        while True:
            try:
                response = requests.get(
                    f"{self.mock_api_url}/api/customers",
                    params={"page": page, "limit": limit},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                customers = data.get("data", [])
                if not customers:
                    break
                    
                all_customers.extend(customers)
                
                total = data.get("total", 0)
                if page * limit >= total:
                    break
                    
                page += 1
                
            except requests.exceptions.RequestException as e:
                raise Exception(f"Failed to fetch customers from API: {str(e)}")
            except (KeyError, ValueError) as e:
                raise Exception(f"Invalid response format from API: {str(e)}")
        
        return all_customers
    
    def parse_date(self, date_str: Optional[str]) -> Optional[date]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    
    def parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        if not datetime_str:
            return None
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    def ingest_customers(self, db: Session, customers_data: List[Dict[str, Any]]) -> int:
        records_processed = 0
        
        for customer_data in customers_data:
            customer_id = customer_data.get("customer_id")
            if not customer_id:
                continue
            
            existing_customer = db.query(Customer).filter(
                Customer.customer_id == customer_id
            ).first()
            
            if existing_customer:
                existing_customer.first_name = customer_data.get("first_name")
                existing_customer.last_name = customer_data.get("last_name")
                existing_customer.email = customer_data.get("email")
                existing_customer.phone = customer_data.get("phone")
                existing_customer.address = customer_data.get("address")
                existing_customer.date_of_birth = self.parse_date(
                    customer_data.get("date_of_birth")
                )
                existing_customer.account_balance = customer_data.get("account_balance", 0.0)
            else:
                new_customer = Customer(
                    customer_id=customer_id,
                    first_name=customer_data.get("first_name"),
                    last_name=customer_data.get("last_name"),
                    email=customer_data.get("email"),
                    phone=customer_data.get("phone"),
                    address=customer_data.get("address"),
                    date_of_birth=self.parse_date(customer_data.get("date_of_birth")),
                    account_balance=customer_data.get("account_balance", 0.0),
                    created_at=self.parse_datetime(customer_data.get("created_at"))
                )
                db.add(new_customer)
            
            records_processed += 1
        
        db.commit()
        return records_processed
