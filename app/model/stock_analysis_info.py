from typing import Optional

from pydantic import BaseModel

class StockAnalysisInfo(BaseModel):
    stock_code: str
    stock_name: str
    analysis_date: Optional[str] = None
    analysts: Optional[str] = None
    research_depth: Optional[int] = None
    id: str