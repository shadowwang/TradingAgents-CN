from pydantic import BaseModel

class StockAnalysisInfo(BaseModel):
    stock_code: str
    stock_name: str
    analysis_date: str
    analysts: str
    research_depth: int
    id: int