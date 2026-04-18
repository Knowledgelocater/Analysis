# app/dashboard.py
import json
import os
from typing import Dict, Any
from .config import settings


def generate_dashboard_html(analysis_json_path: str) -> str:
    """
    Generate an interactive HTML dashboard from analysis JSON.
    
    Args:
        analysis_json_path: Path to the _analysis.json file
        
    Returns:
        Path to the generated HTML dashboard
    """
    
    # Read the analysis JSON
    with open(analysis_json_path, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    profile = analysis_data.get('profile', {})
    correlations = analysis_data.get('correlations', [])
    sample_rows = analysis_data.get('sample_rows', [])
    
    # Extract key metrics
    total_rows = profile.get('rows', 0)
    total_cols = profile.get('cols', 0)
    columns_info = profile.get('columns', [])
    
    # Prepare column statistics for visualization
    numeric_cols = []
    categorical_cols = []
    
    for col in columns_info:
        if 'mean' in col and col['mean'] is not None:
            numeric_cols.append({
                'name': col['name'],
                'mean': col.get('mean'),
                'min': col.get('min'),
                'max': col.get('max'),
                'std': col.get('std'),
                'non_null': col.get('non_null_count'),
                'null': col.get('null_count')
            })
        else:
            categorical_cols.append({
                'name': col['name'],
                'unique': col.get('unique'),
                'non_null': col.get('non_null_count'),
                'null': col.get('null_count'),
                'top_values': col.get('top_values', {})
            })
    
    # Convert to JSON for JavaScript
    numeric_cols_json = json.dumps(numeric_cols)
    categorical_cols_json = json.dumps(categorical_cols)
    correlations_json = json.dumps(correlations)
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .metric-box {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-right: 20px;
            margin-bottom: 15px;
            min-width: 200px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
        }}
        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
        }}
        .table-container {{
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background-color: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .header {{
            color: white;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        .tab-buttons {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            padding: 10px 20px;
            background: #e0e7ff;
            border: 2px solid #667eea;
            color: #667eea;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }}
        .tab-btn.active {{
            background: #667eea;
            color: white;
        }}
        .tab-btn:hover {{
            background: #667eea;
            color: white;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>📊 Data Analysis Dashboard</h1>
            <p>Interactive analysis of your uploaded dataset</p>
        </div>
        
        <!-- Key Metrics -->
        <div class="card">
            <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 20px;">Key Metrics</h2>
            <div style="display: flex; flex-wrap: wrap;">
                <div class="metric-box">
                    <div class="metric-label">Total Rows</div>
                    <div class="metric-value">{total_rows:,}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Total Columns</div>
                    <div class="metric-value">{total_cols}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Numeric Columns</div>
                    <div class="metric-value">{len(numeric_cols)}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Categorical Columns</div>
                    <div class="metric-value">{len(categorical_cols)}</div>
                </div>
            </div>
        </div>
        
        <!-- Tabs -->
        <div class="tab-buttons">
            <button class="tab-btn active" onclick="switchTab('numeric')">📈 Numeric Columns</button>
            <button class="tab-btn" onclick="switchTab('categorical')">📋 Categorical Columns</button>
            <button class="tab-btn" onclick="switchTab('correlations')">🔗 Correlations</button>
            <button class="tab-btn" onclick="switchTab('sample')">📝 Sample Data</button>
        </div>
        
        <!-- Numeric Columns Tab -->
        <div id="numeric" class="tab-content active">
            <div class="card">
                <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 20px;">Numeric Columns Analysis</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Column Name</th>
                                <th>Mean</th>
                                <th>Median (approx)</th>
                                <th>Std Dev</th>
                                <th>Min</th>
                                <th>Max</th>
                                <th>Non-Null Count</th>
                                <th>Null Count</th>
                            </tr>
                        </thead>
                        <tbody id="numeric-table">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Categorical Columns Tab -->
        <div id="categorical" class="tab-content">
            <div class="card">
                <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 20px;">Categorical Columns Analysis</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Column Name</th>
                                <th>Unique Values</th>
                                <th>Non-Null Count</th>
                                <th>Null Count</th>
                                <th>Top Values</th>
                            </tr>
                        </thead>
                        <tbody id="categorical-table">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Correlations Tab -->
        <div id="correlations" class="tab-content">
            <div class="card">
                <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 20px;">Top Correlations</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Column A</th>
                                <th>Column B</th>
                                <th>Correlation</th>
                                <th>Strength</th>
                            </tr>
                        </thead>
                        <tbody id="correlations-table">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Sample Data Tab -->
        <div id="sample" class="tab-content">
            <div class="card">
                <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 20px;">Sample Data (First 5 Rows)</h2>
                <div class="table-container">
                    <table>
                        <tbody id="sample-table">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Data
        const numericCols = {numeric_cols_json};
        const categoricalCols = {categorical_cols_json};
        const correlations = {correlations_json};
        const sampleRows = {json.dumps(sample_rows)};
        
        // Tab switching
        function switchTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        // Populate Numeric Table
        function populateNumericTable() {{
            const tbody = document.getElementById('numeric-table');
            numericCols.forEach(col => {{
                const row = `
                    <tr>
                        <td><strong>${{col.name}}</strong></td>
                        <td>${{col.mean !== null ? col.mean.toFixed(2) : 'N/A'}}</td>
                        <td>-</td>
                        <td>${{col.std !== null ? col.std.toFixed(2) : 'N/A'}}</td>
                        <td>${{col.min !== null ? col.min.toFixed(2) : 'N/A'}}</td>
                        <td>${{col.max !== null ? col.max.toFixed(2) : 'N/A'}}</td>
                        <td>${{col.non_null}}</td>
                        <td>${{col.null}}</td>
                    </tr>
                `;
                tbody.innerHTML += row;
            }});
        }}
        
        // Populate Categorical Table
        function populateCategoricalTable() {{
            const tbody = document.getElementById('categorical-table');
            categoricalCols.forEach(col => {{
                const topVals = Object.entries(col.top_values).map(([k, v]) => `${{k}}: ${{v}}`).join(', ');
                const row = `
                    <tr>
                        <td><strong>${{col.name}}</strong></td>
                        <td>${{col.unique}}</td>
                        <td>${{col.non_null}}</td>
                        <td>${{col.null}}</td>
                        <td>${{topVals}}</td>
                    </tr>
                `;
                tbody.innerHTML += row;
            }});
        }}
        
        // Populate Correlations Table
        function populateCorrelationsTable() {{
            const tbody = document.getElementById('correlations-table');
            correlations.forEach(corr => {{
                let strength = 'Weak';
                if (corr.corr > 0.7) strength = 'Strong';
                else if (corr.corr > 0.5) strength = 'Moderate';
                
                const row = `
                    <tr>
                        <td><strong>${{corr.col_a}}</strong></td>
                        <td><strong>${{corr.col_b}}</strong></td>
                        <td>${{corr.corr.toFixed(4)}}</td>
                        <td>${{strength}}</td>
                    </tr>
                `;
                tbody.innerHTML += row;
            }});
        }}
        
        // Populate Sample Table
        function populateSampleTable() {{
            if (sampleRows.length === 0) return;
            
            const tbody = document.getElementById('sample-table');
            const headers = Object.keys(sampleRows[0]);
            
            // Add header row
            let headerRow = '<tr>';
            headers.forEach(h => {{
                headerRow += `<th>${{h}}</th>`;
            }});
            headerRow += '</tr>';
            tbody.innerHTML = headerRow;
            
            // Add data rows
            sampleRows.forEach(row => {{
                let dataRow = '<tr>';
                headers.forEach(h => {{
                    const val = row[h];
                    dataRow += `<td>${{val !== null ? String(val).substring(0, 50) : 'NULL'}}</td>`;
                }});
                dataRow += '</tr>';
                tbody.innerHTML += dataRow;
            }});
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            populateNumericTable();
            populateCategoricalTable();
            populateCorrelationsTable();
            populateSampleTable();
        }});
    </script>
</body>
</html>
"""
    
    # Save HTML file
    base_name = os.path.basename(analysis_json_path)
    html_name = base_name.replace('_analysis.json', '_dashboard.html')
    html_path = os.path.join(os.path.dirname(analysis_json_path), html_name)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path


def get_all_dashboards() -> list:
    """Get list of all generated dashboards."""
    dashboards = []
    outputs_dir = settings.OUTPUT_DIR
    
    if os.path.exists(outputs_dir):
        for file in os.listdir(outputs_dir):
            if file.endswith('_dashboard.html'):
                dashboards.append({
                    'name': file,
                    'path': os.path.join(outputs_dir, file)
                })
    
    return dashboards
