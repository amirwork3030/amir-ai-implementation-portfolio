# Controlled Natural-Language BI Assistant

A safe AI/data prototype showing how natural-language business questions can be translated into controlled analytics without allowing a model to generate unrestricted SQL.

## Business problem
Business users often want faster answers from operational/finance data, but unrestricted model-generated SQL creates security, accuracy and governance risks.

## BA-to-prototype approach
1. Define the supported business questions and data semantics with stakeholders.
2. Create an explicit intent catalogue and acceptance criteria.
3. Map each approved intent to a fixed, inspectable SQL query plan.
4. Use deterministic intent rules first, with an optional bounded LLM classifier only for intent classification.
5. Return clarification for unsupported or ambiguous questions.
6. Audit the original question, recognised intent and execution status.

## Workflow
`Question -> intent recognition -> allowlist check -> fixed SQL plan -> SQLite -> structured result -> audit log`

## Controls
- The model never generates or executes arbitrary SQL.
- Only allowlisted intents can execute.
- Unsupported questions trigger clarification.
- Query plans are returned for transparency.
- Audit events are recorded.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

See [requirements.md](./requirements.md) and [ARCHITECTURE.md](./ARCHITECTURE.md) for the BA and solution-design evidence.
