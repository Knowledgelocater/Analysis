# app/analysis.py
import pandas as pd
import numpy as np
import os
import json
from .config import settings
from typing import Dict, Any

def convert_timestamps(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: convert_timestamps(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_timestamps(v) for v in obj]
    return obj


def read_excel(file_path: str) -> pd.DataFrame:
    # Use pandas to read — handles .xls/.xlsx
    try:
        df = pd.read_excel(file_path)
    except Exception:
        # fallback to engine openpyxl if needed
        df = pd.read_excel(file_path, engine="openpyxl")
    return df

def basic_profile(df: pd.DataFrame) -> Dict[str, Any]:
    profile = {}
    profile['rows'] = int(df.shape[0])
    profile['cols'] = int(df.shape[1])
    profile['columns'] = []
    for col in df.columns:
        s = df[col]
        col_info = {
            "name": str(col),
            "dtype": str(s.dtype),
            "non_null_count": int(s.count()),
            "null_count": int(s.isna().sum()),
            "unique": int(s.nunique(dropna=True)) if s.nunique(dropna=True) is not None else None
        }
        # numeric stats
        if pd.api.types.is_numeric_dtype(s):
            col_info.update({
                "mean": None if s.dropna().empty else float(s.mean()),
                "median": None if s.dropna().empty else float(s.median()),
                "std": None if s.dropna().empty else float(s.std()),
                "min": None if s.dropna().empty else float(s.min()),
                "max": None if s.dropna().empty else float(s.max()),
            })
        else:
            top = s.dropna().value_counts().head(5).to_dict()
            col_info.update({"top_values": top})
        profile['columns'].append(col_info)
    return profile

def top_correlations(df: pd.DataFrame, numeric_limit: int = 10):
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] <= 1:
        return []
    # limit columns to most informative by variance if too many
    if numeric.shape[1] > numeric_limit:
        variances = numeric.var().sort_values(ascending=False)
        keep_cols = variances.index[:numeric_limit].tolist()
        numeric = numeric[keep_cols]
    corr = numeric.corr().abs()
    pairs = []
    # iterate upper triangle
    cols = corr.columns
    for i in range(len(cols)):
        for j in range(i+1, len(cols)):
            a, b = cols[i], cols[j]
            pairs.append((a, b, float(corr.iloc[i, j])))
    pairs_sorted = sorted(pairs, key=lambda x: x[2], reverse=True)
    return [{"col_a": a, "col_b": b, "corr": c} for a,b,c in pairs_sorted[:10]]

def sample_rows(df: pd.DataFrame, n: int = 5):
    return df.head(n).fillna("").to_dict(orient="records")

def convert_timestamps(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {convert_timestamps(k): convert_timestamps(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_timestamps(item) for item in obj]
    return obj

def analyze_excel(file_path: str) -> str:
    df = read_excel(file_path)
    profile = basic_profile(df)
    correlations = top_correlations(df)
    sample = sample_rows(df, n=5)

    analysis = {
        "file_path": file_path,
        "profile": profile,
        "correlations": correlations,
        "sample_rows": sample,
    }

    # Convert timestamps recursively
    analysis = convert_timestamps(analysis)

    # Ensure output directory exists
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    base = os.path.basename(file_path)
    outname = os.path.splitext(base)[0] + "_analysis.json"
    output_path = os.path.join(settings.OUTPUT_DIR, outname)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    return output_path

def run_analysis(file_path: str) -> dict:
    """
    Wrapper for backward compatibility.
    Celery expects run_analysis(), so we call analyze_excel().
    """
    try:
        output_path = analyze_excel(file_path)
        return {"analysis_path": output_path}
    except Exception as e:
        return {"error": str(e)}
