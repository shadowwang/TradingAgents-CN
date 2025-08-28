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
            var ws = new WebSocket("wss://www.trade-aiagent.com");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            ws.onerror = function(error) {
                console.error('WebSocket错误:', error);
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode('连接发生错误')
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

@stock_router.websocket("/ws")
async def websocket_stock_analysis(websocket: WebSocket):
    await websocket.accept()

    try:
        # 接收客户端发送的股票分析信息
        data = await websocket.receive_json()
        stockanalysis_info = StockAnalysisInfo(**data)

        logger.info(f"🔧 开始运行股票分析 (WebSocket): {stockanalysis_info}")

        # 如果stockanalysis_info为空，返回错误：
        if not stockanalysis_info:
            await websocket.send_json({
                'success': False,
                'state': None,
                'decision': None,
            })
            return

        await websocket.send_json({
            'success': True,
            'type': 'result',
            'decision': ""
        })

        # 设置分析参数
        stockanalysis_info.analysts = ["market", "social", "news", "fundamentals"]
        stockanalysis_info.analysis_date = datetime.now().strftime('%Y-%m-%d')

        # 定义WebSocket进度回调
        async def ws_progress_callback(progress: dict):
            await websocket.send_json({
                'success': True,
                'error': 'ok',
                'type': 'progress',
                'data': progress
            })

        # 运行分析并发送结果
        result = stock_service.run_stock_analysis(stockanalysis_info, ws_progress_callback)
        await websocket.send_json({
            'success': True,
            'error': 'ok',
            'type': 'result',
            'decision': result
        })

    except Exception as e:
        logger.error(f"WebSocket股票分析错误: {str(e)}")
        await websocket.send_json({
            'success': False,
            'error': str(e)
        })
    # finally:
    #     await websocket.close()

@stock_router.get("/get_stock_data/{stock_name}")
async def get_stock_data(stock_name: str):
    return stock_service.get_stock_data(stock_name)

@stock_router.get("/get_team_members")
async def get_team_members():
    return stock_service.get_team_members()