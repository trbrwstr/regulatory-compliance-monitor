from openai import AsyncOpenAI

from config import get_settings


class RegulationSummarizer:
    """Uses GPT-4 to generate plain-English impact summaries of regulatory updates."""

    SYSTEM_PROMPT = """You are a regulatory compliance expert. Your job is to analyze regulatory 
documents and produce clear, plain-English summaries that help businesses understand:

1. What the regulation says (in simple terms)
2. Who it affects (which industries, company sizes, etc.)
3. What actions businesses need to take
4. Key deadlines and effective dates
5. Potential penalties for non-compliance

Keep summaries concise (3-5 paragraphs max). Use bullet points for action items.
Avoid legal jargon - write for a business owner or compliance officer who needs to 
quickly understand if this regulation affects them and what they need to do."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def summarize(self, title: str, abstract: str, raw_content: str = "") -> dict:
        """Generate a plain-English summary and impact assessment."""
        content_to_analyze = f"Title: {title}\n\nAbstract: {abstract}"
        if raw_content:
            content_to_analyze += f"\n\nFull Content (excerpt): {raw_content[:4000]}"

        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"""Analyze this regulatory update and provide:
1. A plain-English summary
2. Impact level (high/medium/low)
3. Affected industries

Regulatory Document:
{content_to_analyze}""",
                },
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        summary_text = response.choices[0].message.content
        impact_level = self._extract_impact_level(summary_text)

        return {
            "summary": summary_text,
            "impact_level": impact_level,
        }

    async def classify_industry(self, title: str, abstract: str) -> list[str]:
        """Classify which industries a regulation affects."""
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You classify regulatory documents by affected industry. "
                    "Respond with ONLY a comma-separated list from these options: "
                    "fintech, healthcare, food_service, general. No other text.",
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\nAbstract: {abstract}",
                },
            ],
            temperature=0.1,
            max_tokens=50,
        )

        industries_text = response.choices[0].message.content.strip().lower()
        valid_industries = {"fintech", "healthcare", "food_service", "general"}
        industries = [i.strip() for i in industries_text.split(",") if i.strip() in valid_industries]

        return industries if industries else ["general"]

    def _extract_impact_level(self, summary: str) -> str:
        """Extract impact level from the summary text."""
        summary_lower = summary.lower()
        if "impact level: high" in summary_lower or "high impact" in summary_lower:
            return "high"
        elif "impact level: low" in summary_lower or "low impact" in summary_lower:
            return "low"
        return "medium"
