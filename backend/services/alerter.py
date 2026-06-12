from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime, timezone

from config import get_settings


class AlertService:
    """Sends email alerts to subscribers via SendGrid."""

    def __init__(self):
        settings = get_settings()
        self.client = SendGridAPIClient(settings.sendgrid_api_key)
        self.from_email = settings.sendgrid_from_email

    def send_alert(self, to_email: str, to_name: str, regulation: dict) -> dict:
        """Send a single alert email about a regulatory update."""
        subject = f"🔔 Regulatory Alert: {regulation['title'][:80]}"

        html_content = self._build_email_html(regulation, to_name)

        message = Mail(
            from_email=Email(self.from_email, "Regulatory Compliance Monitor"),
            to_emails=To(to_email, to_name),
            subject=subject,
            html_content=Content("text/html", html_content),
        )

        try:
            response = self.client.send(message)
            return {
                "status": "sent",
                "status_code": response.status_code,
                "sent_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
            }

    def send_batch_alerts(self, subscribers: list[dict], regulation: dict) -> list[dict]:
        """Send alerts to multiple subscribers for a single regulation."""
        results = []
        for subscriber in subscribers:
            result = self.send_alert(
                to_email=subscriber["email"],
                to_name=subscriber["name"],
                regulation=regulation,
            )
            result["subscriber_email"] = subscriber["email"]
            results.append(result)
        return results

    def _build_email_html(self, regulation: dict, recipient_name: str) -> str:
        """Build the HTML email content."""
        impact_color = {
            "high": "#DC2626",
            "medium": "#D97706",
            "low": "#059669",
        }.get(regulation.get("impact_level", "medium"), "#6B7280")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                       line-height: 1.6; color: #1F2937; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1E3A5F, #2563EB); color: white; 
                          padding: 24px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #F9FAFB; padding: 24px; border: 1px solid #E5E7EB; }}
                .impact-badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px;
                               color: white; font-size: 12px; font-weight: 600; 
                               background-color: {impact_color}; }}
                .summary {{ background: white; padding: 16px; border-radius: 8px; 
                          border-left: 4px solid #2563EB; margin: 16px 0; }}
                .footer {{ padding: 16px; text-align: center; color: #6B7280; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 10px 20px; background: #2563EB; 
                       color: white; text-decoration: none; border-radius: 6px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 20px;">⚖️ Regulatory Compliance Alert</h1>
                <p style="margin: 8px 0 0; opacity: 0.9;">New regulation may affect your business</p>
            </div>
            <div class="content">
                <p>Hi {recipient_name},</p>
                <h2 style="font-size: 18px; color: #1E3A5F;">{regulation.get('title', 'Regulatory Update')}</h2>
                <p><span class="impact-badge">Impact: {regulation.get('impact_level', 'medium').upper()}</span></p>
                
                <div class="summary">
                    <h3 style="margin-top: 0;">Plain-English Summary</h3>
                    <p>{regulation.get('summary', regulation.get('abstract', 'No summary available.'))}</p>
                </div>

                {f'<p><strong>Effective Date:</strong> {regulation["effective_date"]}</p>' if regulation.get('effective_date') else ''}
                {f'<p><a class="btn" href="{regulation["source_url"]}">View Full Document →</a></p>' if regulation.get('source_url') else ''}
            </div>
            <div class="footer">
                <p>You received this because you're subscribed to regulatory updates.</p>
                <p>Regulatory Compliance Monitor</p>
            </div>
        </body>
        </html>
        """
