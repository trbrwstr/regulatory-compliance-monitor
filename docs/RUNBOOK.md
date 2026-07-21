# Operations runbook

## Review a new item

1. Check the source URL, snapshot hash, and citation location.
2. Review the deterministic diff and draft summary.
3. Correct or reject unsupported claims.
4. Approve only when the item is within the bounded source register.
5. Verify delivery records and audit events after approval.

## Source failure

- Inspect source health, last successful fetch, and error state.
- Do not manually mark a broken source complete.
- Record the missing-source period in evaluation output.
- Use the preserved prior snapshot and deterministic diff after recovery.

## Provider or mail outage

- Continue reviewing the deterministic/manual summary.
- Do not bypass approval to send an alert.
- Retry failed delivery only after checking the idempotent delivery key.

## Export and deletion

- Require tenant and reviewer authorization.
- Run `/api/data/export` before deletion when the customer requests a copy.
- Run the deletion operation and retain its verified counts.
- Confirm that customer records were removed and public provenance remains available for reproducibility.

## Rollback

Stop the scheduler before schema or adapter rollback. Restore the database and source snapshot history from the encrypted backup procedure, verify review and delivery state, then resume scheduled jobs. Never delete snapshots to hide a bad parse or incorrect summary.
