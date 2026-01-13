"""
LLM configuration for CrewAI agents.
All agents use GPT-4o for best Hebrew language support.
"""
from langchain_openai import ChatOpenAI
from config import settings

def get_gpt4o(temperature=0.3):
    """
    Get GPT-4o instance for CrewAI agents.

    Args:
        temperature: Controls randomness (0-1). Lower = more consistent.
                    Default 0.3 for reliable parsing.

    Returns:
        ChatOpenAI instance configured for GPT-4o
    """
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=temperature,
        openai_api_key=settings.OPENAI_API_KEY
    )


def get_creative_gpt4o():
    """Get GPT-4o with higher temperature for creative responses."""
    return get_gpt4o(temperature=0.7)


def get_deterministic_gpt4o():
    """Get GPT-4o with very low temperature for deterministic outputs."""
    return get_gpt4o(temperature=0.1)
