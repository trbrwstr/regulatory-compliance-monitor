# Model and provider card

## OpenAI summarization

- **Purpose:** Optional draft summarization and industry classification.
- **Inputs:** Source title, abstract, and bounded content excerpt.
- **Outputs:** Draft summary, impact label, and industry candidates.
- **Authority:** The provider cannot approve, determine legal obligations, select recipients, or send notifications.
- **Fallback:** When unavailable or unconfigured, the system stores a deterministic source-based draft and continues the review workflow.
- **Validation:** Provider output is treated as untrusted text and requires citation-backed human review.
- **Data handling:** API credentials are environment variables; do not place secrets in exports or logs.

## SendGrid delivery

- **Purpose:** Deliver approved notifications.
- **Inputs:** Approved regulation summary, source URL, effective date, and recipient address.
- **Authority:** Delivery cannot occur for draft or rejected regulations.
- **Reliability:** Delivery records use a deterministic regulation/subscriber key to avoid replay duplicates; failures remain visible.
