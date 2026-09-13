# Architecture

Input CSV -> validation tool -> duplicate fingerprint tool -> confidence gate -> optional bounded LLM exception summary -> human review or auto-approved demo state -> SQLite audit log.

The LLM does not control approval. Approval logic remains deterministic and inspectable.
