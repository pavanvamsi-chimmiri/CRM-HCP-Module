from pydantic import BaseModel, Field

from app.ai.groq_service import get_groq_service
from app.ai.tools.base import BaseToolOutput, ToolContext, ToolError
from app.core.logging import get_logger
from app.models import Sentiment

logger = get_logger(__name__)

SENTIMENT_PROMPT = """Analyze the sentiment of this healthcare professional (HCP) interaction text.

Classify sentiment as one of: positive, neutral, negative, mixed

Respond ONLY with valid JSON:
{{
  "sentiment": "positive|neutral|negative|mixed",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>",
  "indicators": ["<phrase or signal>"]
}}

Text to analyze:
{text}
"""


class SentimentInput(BaseModel):
    text: str = Field(min_length=1, description="Interaction notes, outcome, or conversation text")


class SentimentOutput(BaseToolOutput):
    sentiment: Sentiment | None = None
    confidence: float = 0.0
    reasoning: str = ""
    indicators: list[str] = Field(default_factory=list)


class SentimentTool:
    """Detect doctor/HCP sentiment from interaction text."""

    name = "detect_sentiment"
    description = (
        "Detect the sentiment of a doctor interaction from notes or conversation text. "
        "Returns structured JSON with sentiment, confidence, and reasoning."
    )

    @classmethod
    async def execute(cls, ctx: ToolContext, input_data: SentimentInput) -> SentimentOutput:
        del ctx  # Independent LLM tool; no DB required

        try:
            groq = get_groq_service()
            prompt = SENTIMENT_PROMPT.format(text=input_data.text)
            parsed = groq.invoke_json(prompt, fallback={})

            sentiment_value = parsed.get("sentiment")
            sentiment: Sentiment | None = None
            if sentiment_value:
                try:
                    sentiment = Sentiment(sentiment_value)
                except ValueError:
                    sentiment = None

            confidence = float(parsed.get("confidence", 0.0))
            reasoning = parsed.get("reasoning", "")
            indicators = parsed.get("indicators", [])

            if sentiment is None:
                return SentimentOutput(
                    success=False,
                    message="Could not detect sentiment",
                    errors=[ToolError(code="INVALID_SENTIMENT", message="Model returned invalid sentiment")],
                )

            logger.info("tool_sentiment_success", sentiment=sentiment.value, confidence=confidence)

            return SentimentOutput(
                success=True,
                message="Sentiment detected successfully",
                sentiment=sentiment,
                confidence=confidence,
                reasoning=reasoning,
                indicators=indicators,
            )

        except Exception as exc:
            logger.error("tool_sentiment_failed", error=str(exc))
            return SentimentOutput(
                success=False,
                message="Failed to detect sentiment",
                errors=[ToolError(code="SENTIMENT_FAILED", message=str(exc))],
            )
