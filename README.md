# AutoAnalysis Backend

Automated Excel Data Analysis + AI Insights (FastAPI + Celery + Redis + Pandas + Groq)

AutoAnalysis lets users upload Excel files and automatically generates:
- Statistical analysis
- Data profiling
- Correlation insights
- AI-powered recommendations
- Downloadable JSON reports

It automates work usually done in Power BI / Tableau, enabling instant analysis with AI.

## Features
- Excel Upload API
- Background Processing (Celery + Redis)
- Automatic Data Profiling
- Correlation Matrix
- Top values & numerical statistics
- AI Insights via Groq (OpenAI-compatible endpoint)
- Downloadable JSON reports
- FastAPI web interface for local testing

## Tech Stack
Backend
- Python 3.12
- FastAPI, Uvicorn
- Asynchronous processing
- Celery + Redis

Data processing
- Pandas, NumPy, openpyxl

AI integration
- Groq API (Mixtral / LLaMA models)
- OpenAI-compatible ChatCompletions API

Configuration
- pydantic-settings (.env support)

## Project Structure
autoAnalysis/
```
│── app/
│   ├── main.py          # FastAPI entry
│   ├── tasks.py         # Celery worker tasks
│   ├── analysis.py      # Excel -> Data summary
│   ├── ai.py            # AI insights via Groq
│   ├── config.py        # Environment config
│   └── groq_test.py     # Simple Groq test tool
│── uploads/             # Uploaded Excel files
│── outputs/             # Generated reports
│── requirements.txt
│── .env
```

## Setup Instructions
1. Clone
    cd autoAnalysis

2. Create venv
    python -m venv venv
    venv\Scripts\activate   # Windows

3. Install
    pip install -r requirements.txt

4. Configure
    Copy `.env.example` to `.env` and set:
    ```
    REDIS_URL=redis://localhost:6379/0
    GROQ_API_KEY=your_api_key_here
    GROQ_MODEL=gpt-4o-mini
    UPLOAD_DIR=uploads
    OUTPUT_DIR=outputs
    ```

## Running the Backend
1. Start Redis
    redis-server

2. Start Celery worker
    celery -A app.tasks.celery_app worker --loglevel=info --pool=solo

3. Run FastAPI
    uvicorn app.main:app --reload

API base: http://127.0.0.1:8000

## API Endpoints
- POST /api/upload  
  Accepts .xlsx / .xls, returns job_id.

- GET /api/status/{job_id}  
  Status values: PENDING, STARTED, SUCCESS, FAILURE

- GET /api/result/file?path=<output_path>  
  Downloads *_analysis.json and *_insights.json

## How It Works
- Excel → Pandas
  - Row/column counts
  - Null value summary
  - Unique values
  - Numerical stats (mean, median, std, min, max)
  - Categorical top values
  - Correlation insights
  - Sample rows

- AI layer
  - Sends compact summary to Groq AI
  - Receives key insights, recommendations, data quality warnings
  - All outputs saved as JSON

## Roadmap
- React frontend dashboard
- CSV and SQL support
- Automated PDF report generation
- Real-time charts API
- Authentication / user accounts

## Contributing
PRs, issues, and ideas are welcome.

## License
MIT © 2025 Kinshuk Shukla