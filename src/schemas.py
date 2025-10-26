from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class TransactionIn(BaseModel):
    transaction_id: str
    date: Optional[str]
    type: Optional[str]
    amount: float
    category: Optional[str]
    merchant: Optional[str]
    location: Optional[str]
    balance_after: Optional[float]

class AnalyzeRequest(BaseModel):
    user_id: Optional[int] = None
    user_profile: Optional[dict] = None   # you can pass partial profile
    transactions: Optional[List[TransactionIn]] = None

class AnalyzeResponse(BaseModel):
    summary: str
    recommendations: List[str]

class RecommendRequest(BaseModel):
    user_id: Optional[int] = None
    context: Optional[dict] = None

class RecommendResponse(BaseModel):
    products: List[dict]  # e.g. [{"name": "...", "rationale": "...", "estimated_return": "..."}]