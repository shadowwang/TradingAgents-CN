from http.client import HTTPException
from typing import List, Dict, Any

from fastapi import APIRouter
from starlette.websockets import WebSocketDisconnect, WebSocket

from app.manager.websocket_manager import manager
from app.model.stock_analysis_info import StockAnalysisInfo
from app.services.stock_service import StockService, logger
from tradingagents.utils.stock_validator import get_stock_preparer

stock_router = APIRouter()
stock_service = StockService()

@stock_router.post("/stock_analysis")
async def run_stock_analysis(stockanalysis_info: StockAnalysisInfo):
    logger.info(f"🔧 开始运行股票分析: {stockanalysis_info}")
    # 如果stockanalysis_info为空，返回错误：
    if not stockanalysis_info:
        return {
            'success': False,
            'state': None,
            'decision': None,
        }
    return stock_service.run_stock_analysis(stockanalysis_info, progress_callback)

@stock_router.get("/get_stock_data/{stock_name}")
async def get_stock_data(stock_name: str):
    return stock_service.get_stock_data(stock_name)

@stock_router.get("/get_team_members")
async def get_team_members():
    return stock_service.get_team_members()

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