from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ActiveAutomationOut(BaseModel):
    id: int
    automation_id: int
    name: str
    description: Optional[str] = None
    tokens_remaining: int = 0
    demo_tokens: int = 0
    integration_status: Optional[str] = None
    created_at: datetime

class PaymentOut(BaseModel):
    id: int
    automation_id: Optional[int] = None
    amount: int
    tokens_purchased: int
    gateway: str
    method: Optional[str] = None
    transaction_id: Optional[str] = None
    ref_id: Optional[str] = None
    status: str
    created_at: datetime

class PaymentListOut(BaseModel):
    total: int
    items: List[PaymentOut]

class MonthExpense(BaseModel):
    month: str   # "YYYY-MM"
    amount: int  # total paid that month (successful payments)

class MonthlyExpensesOut(BaseModel):
    points: List[MonthExpense]

class PaymentReceiptOut(BaseModel):
    id: int
    amount: int
    tokens_purchased: int
    status: str
    gateway: str
    method: Optional[str]
    transaction_id: Optional[str]
    ref_id: Optional[str]
    automation_id: Optional[int]
    created_at: datetime
