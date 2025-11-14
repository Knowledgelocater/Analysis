# app/tasks.py
import os
import uuid
import pandas as pd
from celery import Celery
from .config import settings
from .analysis import run_analysis
from .ai import call_groq_for_insights

# -------------------------------------------
# 1) INIT CELERY APP  (must be before @task)
# -------------------------------------------
celery_app = Celery(
    "auto_analysis",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"]
)

# -------------------------------------------
# 2) DEFINE TASK
# -------------------------------------------
@celery_app.task(name="app.tasks.process_file")
def process_file(file_path: str):
    try:
        print(f"[Celery] Processing file: {file_path}")

        # 1) Data analysis
        analysis_result = run_analysis(file_path)
        if "error" in analysis_result:
            return {"status": "error", "error": analysis_result["error"]}

        analysis_path = analysis_result["analysis_path"]

        # 2) AI Insights (Groq)
        ai_result = call_groq_for_insights(analysis_path)

        # AI Error
        if "error" in ai_result:
            return {
                "status": "success",
                "analysis_path": analysis_path,
                "insights_error": ai_result["error"]
            }

        # AI Success
        return {
            "status": "success",
            "analysis_path": analysis_path,
            "insights_path": ai_result["insights_path"],
            "insights": ai_result["insights"]
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}
