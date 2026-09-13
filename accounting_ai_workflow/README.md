# AI Accounting Practice Automation

A finance-automation prototype showing how a Technical AI Business Analyst can move from process analysis to an inspectable AI-enabled workflow with explicit controls.

## Business problem
Accounting teams often spend time validating invoice/document data, spotting duplicates, handling incomplete records and routing exceptions. Fully autonomous posting is inappropriate when confidence is low or controls fail.

## BA-to-prototype approach
1. Map the AS-IS document/invoice workflow and identify repetitive validation and exception steps.
2. Define the TO-BE workflow and business rules for automation vs human review.
3. Translate requirements into validation logic, confidence thresholds, duplicate controls and audit requirements.
4. Prototype the workflow in Python with optional bounded LLM exception summarisation.
5. Persist every decision to SQLite for traceability and UAT review.

## Workflow
`Invoice intake -> validate -> duplicate check -> confidence gate -> bounded exception summary -> auto-approved demo state or human review -> audit log`

## Key controls
- The LLM never controls approval.
- Missing invoice numbers, invalid/negative amounts and possible duplicates cannot auto-approve.
- Low-confidence or failed-control records route to human review.
- Decisions are deterministic and auditable.
- Published sample data is synthetic.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The demo works without a live LLM key. Optional OpenAI/Anthropic adapters can provide bounded exception summaries when configured through environment variables.

See [requirements.md](./requirements.md) and [ARCHITECTURE.md](./ARCHITECTURE.md) for the BA and architecture evidence.
