from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from main import VideoProcessor

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = VideoProcessor()

@app.post("/api/process-video")
async def process_video(file: UploadFile = File(...)):
    try:
        # 保存上传的视频文件
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 处理视频
        result = processor.process_video(temp_file_path)
        
        # 读取字幕文件内容
        with open(result['subtitle'], 'r', encoding='utf-8') as f:
            subtitles = f.read()
        
        # 清理临时文件
        os.unlink(temp_file_path)
        if os.path.exists(result['audio']):
            os.unlink(result['audio'])
        if os.path.exists(result['subtitle']):
            os.unlink(result['subtitle'])
        
        return {"subtitles": subtitles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)