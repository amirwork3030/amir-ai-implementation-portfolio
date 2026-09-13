# Social Housing / Property Management AI Operations

A bounded AI-assisted workflow demonstrating how I move from stakeholder/process discovery to a working Technical AI BA prototype.

## Business problem
Property teams can receive fragmented messages from tenants, contractors, landlords, councils/referral teams and internal staff. Manual triage creates missed actions, duplicated chasing, unclear ownership and deadline risk.

## BA-to-prototype approach
1. Identify stakeholders, communication channels, case types, service levels and failure points.
2. Map the AS-IS process and pain points.
3. Define the TO-BE triage/routing workflow, taxonomy, controls and human-review points.
4. Translate these into functional requirements and acceptance criteria.
5. Prototype the workflow in Python using deterministic rules plus an optional bounded LLM summarisation layer.
6. Persist routing/decision data to SQLite for traceability and iteration.

## Workflow
`Intake -> classify -> extract context -> assess urgency/deadline -> select owner -> human review where required -> audit -> action queue`

## Controls
- No autonomous legal, safeguarding or tenancy decisions.
- High-impact categories require human review.
- The optional LLM only summarises and suggests a bounded next action.
- Structured outputs and synthetic data only.
- Routing decisions are auditable.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Optional live LLM mode supports environment-variable configuration for OpenAI or Anthropic. The demo works without a live LLM key using deterministic fallback behaviour.

See [requirements.md](./requirements.md) and [ARCHITECTURE.md](./ARCHITECTURE.md) for the BA and solution-design evidence.
