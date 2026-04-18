# app/api/dashboard_routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from ..dashboard import generate_dashboard_html, get_all_dashboards
from ..config import settings

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/generate/{analysis_file}")
def generate_dashboard(analysis_file: str):
    """
    Generate HTML dashboard from analysis JSON file.
    
    Args:
        analysis_file: Name of the analysis JSON file (e.g., 'filename_analysis.json')
    
    Returns:
        Generated dashboard file path
    """
    try:
        analysis_path = os.path.join(settings.OUTPUT_DIR, analysis_file)
        
        if not os.path.exists(analysis_path):
            raise HTTPException(status_code=404, detail="Analysis file not found")
        
        if not analysis_file.endswith('_analysis.json'):
            raise HTTPException(status_code=400, detail="Invalid analysis file")
        
        dashboard_path = generate_dashboard_html(analysis_path)
        
        return {
            "status": "success",
            "dashboard_path": dashboard_path,
            "dashboard_file": os.path.basename(dashboard_path)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view/{dashboard_file}")
def view_dashboard(dashboard_file: str):
    """
    View the generated HTML dashboard.
    
    Args:
        dashboard_file: Name of the dashboard HTML file
    
    Returns:
        HTML file
    """
    try:
        if not dashboard_file.endswith('_dashboard.html'):
            raise HTTPException(status_code=400, detail="Invalid dashboard file")
        
        dashboard_path = os.path.join(settings.OUTPUT_DIR, dashboard_file)
        
        if not os.path.exists(dashboard_path):
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return FileResponse(dashboard_path, media_type="text/html")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
def list_dashboards():
    """
    List all available dashboards.
    
    Returns:
        List of dashboard files with their paths
    """
    try:
        dashboards = get_all_dashboards()
        return {
            "status": "success",
            "count": len(dashboards),
            "dashboards": dashboards
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list-analysis-files")
def list_analysis_files():
    """
    List all analysis JSON files that can be converted to dashboards.
    
    Returns:
        List of analysis JSON files
    """
    try:
        analysis_files = []
        outputs_dir = settings.OUTPUT_DIR
        
        if os.path.exists(outputs_dir):
            for file in os.listdir(outputs_dir):
                if file.endswith('_analysis.json'):
                    analysis_files.append({
                        'name': file,
                        'path': os.path.join(outputs_dir, file)
                    })
        
        return {
            "status": "success",
            "count": len(analysis_files),
            "analysis_files": analysis_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
