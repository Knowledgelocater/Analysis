# Dashboard Feature - Usage Guide

## Overview
The dashboard generator creates interactive HTML dashboards from your analysis JSON files. It visualizes all the statistical features generated during data analysis.

## Files Created
- **`app/dashboard.py`** - Dashboard generator module
- **`app/api/dashboard_routes.py`** - API endpoints for dashboard management

## Features Displayed in Dashboard

### 1. **Key Metrics** (Top Section)
- Total Rows: Number of records in the dataset
- Total Columns: Number of features
- Numeric Columns: Count of numeric/quantitative columns
- Categorical Columns: Count of categorical/qualitative columns

### 2. **Numeric Columns Tab** 📈
For each numeric column, displays:
- **Mean**: Average value
- **Std Dev**: Standard deviation (variability)
- **Min/Max**: Minimum and maximum values
- **Non-Null Count**: Number of non-missing values
- **Null Count**: Number of missing values

### 3. **Categorical Columns Tab** 📋
For each categorical column, displays:
- **Unique Values**: Count of distinct values
- **Non-Null Count**: Number of non-missing values
- **Null Count**: Number of missing values
- **Top Values**: Most frequent categories with their counts

### 4. **Correlations Tab** 🔗
Shows top 10 correlations between numeric columns:
- **Column A & B**: Which columns are correlated
- **Correlation Value**: Strength (-1 to 1)
- **Strength Level**: Weak/Moderate/Strong classification

### 5. **Sample Data Tab** 📝
Displays first 5 rows of your dataset in a table format.

---

## How to Use

### Option 1: Via Python Script
```python
from app.dashboard import generate_dashboard_html

# Generate dashboard from analysis file
dashboard_path = generate_dashboard_html('outputs/filename_analysis.json')
print(f"Dashboard created: {dashboard_path}")

# Open in browser (Windows)
import os
os.startfile(dashboard_path)
```

### Option 2: Via API Endpoints

#### 1. List all analysis files
```bash
GET http://localhost:8000/dashboard/list-analysis-files
```

#### 2. Generate dashboard from analysis file
```bash
POST http://localhost:8000/dashboard/generate/{filename}_analysis.json

Example:
POST http://localhost:8000/dashboard/generate/a89ba270-5f5b-400b-b9de-cb255ee4cc77_CovidDeaths_analysis.json
```

#### 3. View generated dashboard
```bash
GET http://localhost:8000/dashboard/view/{filename}_dashboard.html

Example:
GET http://localhost:8000/dashboard/view/a89ba270-5f5b-400b-b9de-cb255ee4cc77_CovidDeaths_dashboard.html
```

#### 4. List all generated dashboards
```bash
GET http://localhost:8000/dashboard/list
```

---

## Example Workflow

1. **Upload file via API** → Creates `filename_analysis.json`
2. **Generate dashboard**:
   ```bash
   POST http://localhost:8000/dashboard/generate/filename_analysis.json
   ```
3. **View in browser**:
   ```bash
   GET http://localhost:8000/dashboard/view/filename_dashboard.html
   ```

---

## Dashboard Output Files

Generated dashboards are stored in: `outputs/`

Files named: `{original_filename}_dashboard.html`

Example:
```
outputs/
├── CovidDeaths_analysis.json
├── CovidDeaths_dashboard.html      ← Interactive dashboard
├── CovidDeaths_insights.json
└── CovidDeaths_insights.html
```

---

## Features

✅ Responsive design - works on desktop and mobile
✅ Interactive tabs - switch between different analyses
✅ Beautiful UI with gradient styling
✅ Tabular display of all statistics
✅ Fast loading - pure HTML/JavaScript (no backend calls)
✅ Copy-friendly - easily share HTML file

---

## To Enable in FastAPI (Optional)

Add this to your `app/main.py`:

```python
from app.api.dashboard_routes import router as dashboard_router

app.include_router(dashboard_router)
```

Then restart your FastAPI server:
```bash
python -m uvicorn app.main:app --reload
```

---

## Example Output

The generated HTML dashboard includes:
- 4 tab sections for different analyses
- Beautiful gradient styling with purple theme
- Fully responsive table layouts
- Hover effects on rows
- Sortable metrics
