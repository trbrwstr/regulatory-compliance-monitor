# Source register and data rights

## Register status

This register is intentionally bounded. RCM-001 must name the first vertical, jurisdiction set, accountable reviewer, and freshness objective before production source expansion.

| Source | Type | Terms / attribution | Freshness target | Known gap |
|---|---|---|---|---|
| Federal Register API | Official API | Preserve Federal Register attribution and source URL | Hourly | API availability and publication lag |
| Configured RSS feeds | Official/agency feed | Preserve feed attribution and linked item URL | 30 minutes | Feed schema drift and incomplete history |
| Configured state sites | Official HTML | Preserve agency attribution and source URL | 4 hours | Generic parser may miss layout-specific changes |

## Data rights

Official source content remains attributed to its publisher and is retained only as provenance needed to reconstruct displayed changes. Customer-owned subscribers, review notes, preferences, and derived decisions are exportable and eligible for deletion. Deletion retains public-source provenance and the minimum audit evidence needed to verify the deletion job.

## Consent and retention

Notification recipients require explicit subscription and active status. Retention policies must be set per tenant. Public-source snapshots are not deleted by customer-data deletion because doing so would break reproducibility; this boundary is reported in the deletion response.
