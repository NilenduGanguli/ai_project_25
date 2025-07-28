from typing import Optional, List


BASE_SENTIMENT_PROMPT = """You are an expert sentiment analyst with advanced natural language processing capabilities.

Your task is to analyze the sentiment and emotional tone of the provided text. Focus on:
- Overall emotional valence (positive, negative, neutral)
- Confidence in your assessment
- Key indicators that support your determination

Always respond with proper markdown formatting when providing explanations."""


MULTIMODAL_SENTIMENT_EXTENSION = """
You have multimodal capabilities and can analyze documents directly, including:
- Text content and comprehensive emotional analysis
- Visual elements like charts, graphs, images that may convey emotional context
- Document layout and formatting that might indicate tone
- Combined textual and visual sentiment indicators

When analyzing multimodal content, consider how visual elements complement or modify the textual sentiment."""


VECTOR_SENTIMENT_EXTENSION = """
You specialize in text-based sentiment analysis and emotional tone detection.

Focus on extracting meaningful emotional indicators from textual content, identifying:
- Explicit emotional language and sentiment-bearing words
- Implicit emotional cues and contextual sentiment
- Overall emotional tone and intensity
- Balanced assessment of mixed sentiments"""


def _get_base_sentiment_prompt() -> str:
    return """Analyze the sentiment and provide:
- sentiment: one of 'positive', 'negative', or 'neutral'
- score: confidence score between 0 and 1 (how confident you are in this sentiment classification)
- summary: a brief 1-2 sentence explanation of why you determined this sentiment, highlighting key emotional indicators"""


def build_sentiment_prompt(base: str = BASE_SENTIMENT_PROMPT, extensions: Optional[List[str]] = None) -> str:
    if extensions is None:
        extensions = []

    prompt_parts = [base.strip()]

    for extension in extensions:
        if extension and extension.strip():
            prompt_parts.append(extension.strip())

    prompt_parts.append(_get_base_sentiment_prompt())

    return "\n\n".join(prompt_parts)


def get_multimodal_sentiment_prompt() -> str:
    return build_sentiment_prompt(
        extensions=[MULTIMODAL_SENTIMENT_EXTENSION]
    )


def get_text_sentiment_prompt() -> str:
    return build_sentiment_prompt(
        extensions=[VECTOR_SENTIMENT_EXTENSION]
    )


def get_custom_sentiment_prompt(extensions: List[str]) -> str:
    return build_sentiment_prompt(extensions=extensions)
