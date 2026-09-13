# Social Housing / Property Operations AI Triage - BA Requirements

## Business problem
Property-management operations can receive high volumes of fragmented messages across tenant, contractor, landlord, council/referral and internal channels. Manual triage creates risk of missed actions, unclear ownership, duplicated chasing and poor visibility of deadlines.

## AS-IS pattern
Message arrives -> staff read manually -> decide priority -> identify property/case -> forward/chase -> create task manually -> follow up across separate channels -> status difficult to track.

## TO-BE pattern
Message/event intake -> AI-assisted classification and entity extraction -> urgency/deadline identification -> bounded next-action suggestion -> rule-based owner routing -> human review for controlled categories -> task/audit record -> dashboard/status follow-up.

## Stakeholders for discovery workshops
- Property Manager / Operations Lead
- Housing Officers / Tenancy Coordinators
- Maintenance / Compliance staff
- Contractors
- Landlords / Providers
- Council / Referral teams
- Admin / Customer support
- Technical / Data / Information Governance stakeholders

## Functional requirements
- FR-01: Ingest or accept messages/events from approved channels.
- FR-02: Identify property/case reference where supplied.
- FR-03: Classify the operational intent into an agreed taxonomy.
- FR-04: Detect explicit deadline language and urgency indicators.
- FR-05: Route work to an agreed operational owner/queue.
- FR-06: Require human review for high-impact tenancy, compliance, move-in or urgent items.
- FR-07: Record triage decision, timestamp, source, owner and next action in an audit log.
- FR-08: Do not allow the LLM to make legal, safeguarding, tenancy or financial decisions autonomously.

## Example acceptance criteria
Given a message contains an urgent maintenance indicator, when triage runs, then it is classified as urgent, routed to Property Operations and flagged for human review.

Given a message relates to missing tenancy documentation, when triage runs, then the Housing Officer queue is selected and the item cannot be auto-closed.

Given no recognised category is detected, when triage runs, then the item is routed to Operations Triage rather than inventing a category or action.
