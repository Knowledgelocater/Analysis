# app/tasks.py
import os
import uuid
import pandas as pd
from celery import Celery
from .config import settings
from .analysis import run_analysis
from .ai import call_groq_for_insights
from .dashboard import generate_dashboard_html
from .services.email_service import email_service

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
def process_file(file_path: str, user_email: str = None):
    try:
        print(f"[Celery] Processing file: {file_path}")

        # 1) Data analysis
        analysis_result = run_analysis(file_path)
        if "error" in analysis_result:
            return {"status": "error", "error": analysis_result["error"]}

        analysis_path = analysis_result["analysis_path"]

        # 2) Generate Dashboard
        try:
            dashboard_path = generate_dashboard_html(analysis_path)
            print(f"[Celery] Dashboard generated: {dashboard_path}")
        except Exception as e:
            print(f"[Celery] Dashboard generation failed: {str(e)}")
            dashboard_path = None

        # 3) AI Insights (Groq)
        ai_result = call_groq_for_insights(analysis_path)

        # AI Error
        if "error" in ai_result:
            result = {
                "status": "success",
                "analysis_path": analysis_path,
                "dashboard_path": dashboard_path,
                "insights_error": ai_result["error"]
            }
        else:
            # AI Success
            result = {
                "status": "success",
                "analysis_path": analysis_path,
                "dashboard_path": dashboard_path,
                "insights_path": ai_result["insights_path"],
                "insights": ai_result["insights"]
            }

        # 4) Send email if user_email provided and email enabled
        if user_email and settings.ENABLE_EMAIL and settings.SENDER_EMAIL:
            send_dashboard_email.delay(
                user_email=user_email,
                file_name=os.path.basename(file_path),
                dashboard_path=dashboard_path,
                analysis_path=analysis_path
            )
            result["email_status"] = "queued"

        return result

    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.tasks.send_dashboard_email")
def send_dashboard_email(user_email: str, file_name: str, dashboard_path: str, analysis_path: str):
    """
    Send dashboard and analysis to user via email.
    """
    try:
        print(f"[Celery] Sending email to {user_email}")
        
        if not dashboard_path or not os.path.exists(dashboard_path):
            print(f"[Celery] Dashboard file not found: {dashboard_path}")
            return {"status": "error", "error": "Dashboard file not found"}
        
        success = email_service.send_dashboard_email(
            recipient_email=user_email,
            file_name=file_name,
            dashboard_path=dashboard_path,
            analysis_path=analysis_path
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Email sent to {user_email}",
                "recipient": user_email
            }
        else:
            return {
                "status": "error",
                "message": "Failed to send email",
                "recipient": user_email
            }
    
    except Exception as e:
        print(f"[Celery] Email task failed: {str(e)}")
        return {"status": "error", "error": str(e)}
