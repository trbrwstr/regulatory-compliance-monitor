# Architecture and data flow

## Supported scope

The MVP is a monitoring and review tool, not legal advice. The supported scope must be recorded by the RCM-001 decision before new sources or jurisdictions are enabled.

## Flow

1. A versioned source adapter fetches an allowlisted official endpoint.
2. The response is bounded, parsed as untrusted content, hashed, and stored as an immutable source snapshot.
3. The scheduler normalizes content, creates a regulation version, and records a deterministic diff from the prior version.
4. Transparent relevance rules and optional provider classification create a draft item.
5. A summary remains a draft and carries citations to the snapshot and location.
6. An authorized reviewer approves or rejects the item.
7. Only approved items can create idempotent notification records.
8. Audit events preserve review, deletion, and delivery actions.

## Data boundaries

- Customer-owned records: subscribers, preferences, review notes, and derived decisions.
- Public-source provenance: source URLs, snapshots, hashes, versions, diffs, and citations retained for reproducibility.
- Secrets: environment variables only; never exported or written to content logs.

## Failure states

A source timeout, malformed response, stale source, unavailable model, or failed mail delivery produces an explicit incomplete or failed state. The system must not present an all-clear state when source coverage is incomplete.
