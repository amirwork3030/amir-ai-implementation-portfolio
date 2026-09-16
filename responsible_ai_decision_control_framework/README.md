# Responsible AI Decision Control Framework

Synthetic portfolio proof-of-concept demonstrating how a Business Analyst can translate policy, risk and control expectations into implementation-ready requirements for AI-enabled decision workflows.

> Portfolio demonstration only. Uses synthetic scenarios and does not represent a deployment for a regulator or financial institution.

## Business problem

AI-enabled decisions need more than an accurate model output. Organisations need clear rules for when AI may recommend or progress an outcome, when a human must review it, when the case must be escalated, and what evidence must be retained for audit and validation.

## Control model

`AI output -> confidence/risk assessment -> policy & control checks -> decision threshold -> approve / human review / escalate -> decision log -> validation evidence`

### Example routing rules

- **Low risk + high confidence + controls passed** -> AI recommendation can progress to defined business approval.
- **Medium confidence or material exception** -> mandatory human review.
- **Low confidence, policy conflict or high-impact case** -> escalate to authorised owner; no autonomous progression.
- **All outcomes** -> capture decision ID, inputs, rule triggered, reviewer/owner, outcome, rationale and timestamp.

## BA / Responsible AI evidence

- AS-IS / TO-BE process modelling
- Translation of policy, standards, risk and control expectations into workflow requirements
- Functional requirements, user stories and acceptance criteria
- Human-in-the-loop controls
- Confidence / decision thresholds
- Escalation and exception paths
- Auditability and traceability
- Validation scenarios and business sign-off evidence
- Risks/issues identified through design, build and testing

## Sample acceptance criteria

**Given** an AI-supported case is classified as high impact, **when** the workflow reaches the decision stage, **then** the system must prevent autonomous approval and route the case to an authorised human reviewer.

**Given** model confidence falls below the agreed threshold, **when** a recommendation is generated, **then** the workflow must flag the confidence result, create an exception reason and route the case for review or escalation.

**Given** a policy/control rule fails, **when** the workflow evaluates the case, **then** the AI recommendation must not progress and the failed control, escalation owner and final resolution must be recorded.

## Visual demo

Open [`index.html`](index.html) to view the synthetic decision-control dashboard.

## Implementation-readiness outputs

A production implementation would add authenticated roles, approved policy/control rules, model/version metadata, data lineage, formal validation evidence, monitoring thresholds, incident/change controls and integration with the organisation's case-management/audit systems.
