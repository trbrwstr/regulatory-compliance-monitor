# Threat model

| Threat | Control | Evidence / residual risk |
|---|---|---|
| SSRF or hostile redirect | HTTPS-only allowlist, DNS private-address rejection, redirects disabled | Source adapter tests; DNS rebinding remains an infrastructure concern |
| Prompt injection in fetched content | Source content is data, not instructions; provider is optional and isolated | Summarizer prompt and fallback; provider output still requires review |
| Malicious oversized or invalid payload | Content-type allowlist and 5 MiB response limit | Adapter contract tests |
| Cross-tenant access | Tenant context is required on data-control endpoints; production auth must replace header identity | Header identity is an MVP boundary and must not be treated as complete IAM |
| Duplicate notification | Unique delivery key per regulation/subscriber | Database uniqueness and scheduler replay check |
| Forged approval | API key, reviewer role, reviewer ID, citation requirement, and audit event | Full token/session auth remains a follow-up hardening item |
| Secrets leakage | Environment-only configuration; exports omit secrets | Operators must avoid logging environment values |
| Misleading all-clear | Explicit source health and missing-source evaluation fields | Health aggregation remains an operational follow-up |
