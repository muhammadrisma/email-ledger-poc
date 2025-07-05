from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class TransactionResponse(BaseModel):
    id: int
    email_id: str
    email_subject: str
    email_sender: str
    email_date: datetime
    amount: Optional[float]
    currency: str
    vendor: str
    transaction_type: str
    reference_id: str
    description: str
    category: str
    processed_at: datetime
    is_processed: bool
    
    class Config:
        from_attributes = True

class SummaryResponse(BaseModel):
    total_transactions: int
    total_amount: float
    category_breakdown: Dict[str, int]

class ProcessingResponse(BaseModel):
    processed_count: int
    successful_extractions: int
    timestamp: str

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    vendor: Optional[str] = None
    transaction_type: Optional[str] = None
    reference_id: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str 