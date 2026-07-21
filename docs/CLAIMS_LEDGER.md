# Claims ledger

| Claim | Evidence required | Current status | Boundary |
|---|---|---|---|
| A source change is reproducible | Immutable snapshot, hash, version, diff, and citation | Implemented in ingestion path | Applies only to captured source content |
| Draft summaries have a deterministic fallback | Provider-disabled summarizer path | Implemented | Fallback is not legal analysis |
| Notifications require review | Approval state checked before alert creation | Implemented | MVP reviewer identity uses protected request headers |
| Notification replay is idempotent | Unique delivery key and scheduler lookup | Implemented | Concurrent multi-worker delivery needs database locking validation |
| Customer data can be exported | `/api/data/export` machine-readable response | Implemented | Current tenant scoping requires authenticated tenant context integration |
| Customer data deletion is verified | Deletion job counts and verification timestamp | Implemented | Public provenance is intentionally retained |
| Bounded-source metrics are measurable | Fixture evaluation harness | Implemented with seeded fixture | Live pilot evidence is not represented by seeded results |

No claim in this ledger represents legal or regulatory compliance.
