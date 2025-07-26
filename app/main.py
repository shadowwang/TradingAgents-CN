import uvicorn
from fastapi import FastAPI

# 创建API应用
app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Hello World"}

if __name__ == '__main__':
  uvicorn.run(app, host='0.0.0.0', port=6006, log_level="info", workers=1)