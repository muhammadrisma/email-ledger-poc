from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..db.models import get_db, FinancialTransaction
from ..services.ledger_service import LedgerService
from ..core.processor import EmailLedgerProcessor
from ..schema import (
    TransactionResponse, 
    SummaryResponse, 
    ProcessingResponse, 
    TransactionUpdate,
    HealthResponse
)

router = APIRouter()

ledger_service = LedgerService()
processor = EmailLedgerProcessor()

@router.get("/", response_model=dict)
async def root():
    """
    Root endpoint.
    
    Returns basic API information and version.
    """
    return {"message": "Email Ledger API", "version": "1.0.0"}

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get all transactions with pagination.
    
    Args:
        limit: Maximum number of transactions to return (1-1000)
        offset: Number of transactions to skip
        db: Database session
        
    Returns:
        List of transaction objects
    """
    transactions = ledger_service.get_transactions(db, limit=limit, offset=offset)
    return transactions

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific transaction by ID.
    
    Args:
        transaction_id: ID of the transaction to retrieve
        db: Database session
        
    Returns:
        Transaction object or 404 if not found
    """
    transaction = db.query(FinancialTransaction).filter(
        FinancialTransaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction

@router.get("/transactions/category/{category}", response_model=List[TransactionResponse])
async def get_transactions_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    """
    Get transactions by category.
    
    Args:
        category: Expense category to filter by
        db: Database session
        
    Returns:
        List of transactions in the specified category
    """
    transactions = ledger_service.get_transactions_by_category(db, category)
    return transactions

@router.get("/summary", response_model=SummaryResponse)
async def get_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics.
    
    Returns total transactions, total amount, and category breakdown.
    
    Args:
        db: Database session
        
    Returns:
        Summary statistics object
    """
    return ledger_service.get_summary_stats(db)

@router.post("/process-emails", response_model=ProcessingResponse)
async def process_emails():
    """
    Trigger email processing.
    
    Initiates the email processing pipeline to extract financial
    data from unprocessed emails.
    
    Returns:
        Processing result with statistics
    """
    try:
        result = processor.process_emails()
        return ProcessingResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a transaction.
    
    Args:
        transaction_id: ID of the transaction to delete
        db: Database session
        
    Returns:
        Success message or 404 if transaction not found
    """
    success = ledger_service.delete_transaction(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    updates: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a transaction.
    
    Args:
        transaction_id: ID of the transaction to update
        updates: Transaction update data
        db: Database session
        
    Returns:
        Updated transaction object or 404 if not found
    """
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    transaction = ledger_service.update_transaction(db, transaction_id, update_dict)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns API health status and current timestamp.
    
    Returns:
        Health status object
    """
    return HealthResponse(
        status="healthy", 
        timestamp=datetime.utcnow().isoformat()
    ) 