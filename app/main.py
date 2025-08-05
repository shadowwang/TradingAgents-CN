import uvicorn
from fastapi import FastAPI

from app.controller.stock_controller import stock_router as stock_router
from tradingagents.utils.stock_validator import get_stock_preparer
# 创建API应用
app = FastAPI()
app.include_router(stock_router, prefix='/v1')

if __name__ == '__main__':
  uvicorn.run(app, host='127.0.0.0', port=6006, log_level="info", workers=1)