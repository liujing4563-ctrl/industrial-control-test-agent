from .provider import LLMProvider
from .providers.mock import MockLLMProvider


def create_provider(provider_name: str = "mock") -> LLMProvider:
    if provider_name == "mock":
        return MockLLMProvider()
    raise ValueError(f"Unsupported provider: {provider_name}")
