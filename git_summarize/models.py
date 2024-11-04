from .openrouter_models import get_openrouter_models

def get_supported_models(refresh: bool = False) -> list[str]:
    """Get list of supported models including OpenRouter models."""
    models = ["gpt-3.5-turbo"]  # Default OpenAI model
    openrouter_models = get_openrouter_models(refresh)
    return models + openrouter_models

FAVORITE_MODELS = [
    "gpt-3.5-turbo",
    "openrouter/nvidia/llama-3.1-nemotron-70b-instruct",
    "openrouter/qwen/qwen-2.5-72b-instruct",
    "openrouter/anthropic/claude-3.5-sonnet",
    "openrouter/deepseek/deepseek-chat",
    "openrouter/meta-llama/llama-3-70b-instruct",
    "openrouter/anthracite-org/magnum-v4-72b"
]
