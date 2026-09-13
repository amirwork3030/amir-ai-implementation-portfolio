# Business / Technical Requirements

- AIR-01: Ingest invoice records and validate mandatory fields.
- AIR-02: Calculate a confidence score based on completeness and validation results.
- AIR-03: Detect potential duplicates before posting.
- AIR-04: Route low-confidence, invalid or duplicate records to human review.
- AIR-05: Record workflow decisions in an audit log.
- AIR-06: Do not auto-approve negative amounts or missing invoice numbers.

## Acceptance Criteria

- Valid unique invoices can reach `AUTO_APPROVED`.
- Duplicate records are held for `HUMAN_REVIEW`.
- Missing invoice number or invalid amount reduces confidence and prevents auto-approval.
- Every record creates an audit event in SQLite.
