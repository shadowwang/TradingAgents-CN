from typing import Optional, Literal, List

from pydantic import BaseModel

class StockAnalysisInfo(BaseModel):
    stock_code: str
    stock_name: str
    analysis_date: Optional[str] = None
    analysts: Optional[List[str]["market", "social", "news", "fundamentals"]] = None
    research_depth: Optional[int] = 1
    id: str