# app/main.py
import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .tasks import process_file
from celery.result import AsyncResult
import shutil

app = FastAPI(title="Auto Analysis Backend")
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <body>
            <h2>Upload Excel File</h2>
            <form action="/api/upload" enctype="multipart/form-data" method="post">
                <input name="file" type="file" accept=".xlsx,.xls" />
                <button type="submit">Upload</button>
            </form>
        </body>
    </html>
    """



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ensure directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

@app.post("/api/upload")
async def upload_excel(file: UploadFile = File(...)):
    # Basic validation
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx or .xls files supported")
    # Save file to disk
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    save_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # enqueue background task
    job = process_file.delay(save_path)
    return {"job_id": job.id, "file_id": file_id, "filename": filename}

@app.get("/api/status/{job_id}")
def job_status(job_id: str):
    res = AsyncResult(job_id, app=process_file._get_app())
    data = {"job_id": job_id, "state": res.state}
    if res.state == "PENDING":
        data["message"] = "Queued or not started"
    elif res.state == "STARTED":
        data["message"] = "Processing"
    elif res.state == "SUCCESS":
        data["message"] = "Completed"
        data["result"] = res.result  # dict returned by task
    elif res.state == "FAILURE":
        data["message"] = str(res.result)
    else:
        data["message"] = str(res.result)
    return JSONResponse(content=data)

@app.get("/api/result/file")
def get_file(path: str):
    # security: prevent path traversal
    base = os.path.abspath(settings.OUTPUT_DIR)
    requested = os.path.abspath(path)
    if not requested.startswith(base):
        raise HTTPException(status_code=403, detail="Forbidden")
    if not os.path.exists(requested):
        raise HTTPException(status_code=404, detail="Not found")
    # return file
    return FileResponse(requested, media_type="application/json", filename=os.path.basename(requested))
