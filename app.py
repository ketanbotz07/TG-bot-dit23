from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from video_processor import process_video
import uuid, os, threading

app = FastAPI()
progress = {}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # Ensure input/output folders exist
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Create unique task ID and file paths
    task_id = str(uuid.uuid4())
    input_path = f"input/{task_id}.mp4"
    output_path = f"output/{task_id}_final.mp4"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Initialize progress
    progress[task_id] = 0

    # Run video processing in background thread
    def bg():
        process_video(input_path, output_path, task_id, progress)
        progress[task_id] = 100

    threading.Thread(target=bg, daemon=True).start()
    return {"task_id": task_id, "status": "processing"}


@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    return {"progress": progress.get(task_id, 0)}


@app.get("/download/{task_id}")
async def download_video(task_id: str):
    path = f"output/{task_id}_final.mp4"
    return FileResponse(path, media_type="video/mp4", filename="final.mp4")
