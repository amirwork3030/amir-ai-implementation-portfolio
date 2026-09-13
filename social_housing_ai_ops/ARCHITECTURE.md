# Architecture - Social Housing / Property Operations AI Triage

## Delivery pattern
1. Discovery workshops map current communication channels, actors, case types, service levels and failure points.
2. BA creates AS-IS and TO-BE workflows plus taxonomy, routing rules and human-control points.
3. Prototype accepts synthetic messages/events.
4. Deterministic rules handle routing/urgency guardrails.
5. Optional LLM layer summarises and suggests bounded next actions using OpenAI or Claude.
6. SQLite audit log records every triage decision for review and iteration.

## Why this is an agent/workflow prototype
The solution is not just a chatbot. It performs a bounded multi-step operational workflow:

Intake -> classify -> extract context -> assess urgency -> select owner -> request human review where required -> persist audit -> expose action queue.

## Controls
- Human approval for high-impact categories.
- No autonomous legal/tenancy/safeguarding decisions.
- No unrestricted external actions in the demo.
- Structured outputs only.
- Synthetic data only.
- Auditability of routing and decisions.

## Production extensions
Approved connectors could later integrate email, CRM/case-management, ServiceNow/Jira, property systems, WhatsApp Business APIs, document stores and notification services subject to information-governance review.
