import json
import os
from pathlib import Path

import streamlit as st
from core import MODULES, Recommendation, approve, controls, recommend, validate_input

st.set_page_config(page_title="Amir Iqbal | AI Business Analyst", page_icon="◈", layout="wide")
st.markdown("""<style>.stApp {background:#f5f7fb} h1,h2,h3 {color:#14243b} div[data-testid="stMetric"] {background:white;padding:18px;border-radius:12px;border:1px solid #dde4ef} .block-container {padding-top:6rem!important}</style>""", unsafe_allow_html=True)
st.caption("AMIR IQBAL · TECHNICAL AI BUSINESS ANALYST")
st.title("From business challenge to controlled action")
st.write("Three working portfolio modules demonstrate discovery, structured AI recommendations, human oversight and auditability.")
st.info("Synthetic portfolio demonstration. Human approval records acceptance of a recommendation for review; it does not approve finance, execute transformation or accept an engagement.")
with st.sidebar:
    st.header("Workspace")
    module = st.selectbox("Module", list(MODULES), key="selected_module")
    live_enabled = os.getenv("PORTFOLIO_ENABLE_PRIVATE_LIVE", "").lower() == "true"
    modes = ["Sample-data demonstration"] + (["Live OpenAI"] if live_enabled else [])
    mode = st.radio("Recommendation mode", modes)
    st.caption("Demo mode makes no external API calls. Live mode sends the input to OpenAI; use synthetic data only.")
    model = st.text_input("OpenAI model", "gpt-4o-mini") if mode == "Live OpenAI" else "gpt-4o-mini"
    st.caption("Public deployment is free demo only. Live integration is disabled unless explicitly enabled in a private, access-controlled deployment.")

# Recruiter-facing portfolio homepage; module selection and review controls remain below.
st.markdown("""
<style>
.hero-banner {background:linear-gradient(125deg,#11243c,#214e77);border-radius:18px;
 padding:30px 34px;color:white;margin:8px 0 25px;}
.hero-banner h2 {color:white!important;font-size:2rem;line-height:1.2;margin:0 0 12px;}
.hero-banner p {color:#dce9f5;font-size:1.05rem;max-width:760px;margin:0;}
.section-kicker {font-weight:700;letter-spacing:.13em;color:#3976a9;font-size:.8rem;}
.project-card {min-height:220px;background:white;border:1px solid #dbe4ee;border-radius:14px;
padding:20px;box-shadow:0 4px 16px rgba(18,39,64,.035);}
.project-card h3 {font-size:1.2rem;margin:10px 0;color:#132843;}
.project-card p {color:#4b5d70;font-size:.91rem;line-height:1.55;}
.project-tag {color:#276193;font-weight:700;font-size:.73rem;letter-spacing:.06em;}
</style>
<div class="hero-banner">
<div class="section-kicker" style="color:#a8d8ff">AI IMPLEMENTATION · BUSINESS ANALYSIS · DIGITAL TRANSFORMATION</div>
<h2>Turning complex business problems into practical AI solutions.</h2>
<p>Explore three interactive demonstrations covering financial services, operational transformation
and professional services. Each illustrates structured recommendations, human oversight and traceable decisions.</p>
</div>
""", unsafe_allow_html=True)
st.markdown('<p class="section-kicker">SELECTED PROJECTS</p>', unsafe_allow_html=True)
st.subheader("Explore the portfolio")
projects = [
    ("Insurance premium finance", "FINANCIAL SERVICES · AI CASE TRIAGE",
     "Insurance Premium Finance", "Analyse an insurance finance case, flag affordability, arrears and vulnerability controls, and route recommendations for human review.",
     "Case triage · Finance controls · Audit"),
    ("Process discovery & transformation", "OPERATIONS · PROCESS IMPROVEMENT",
     "AI Process Transformation", "Investigate current workflows, quantify baseline workload and propose practical future-state process improvements.",
     "AS-IS / TO-BE · Requirements · Value"),
    ("Professional services intake", "PROFESSIONAL SERVICES · WORK INTAKE",
     "Professional Services Intake", "Assess incoming requests, surface conflict-check requirements and recommend a review route for client-facing work.",
     "Intake · Routing · Human oversight"),
]
columns = st.columns(3, gap="medium")
for col, (name, label, heading, description, tags) in zip(columns, projects):
    with col:
        st.markdown(
            f'<div class="project-card"><div class="project-tag">{label}</div>'
            f'<h3>{heading}</h3><p>{description}</p>'
            f'<p><strong>{tags}</strong></p></div>',
            unsafe_allow_html=True,
        )
        st.button("Explore this project →", key=f"explore:{name}",
                  use_container_width=True,
                  on_click=lambda value=name: st.session_state.update(selected_module=value))
st.caption("Public portfolio uses synthetic examples and pre-defined demonstration recommendations. Live LLM calls are disabled.")
st.divider()
st.subheader("Interactive project workspace")
st.write(f"**Selected demonstration:** {module}. Use the workspace below to generate, edit and approve a structured recommendation.")

left, right = st.columns([1, 1.15], gap="large")
with left:
    st.subheader("1 · Discover & validate")
    raw = st.text_area("Synthetic case data · editable JSON", json.dumps(MODULES[module], indent=2), height=340, key=f"input:{module}")
    data = None
    try:
        data = validate_input(module, json.loads(raw))
        flags = controls(module, data)
        st.success("Case structure validated")
        for flag in flags:
            st.warning(flag)
        if module == "Insurance premium finance":
            st.metric("Financed amount · illustrative", f"£{data['premium'] - data['deposit']:,.0f}")
        elif module == "Process discovery & transformation":
            st.metric("Reported monthly workload", f"{data['monthly_volume'] * data['minutes_per_case'] / 60:,.1f} hours")
        else:
            st.metric("Estimated effort", f"{data['estimated_hours']} hours")
    except (ValueError, TypeError):
        st.error("Invalid case JSON. Use the sample field names and data types.")
    if st.button("Generate recommendation", type="primary", disabled=data is None):
        try:
            key = os.getenv("OPENAI_API_KEY")
            if mode == "Live OpenAI" and not key:
                try:
                    key = st.secrets.get("OPENAI_API_KEY")
                except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
                    key = None
            with st.spinner("Preparing structured recommendation…"):
                rec = recommend(module, data, mode == "Live OpenAI", key, model)
            st.session_state["result"] = {"module": module, "data": data, "rec": rec.model_dump(), "mode": mode}
            st.session_state["generation"] = st.session_state.get("generation", 0) + 1
        except Exception:
            st.error("Recommendation unavailable. Check secure credentials, model access and provider connectivity. No approval was recorded.")
with right:
    st.subheader("2 · Review & refine")
    result = st.session_state.get("result")
    if result and result["module"] == module and result["data"] == data and result["mode"] == mode:
        generation = st.session_state["generation"]
        already_approved = st.session_state.get("approved_generation") == generation
        edited = st.text_area("Editable recommendation · structured JSON", json.dumps(result["rec"], indent=2), height=350, key=f"recommendation:{generation}", disabled=already_approved)
        st.caption("Edit the recommendation before approving. Deterministic controls remain attached to the original input.")
        st.subheader("3 · Human approval")
        reviewer = st.text_input("Reviewer name", key=f"reviewer:{generation}", disabled=already_approved)
        note = st.text_area("Approval rationale", key=f"note:{generation}", disabled=already_approved)
        acknowledge = st.checkbox("I reviewed the input, recommendation and mandatory controls. This approves a recommendation for review only.", key=f"ack:{generation}", disabled=already_approved)
        if st.button("Approve recommendation for review", disabled=already_approved):
            try:
                payload = Recommendation.model_validate_json(edited).model_dump()
                audit_id = approve(os.getenv("PORTFOLIO_AUDIT_DB", str(Path(__file__).parent / "portfolio_audit.db")), module, data, payload, reviewer, note, acknowledge)
                st.session_state["approved_generation"] = generation
                st.session_state["audit_id"] = audit_id
                st.session_state["approved_record"] = {"audit_id": audit_id, "module": module, "case": data, "recommendation": payload, "controls": controls(module, data), "reviewer": reviewer, "rationale": note, "outcome": "RECOMMENDATION_APPROVED_FOR_REVIEW"}
                st.rerun()
            except (ValueError, TypeError):
                st.error("Provide valid recommendation JSON, reviewer, rationale and acknowledgement.")
            except Exception:
                st.error("Audit storage unavailable. Approval was not confirmed.")
        if st.session_state.get("approved_generation") == generation:
            st.success(f"Recommendation approved for review · audit #{st.session_state['audit_id']}")
            st.download_button("Export this session’s approval record", json.dumps(st.session_state["approved_record"], indent=2), file_name="approval-record.json", mime="application/json")
        st.download_button("Export recommendation draft", edited, file_name=f"{data['case_id']}-recommendation.json", mime="application/json")
    else:
        st.write("Generate a recommendation from the current case to begin review.")
        st.caption("Changing the input or mode requires a fresh recommendation before approval.")
st.divider()
st.caption("PORTFOLIO EVIDENCE · Requirements translation · Process controls · JSON schema · Human approval · SQLite audit")
