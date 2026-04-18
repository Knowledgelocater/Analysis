# app/main.py
import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
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
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 100px auto;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                }
                .container {
                    background: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                h2 {
                    color: #667eea;
                    text-align: center;
                }
                form {
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }
                input[type="email"], input[type="file"] {
                    padding: 10px;
                    border: 2px solid #667eea;
                    border-radius: 5px;
                    font-size: 14px;
                }
                input[type="email"]:focus, input[type="file"]:focus {
                    outline: none;
                    border-color: #764ba2;
                    box-shadow: 0 0 5px rgba(102, 126, 234, 0.5);
                }
                button {
                    padding: 12px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                button:hover {
                    transform: scale(1.02);
                }
                .info {
                    background: #f0f4ff;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #667eea;
                    font-size: 13px;
                    color: #333;
                    margin-top: 20px;
                }
                .info h4 {
                    margin: 0 0 10px 0;
                    color: #667eea;
                }
                .info ul {
                    margin: 0;
                    padding-left: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📊 Upload Excel File for Analysis</h2>
                <form action="/api/upload" enctype="multipart/form-data" method="post">
                    <div>
                        <label for="email" style="font-weight: bold; color: #333;">📧 Your Email Address:</label>
                        <input 
                            id="email"
                            name="email" 
                            type="email" 
                            placeholder="your@email.com"
                            required
                            style="width: 100%; box-sizing: border-box;"
                        />
                    </div>
                    
                    <div>
                        <label for="file" style="font-weight: bold; color: #333;">📁 Select Excel File:</label>
                        <input 
                            id="file"
                            name="file" 
                            type="file" 
                            accept=".xlsx,.xls"
                            required
                            style="width: 100%; box-sizing: border-box;"
                        />
                    </div>
                    
                    <button type="submit">🚀 Upload & Analyze</button>
                </form>
                
                <div class="info">
                    <h4>✨ What happens after upload:</h4>
                    <ul>
                        <li>📊 Your file is analyzed for statistical insights</li>
                        <li>📈 Interactive dashboard is generated</li>
                        <li>🤖 AI insights are extracted (if API key configured)</li>
                        <li>📧 Dashboard is sent to your email (if email is configured)</li>
                    </ul>
                </div>
            </div>
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
async def upload_excel(file: UploadFile = File(...), email: str = Form(...)):
    # Basic validation
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx or .xls files supported")
    
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email address required")
    
    # Save file to disk
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    save_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # enqueue background task with email
    job = process_file.delay(save_path, user_email=email)
    return {
        "job_id": job.id, 
        "file_id": file_id, 
        "filename": filename,
        "email": email,
        "message": "File uploaded. Processing started. Dashboard will be emailed to you when ready."
    }

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
