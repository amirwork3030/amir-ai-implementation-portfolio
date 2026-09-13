from __future__ import annotations
import sqlite3, json
from pathlib import Path
from datetime import datetime, timezone
from llm_adapter import llm_json

BASE=Path(__file__).parent
DB=BASE/'business_metrics.db'
ALLOWED={'monthly_revenue','cost_by_department','monthly_incidents','margin_by_department','clarify'}

def init_db(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS metrics(month TEXT, department TEXT, revenue REAL, cost REAL, incidents INTEGER)')
    if conn.execute('SELECT COUNT(*) FROM metrics').fetchone()[0] == 0:
        rows=[('2026-06','Finance',125000,82000,4),('2026-06','Operations',98000,74000,9),('2026-07','Finance',132000,85000,3),('2026-07','Operations',102000,76000,6),('2026-08','Finance',140000,87000,2),('2026-08','Operations',110000,79000,5)]
        conn.executemany('INSERT INTO metrics VALUES (?,?,?,?,?)',rows)
    conn.execute('CREATE TABLE IF NOT EXISTS audit(ts TEXT, question TEXT, intent TEXT, status TEXT)')
    conn.commit()

def recognise_rules(question):
    q=question.lower()
    if 'revenue' in q and ('month' in q or 'monthly' in q or 'trend' in q): return 'monthly_revenue'
    if 'cost' in q and ('department' in q or 'by team' in q): return 'cost_by_department'
    if 'incident' in q and ('month' in q or 'trend' in q): return 'monthly_incidents'
    if ('margin' in q or 'profit' in q) and 'department' in q: return 'margin_by_department'
    return 'clarify'

def recognise(question):
    rule=recognise_rules(question)
    if rule!='clarify': return rule
    data=llm_json(
        'Classify the business question into exactly one supported intent: monthly_revenue, cost_by_department, monthly_incidents, margin_by_department, clarify. Never create SQL.',
        question,
        allowed_keys=['intent']
    )
    intent=(data or {}).get('intent','clarify')
    return intent if intent in ALLOWED else 'clarify'

def plan(intent):
    plans={
      'monthly_revenue':'SELECT month, ROUND(SUM(revenue),2) value FROM metrics GROUP BY month ORDER BY month',
      'cost_by_department':'SELECT department, ROUND(SUM(cost),2) value FROM metrics GROUP BY department ORDER BY value DESC',
      'monthly_incidents':'SELECT month, SUM(incidents) value FROM metrics GROUP BY month ORDER BY month',
      'margin_by_department':'SELECT department, ROUND(SUM(revenue-cost),2) value FROM metrics GROUP BY department ORDER BY value DESC'
    }
    return plans.get(intent)

def ask(question):
    conn=sqlite3.connect(DB)
    init_db(conn)
    intent=recognise(question)
    if intent=='clarify':
        conn.execute('INSERT INTO audit VALUES (?,?,?,?)',(datetime.now(timezone.utc).isoformat(),question,intent,'CLARIFICATION_REQUIRED'))
        conn.commit(); conn.close()
        return {'status':'CLARIFICATION_REQUIRED','message':'Supported examples: monthly revenue trend, cost by department, monthly incident trend, margin by department.'}
    sql=plan(intent)
    cur=conn.execute(sql)
    cols=[d[0] for d in cur.description]
    rows=[dict(zip(cols,r)) for r in cur.fetchall()]
    conn.execute('INSERT INTO audit VALUES (?,?,?,?)',(datetime.now(timezone.utc).isoformat(),question,intent,'OK'))
    conn.commit(); conn.close()
    return {'status':'OK','intent':intent,'query_plan':sql,'rows':rows}

if __name__=='__main__':
    for q in ['Show monthly revenue trend','Show cost by department','What is margin by department?','Tell me everything about customers']:
        print('\nQUESTION:',q)
        print(json.dumps(ask(q),indent=2))
