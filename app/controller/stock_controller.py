from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.manager.websocket_manager import manager
from app.model.stock_analysis_info import StockAnalysisInfo
from app.services.stock_service import StockService, logger

stock_router = APIRouter()
stock_service = StockService()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("wss://www.trade-aiagent.com/v1/progress");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

from fastapi.responses import HTMLResponse
@stock_router.get("/")
async def get():
    return HTMLResponse(html)

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
    stockanalysis_info.analysts = ["market", "social", "news", "fundamentals"];
    stockanalysis_info.analysis_date = datetime.now().strftime('%Y-%m-%d');
    return stock_service.run_stock_analysis(stockanalysis_info, progress_callback)

@stock_router.get("/get_stock_data/{stock_name}")
async def get_stock_data(stock_name: str):
    return stock_service.get_stock_data(stock_name)

@stock_router.get("/get_team_members")
async def get_team_members():
    return stock_service.get_team_members()

@stock_router.websocket("/progress")
async def websocket_progress(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接开放
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def progress_callback(message: str, step: int = None, total_steps: int = None):
    await manager.broadcast(message)