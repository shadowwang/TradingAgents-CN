import uvicorn
from fastapi import FastAPI

from tradingagents.utils.stock_validator import get_stock_preparer
# 创建API应用
app = FastAPI()

@app.get("/v1/get_stock_data/{stock_code}")
async def get_stock_data(stock_code: str):
  preparer = get_stock_preparer()
  result = preparer.prepare_stock_data(stock_code)
  return result

if __name__ == '__main__':
  uvicorn.run(app, host='0.0.0.0', port=6006, log_level="info", workers=1)