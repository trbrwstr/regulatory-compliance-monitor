# Diligence index

| Area | Artifact |
|---|---|
| Architecture and data flow | `docs/ARCHITECTURE.md` |
| Threat model and controls | `docs/THREAT_MODEL.md` |
| Source register and data rights | `docs/SOURCE_REGISTER.md` |
| Model and provider card | `docs/PROVIDER_CARD.md` |
| Claims and evidence boundaries | `docs/CLAIMS_LEDGER.md` |
| Operations and rollback | `docs/RUNBOOK.md` |
| Evaluation fixture and metrics | `backend/evaluation_fixtures.json`, `backend/evaluation.py` |
| Qualified pilot protocol and API | `docs/PILOT_PROTOCOL.md`, `backend/routers/pilot.py`, `backend/services/pilot.py` |
| Additive schema migration support | `backend/migrations.py` |
| Machine-readable export and verified deletion | `backend/routers/data_controls.py`, `backend/services/data_lifecycle.py` |
| Data model and provenance entities | `backend/models.py` |

Seeded evaluation output must be labeled as fixture evidence. Live pilot evidence requires a qualified reviewer and parallel manual-monitoring record.
