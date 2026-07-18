"""LLM provider abstractions for the industrial test agent."""

from .provider import LLMProvider
from .providers.mock import MockLLMProvider

__all__ = ["LLMProvider", "MockLLMProvider"]
