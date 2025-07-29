from pydantic import BaseModel

class StockAnalysisInfo(BaseModel):
    stock_code: str
    analysis_date: str
    analysts: str
    research_depth: int