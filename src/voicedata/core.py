"""VoiceData Lab: local analytics, safe intent schema, and offline speech adapters."""
from __future__ import annotations
import argparse
import json
import re
import sqlite3
import subprocess
from pathlib import Path

def create_demo_database(db: str | Path) -> None:
    """Synthetic revenue values. Never label these as actual SEC company results."""
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS revenue (company TEXT NOT NULL, quarter TEXT NOT NULL, revenue REAL NOT NULL, PRIMARY KEY(company,quarter))")
        conn.executemany("INSERT OR REPLACE INTO revenue VALUES (?,?,?)",[
            ("DemoCo","2025-Q1",20.0),("DemoCo","2025-Q2",24.0),
            ("DemoCo","2025-Q3",27.0),("DemoCo","2025-Q4",35.0)])
        conn.commit()

def parse_intent(text: str) -> dict:
    """Transparent baseline: supports revenue summaries for a named company."""
    if not isinstance(text,str) or not text.strip():
        raise ValueError("Query cannot be empty")
    if not re.search(r"\brevenue\b",text,re.I):
        raise ValueError("Only revenue questions supported in the baseline")
    match = re.search(r"\bfor\s+([\w-]+)",text,re.I)
    company = match.group(1) if match else "DemoCo"
    return {"operation":"revenue_trend","company":company}

def query_revenue(db: str | Path, intent: dict) -> list[dict]:
    if set(intent) != {"operation","company"} or intent["operation"] != "revenue_trend":
        raise ValueError("Unsupported analytics operation")
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT quarter,revenue FROM revenue WHERE company = ? ORDER BY quarter",(intent["company"],)).fetchall()
    if not rows:
        raise LookupError("No matching revenue data")
    return [{"quarter":quarter,"revenue":rev} for quarter,rev in rows]

def analyze(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("At least one observation is required")
    changes = []
    for prior, current in zip(rows, rows[1:]):
        if prior["revenue"] == 0:
            changes.append({"quarter":current["quarter"],"growth_pct":None})
        else:
            changes.append({"quarter":current["quarter"],"growth_pct":round(100*(current["revenue"]-prior["revenue"])/prior["revenue"],2)})
    valid = [x for x in changes if x["growth_pct"] is not None]
    top = max(valid,key=lambda x:x["growth_pct"]) if valid else None
    return {"rows":rows,"quarterly_growth":changes,"highest_growth":top}

def transcribe(path: str, model_size: str = "tiny") -> str:
    """Requires local pip install -e '.[voice]' and first-use model download."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("Install optional voice dependencies: pip install -e '.[voice]'") from exc
    model = WhisperModel(model_size,device="cpu",compute_type="int8")
    segments,_ = model.transcribe(path)
    return " ".join(s.text.strip() for s in segments).strip()

def speak(text: str, *, command: str = "say") -> None:
    """macOS system TTS; on other systems provide a compatible TTS executable."""
    subprocess.run([command,text],check=True)

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=["init","ask","voice"])
    p.add_argument("--db",default="demo.db")
    p.add_argument("--text",default="Show revenue for DemoCo")
    p.add_argument("--audio",help="Audio file for optional local speech recognition")
    p.add_argument("--speak",action="store_true")
    args=p.parse_args()
    if args.command=="init":
        create_demo_database(args.db)
        print("Initialized synthetic DemoCo data")
        return
    query = transcribe(args.audio) if args.command=="voice" and args.audio else args.text
    result=analyze(query_revenue(args.db,parse_intent(query)))
    result["transcript"]=query
    print(json.dumps(result,indent=2))
    if args.speak:
        top=result["highest_growth"]
        speak(f"Highest quarter over quarter growth: {top['quarter']}, {top['growth_pct']} percent" if top else "Insufficient data to calculate growth")

if __name__=="__main__":
    main()
