# app/ai.py
import os
import json
from groq import Groq
from typing import Dict, Any

from .config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """
You are a data analysis assistant.
You must return output in strict JSON format with keys:
- insights (list of strings)
- recommendations (list of strings)
- data_issues (list of strings)
Never return text outside JSON.
"""

def build_prompt(analysis_json: Dict[str, Any]) -> str:
    profile = analysis_json.get("profile", {})
    corr = analysis_json.get("correlations", [])
    sample = analysis_json.get("sample_rows", [])

    lines = []
    lines.append(f"Rows: {profile.get('rows')}, Columns: {profile.get('cols')}")

    lines.append("Columns:")
    for c in profile.get("columns", []):
        lines.append(
            f"- {c['name']} (dtype={c['dtype']}, non_null={c['non_null_count']}, nulls={c['null_count']})"
        )

    if corr:
        lines.append("Top correlations:")
        for p in corr[:5]:
            lines.append(f"- {p['col_a']} vs {p['col_b']}: {p['corr']}")

    lines.append("Sample rows:")
    for row in sample[:5]:
        lines.append(str(row))

    return "\n".join(lines)


def call_groq_for_insights(analysis_path: str) -> dict:
    try:
        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis_json = json.load(f)

        prompt_text = build_prompt(analysis_json)

        # --- Call Groq ---
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_text}
            ],
        )

        raw_text = response.choices[0].message.content.strip()

        # Groq may return fenced JSON ```json ... ``` → CLEAN IT
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").strip()
            if raw_text.startswith("json"):
                raw_text = raw_text[len("json"):].strip()

        # Try parsing JSON
        try:
            parsed = json.loads(raw_text)
        except:
            return {"error": f"AI returned non-JSON output:\n{raw_text}"}

        insights_path = analysis_path.replace("_analysis.json", "_insights.json")

        with open(insights_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)

        return {"insights_path": insights_path, "insights": parsed}

    except Exception as e:
        return {"error": str(e)}
