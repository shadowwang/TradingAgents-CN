from fastapi import APIRouter

from app.model.stock_analysis_info import StockAnalysisInfo
from app.services.stock_service import StockService
from tradingagents.utils.stock_validator import get_stock_preparer

stock_router = APIRouter()
stock_service = StockService()

@stock_router.post("/stock_analysis/")
def run_stock_analysis(stockanalysis_info: StockAnalysisInfo):
    return stock_service.run_stock_analysis(stockanalysis_info)

@stock_router.get("/get_stock_data/{stock_code}")
def get_stock_data(stock_code: str):
  return stock_service.get_stock_data(stock_code)
