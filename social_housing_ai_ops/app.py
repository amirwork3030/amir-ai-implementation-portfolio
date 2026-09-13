from __future__ import annotations
import csv, json, sqlite3
from pathlib import Path
from datetime import datetime, timezone
from llm_adapter import llm_json

BASE = Path(__file__).parent
INPUT = BASE / "sample_messages.csv"
DB = BASE / "housing_ops_audit.db"

CATEGORIES = {
    "URGENT_MAINTENANCE": ["leak", "water", "no heating", "electrical", "danger"],
    "COMPLIANCE": ["gas safety", "certificate", "expires", "renewal"],
    "TENANCY_DOCUMENTS": ["tenancy", "proof of id", "documents", "referral"],
    "MOVE_IN": ["moving in", "move in", "inventory", "key collection"],
    "CONTRACTOR_COORDINATION": ["attend", "access", "job completed", "invoice"],
    "ROUTINE_MAINTENANCE": ["repair", "light", "broken"],
}

DEFAULT_OWNER = {
    "URGENT_MAINTENANCE": "Property Operations",
    "COMPLIANCE": "Compliance Team",
    "TENANCY_DOCUMENTS": "Housing Officer",
    "MOVE_IN": "Tenancy Coordinator",
    "CONTRACTOR_COORDINATION": "Property Operations",
    "ROUTINE_MAINTENANCE": "Maintenance Queue",
    "GENERAL": "Operations Triage",
}

def rule_classify(text: str):
    low = text.lower()
    scores = {cat: sum(1 for kw in kws if kw in low) for cat, kws in CATEGORIES.items()}
    category = max(scores, key=scores.get) if max(scores.values(), default=0) > 0 else "GENERAL"
    urgency = "HIGH" if category == "URGENT_MAINTENANCE" else "MEDIUM" if category in {"COMPLIANCE", "TENANCY_DOCUMENTS", "MOVE_IN"} else "LOW"
    return category, urgency

def extract_deadline(text: str):
    low = text.lower()
    for token in ["today", "tomorrow", "monday", "friday", "next month"]:
        if token in low:
            return token
    return ""

def bounded_llm_summary(row, category, urgency):
    payload = {
        "message": row["message"],
        "category": category,
        "urgency": urgency,
        "property_ref": row["property_ref"],
        "sender_role": row["sender_role"],
    }
    data = llm_json(
        "You are a bounded housing operations triage assistant. Summarise the supplied message in one sentence and suggest one operational next action. Do not make legal, safeguarding or tenancy decisions. Do not invent facts.",
        json.dumps(payload),
        allowed_keys=["summary", "next_action"],
    )
    if not data:
        return row["message"][:120], "Route to the assigned owner for human review and action."
    return data.get("summary", ""), data.get("next_action", "")

def init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS triage_audit(
        ts TEXT, message_id TEXT, property_ref TEXT, category TEXT, urgency TEXT,
        owner TEXT, deadline TEXT, human_review INTEGER, summary TEXT, next_action TEXT
    )""")
    conn.commit()

def run():
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    init_db(conn)
    rows = list(csv.DictReader(INPUT.open()))
    results = []
    for row in rows:
        category, urgency = rule_classify(row["message"])
        deadline = extract_deadline(row["message"])
        owner = DEFAULT_OWNER[category]
        human_review = 1 if urgency == "HIGH" or category in {"TENANCY_DOCUMENTS", "COMPLIANCE", "MOVE_IN"} else 0
        summary, next_action = bounded_llm_summary(row, category, urgency)
        item = {
            "message_id": row["message_id"],
            "property_ref": row["property_ref"],
            "category": category,
            "urgency": urgency,
            "owner": owner,
            "deadline": deadline,
            "human_review": bool(human_review),
            "summary": summary,
            "next_action": next_action,
        }
        conn.execute(
            "INSERT INTO triage_audit VALUES (?,?,?,?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), row["message_id"], row["property_ref"], category,
             urgency, owner, deadline, human_review, summary, next_action),
        )
        results.append(item)
    conn.commit(); conn.close()
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run()
