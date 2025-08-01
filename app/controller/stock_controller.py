from typing import List, Dict, Any

from fastapi import APIRouter
from starlette.websockets import WebSocketDisconnect, WebSocket

from app.manager.websocket_manager import manager
from app.model.stock_analysis_info import StockAnalysisInfo
from app.services.stock_service import StockService
from tradingagents.utils.stock_validator import get_stock_preparer

stock_router = APIRouter()
stock_service = StockService()

@stock_router.post("/stock_analysis/")
async def run_stock_analysis(stockanalysis_info: StockAnalysisInfo):
    return stock_service.run_stock_analysis(stockanalysis_info, progress_callback)

@stock_router.get("/get_stock_data/{stock_code}", response_model=List[Dict[str, Any]])
def get_stock_data(stock_name: str):
  return stock_service.get_stock_data(stock_name)

"""
const socket = new WebSocket('ws://your-server-address/ws/progress');

socket.onmessage = (event) => {
    console.log('Progress update:', event.data);
};
"""
@stock_router.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接开放
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def progress_callback(message: str, step: int = None, total_steps: int = None):
    await manager.broadcast(message)