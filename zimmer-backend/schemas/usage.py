from typing import List, Optional
from pydantic import BaseModel

class WeeklyPoint(BaseModel):
    day: str          # e.g., "2025-09-01"
    tokens: int = 0
    sessions: int = 0

class MonthlyPoint(BaseModel):
    month: str        # e.g., "2025-05"
    value: int = 0    # total tokens in that month

class DistributionPoint(BaseModel):
    name: str         # automation name (or "Unknown")
    value: int = 0    # tokens total

class UsageWeeklyOut(BaseModel):
    points: List[WeeklyPoint]

class UsageMonthlyOut(BaseModel):
    points: List[MonthlyPoint]

class UsageDistributionOut(BaseModel):
    points: List[DistributionPoint]
