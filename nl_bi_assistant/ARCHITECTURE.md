# Architecture

Natural-language question -> deterministic intent rules -> optional bounded LLM intent classifier -> allowlisted intent -> fixed SQL query plan -> SQLite -> structured result -> audit log.

The model never generates or executes arbitrary SQL.
