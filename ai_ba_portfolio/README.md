# AI Business Analyst portfolio

A professional Streamlit application with three working modules: insurance premium finance case triage, business process discovery and transformation, and professional services intake. All examples are synthetic.

## Run locally

From `/workspace/amir-ai-implementation-portfolio`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r ai_ba_portfolio/requirements.txt
cd ai_ba_portfolio
../.venv/bin/python -m streamlit run app.py
```

The sample-data mode runs without credentials and makes no API calls. Choose a module, edit the case JSON, generate a recommendation, edit its structured JSON, then supply a reviewer, rationale and control acknowledgement. SQLite stores the reviewed input, recommendation, mandatory controls, reviewer, timestamp and approval outcome. Changing the input or mode invalidates the displayed recommendation.

## Live OpenAI

For a separate private, access-controlled deployment only, set `PORTFOLIO_ENABLE_PRIVATE_LIVE=true` and configure `OPENAI_API_KEY` securely in the runtime environment or Streamlit deployment secrets. Never commit keys, paste them into case data, or add them to configuration files. Select Live OpenAI in the sidebar. The adapter requests a strict JSON schema and validates the result with Pydantic. Default model: `gpt-4o-mini`; select another compatible model if required. Requests have a 30-second timeout and one retry. Errors do not approve or silently substitute demo recommendations. Live mode sends the synthetic case to OpenAI. Live responses remain editable and always require human approval.

Mandatory controls are computed independently of AI output and remain in the audit even if recommendation text changes. Approval means acceptance of a recommendation for further review, never credit approval, customer engagement acceptance or execution. Missing conflict checks block engagement acceptance, not intake review.

## Test examples

```bash
cd /workspace/amir-ai-implementation-portfolio/ai_ba_portfolio
../.venv/bin/python -m pytest -q
```

Tests cover all three demo recommendations, persisted approvals, missing approval evidence, finance input limits, vulnerability/arrears/affordability controls, conflict checks, and each module's Streamlit generation/approval/stale-input flow. No paid API calls occur during tests. Live integration needs a separately configured key and compatible model and is not validated by demo tests.

## Deploy to Streamlit Community Cloud

Select this repository, branch and entry point `ai_ba_portfolio/app.py`, using Python 3.12. The app-local `requirements.txt` declares dependencies. Configuration is supplied in both repository-root and app-local `.streamlit/config.toml` for their respective launch directories. For public deployment, leave live mode disabled and do not configure an API key. A separate private deployment may use the Secrets editor for live integration. Usage telemetry is disabled in the supplied config.

`PORTFOLIO_AUDIT_DB` optionally selects the SQLite path (default `portfolio_audit.db` beside the app). Cloud local storage may be ephemeral: export recommendations or use a durable approved datastore before operational use. This portfolio has no authentication or authorisation system and reviewer names are self-entered; it is a synthetic demonstration, not an operational finance or client system. No automated deployment has been performed.

## Public deployment checklist

Public deployments default to **free demo only**, even if an OpenAI key is accidentally present. Do not set `PORTFOLIO_ENABLE_PRIVATE_LIVE` or provide API credentials to the public deployment. Live integration is available only when that variable is `true`; use it solely in a separate private, access-controlled deployment. The app itself does not implement authentication, API quotas or billing controls.

In Streamlit Community Cloud choose repository `amirwork3030/amir-ai-implementation-portfolio`, the pushed portfolio branch, entry file `ai_ba_portfolio/app.py`, and Python 3.12. The repository-root `.streamlit/config.toml` also supplies the theme and server configuration for root launches. No deployment secrets are required for the public demo. The app-folder requirements are discovered alongside the entry file.

Only use synthetic inputs and synthetic reviewer names. Approval data is not shown across sessions; each session can export its own approval record. SQLite audit data is ignored by Git and may be lost on cloud restart. Approved recommendations become read-only; generate a fresh recommendation for further edits. Audit records are demonstration evidence, not authenticated legal sign-off.

Run the complete repository test suite from the repository root with `.venv/bin/python -m pytest -q`. Streamlit AppTest exercises all three modules without a browser or API key.
