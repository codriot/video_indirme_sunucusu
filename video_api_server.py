from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import os
import uuid
import time
from pydantic import BaseModel, HttpUrl
import uvicorn
import shutil

# Video indirme fonksiyonlarımızı içe aktaralım
from video_downloader import download_youtube_video, download_twitter_video, download_instagram_video, detect_platform, create_download_dir

app = FastAPI(
    title="Video İndirme API",
    description="YouTube, Twitter ve Instagram videolarını indirmenize olanak sağlayan API",
    version="1.0.0"
)

# İndirilen videoların bilgilerini tutmak için bir sözlük
download_tasks = {}

# İstek için data modeli
class VideoDownloadRequest(BaseModel):
    url: HttpUrl
    quality: Optional[str] = "high"  # high, medium, low

# İndirme durumu için data modeli
class DownloadStatus(BaseModel):
    task_id: str
    status: str
    platform: Optional[str] = None
    download_path: Optional[str] = None
    percentage: Optional[float] = None
    error: Optional[str] = None

# Download klasörü
DOWNLOAD_DIR = create_download_dir()

def background_download(task_id: str, url: str, quality: str):
    """Arka planda video indirme işlemini gerçekleştirir"""
    try:
        platform = detect_platform(url)
        if not platform:
            download_tasks[task_id] = {
                "status": "failed",
                "error": "Desteklenmeyen URL formatı"
            }
            return
        
        download_tasks[task_id]["platform"] = platform
        download_tasks[task_id]["status"] = "downloading"
        
        # Platform türüne göre indirme işlemini başlat
        success = False
        if platform == "youtube":
            success = download_youtube_video(url, DOWNLOAD_DIR)
        elif platform == "twitter":
            success = download_twitter_video(url, DOWNLOAD_DIR)
        elif platform == "instagram":
            success = download_instagram_video(url, DOWNLOAD_DIR)
        
        if success:
            # İndirilen son dosyayı bul
            files = [f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f)) and f.endswith((".mp4", ".webm", ".mkv"))]
            if files:
                # Son eklenen dosyayı bul
                latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(DOWNLOAD_DIR, f)))
                download_path = os.path.join(DOWNLOAD_DIR, latest_file)
                download_tasks[task_id]["download_path"] = download_path
                download_tasks[task_id]["status"] = "completed"
            else:
                download_tasks[task_id]["status"] = "failed"
                download_tasks[task_id]["error"] = "Video indirildi ama dosya bulunamadı"
        else:
            download_tasks[task_id]["status"] = "failed"
            download_tasks[task_id]["error"] = "Video indirme işlemi başarısız oldu"
    
    except Exception as e:
        download_tasks[task_id]["status"] = "failed"
        download_tasks[task_id]["error"] = str(e)

@app.get("/")
def read_root():
    return {"message": "Video İndirme API'ye Hoş Geldiniz", "version": "1.0.0"}

@app.post("/download/", response_model=DownloadStatus)
async def download_video(background_tasks: BackgroundTasks, request: VideoDownloadRequest):
    """
    Video indirme işlemi başlatır ve bir task ID döndürür.
    Bu ID ile indirme durumunu sorgulayabilirsiniz.
    """
    task_id = str(uuid.uuid4())
    download_tasks[task_id] = {
        "status": "pending",
        "platform": None,
        "download_path": None,
        "percentage": 0,
        "error": None
    }
    
    # Arka planda indirme işlemini başlat
    background_tasks.add_task(background_download, task_id, str(request.url), request.quality)
    
    return DownloadStatus(
        task_id=task_id,
        status="pending"
    )

@app.get("/status/{task_id}", response_model=DownloadStatus)
async def check_status(task_id: str):
    """İndirme işleminin durumunu kontrol eder"""
    if task_id not in download_tasks:
        raise HTTPException(status_code=404, detail="Task bulunamadı")
    
    task_info = download_tasks[task_id]
    return DownloadStatus(
        task_id=task_id,
        status=task_info["status"],
        platform=task_info["platform"],
        download_path=task_info["download_path"],
        percentage=task_info.get("percentage", None),
        error=task_info.get("error", None)
    )

@app.get("/video/{task_id}")
async def get_video(task_id: str):
    """Tamamlanan video dosyasını indirir"""
    if task_id not in download_tasks:
        raise HTTPException(status_code=404, detail="Task bulunamadı")
    
    task_info = download_tasks[task_id]
    
    if task_info["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Video henüz hazır değil. Mevcut durum: {task_info['status']}")
    
    if not task_info["download_path"] or not os.path.exists(task_info["download_path"]):
        raise HTTPException(status_code=404, detail="Video dosyası bulunamadı")
    
    return FileResponse(
        path=task_info["download_path"],
        filename=os.path.basename(task_info["download_path"]),
        media_type="video/mp4"  # Çoğu video için bu MIME türü çalışacaktır
    )

@app.get("/videos/")
async def list_videos():
    """İndirilen tüm videoları listeler"""
    videos = []
    try:
        files = [f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f)) and f.endswith((".mp4", ".webm", ".mkv"))]
        
        for file in files:
            file_path = os.path.join(DOWNLOAD_DIR, file)
            file_size = os.path.getsize(file_path)
            videos.append({
                "filename": file,
                "size_bytes": file_size,
                "created_at": time.ctime(os.path.getctime(file_path))
            })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    return {"videos": videos, "count": len(videos)}

@app.delete("/videos/{filename}")
async def delete_video(filename: str):
    """Belirli bir videoyu siler"""
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video dosyası bulunamadı")
    
    try:
        os.remove(file_path)
        return {"message": f"{filename} başarıyla silindi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video silinirken hata oluştu: {str(e)}")

# API'yi başlatmak için main bloğu
if __name__ == "__main__":
    print(f"Video İndirme API başlatılıyor... İndirme klasörü: {DOWNLOAD_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=8000)