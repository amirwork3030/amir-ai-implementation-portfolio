from __future__ import annotations
import csv, sqlite3, json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from llm_adapter import llm_json

BASE = Path(__file__).parent
DB = BASE / "workflow_audit.db"
INPUT = BASE / "sample_invoices.csv"
MANDATORY = ["supplier", "invoice_number", "invoice_date", "gross_amount", "currency"]

def fingerprint(row):
    key = "|".join([row.get("supplier", "").strip().lower(), row.get("invoice_number", "").strip().lower(), row.get("invoice_date", ""), row.get("gross_amount", "")])
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def validate(row):
    issues=[]
    for field in MANDATORY:
        if not str(row.get(field, "")).strip():
            issues.append(f"missing:{field}")
    try:
        if float(row.get("gross_amount", 0)) <= 0:
            issues.append("amount_must_be_positive")
    except ValueError:
        issues.append("invalid_amount")
    return issues

def confidence(issues):
    score=1.0
    score -= 0.18 * len([x for x in issues if x.startswith("missing:")])
    score -= 0.25 * len([x for x in issues if not x.startswith("missing:")])
    return max(0.0, round(score,2))

def analyst_note(row, issues):
    if not issues:
        return "No exception."
    data=llm_json(
        "You are a bounded accounting exception triage assistant. Do not approve or post anything. Summarise only the supplied validation issues.",
        json.dumps({"invoice":row,"issues":issues}),
        allowed_keys=["summary"]
    )
    return data.get("summary") if data else "Review required: " + ", ".join(issues)

def init_db(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS audit(ts TEXT, invoice_id TEXT, fingerprint TEXT, confidence REAL, decision TEXT, issues TEXT, analyst_note TEXT)")
    conn.commit()

def run():
    if DB.exists():
        DB.unlink()
    conn=sqlite3.connect(DB)
    init_db(conn)
    rows=list(csv.DictReader(INPUT.open()))
    seen={}; results=[]
    for row in rows:
        fp=fingerprint(row); issues=validate(row)
        if fp in seen:
            issues.append(f"possible_duplicate_of:{seen[fp]}")
        else:
            seen[fp]=row["invoice_id"]
        conf=confidence(issues)
        decision="AUTO_APPROVED" if conf >= 0.80 and not issues else "HUMAN_REVIEW"
        note=analyst_note(row,issues) if decision=="HUMAN_REVIEW" else "No exception."
        conn.execute("INSERT INTO audit VALUES (?,?,?,?,?,?,?)",(datetime.now(timezone.utc).isoformat(),row["invoice_id"],fp,conf,decision,json.dumps(issues),note))
        results.append({"invoice_id":row["invoice_id"],"supplier":row["supplier"],"confidence":conf,"decision":decision,"issues":issues,"analyst_note":note})
    conn.commit(); conn.close(); print(json.dumps(results,indent=2))

if __name__ == "__main__":
    run()
