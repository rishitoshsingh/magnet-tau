"""Shared LLM call utilities.

Uses litellm Router with RetryPolicy and cooldowns so all agents automatically
handle rate-limit errors without manual sleep/retry loops.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from litellm import Router
from litellm.router import RetryPolicy

# One Router instance per (full_model_key, api_base).
# Routers are cheap to create but hold retry state, so caching them lets the
# cooldown logic accumulate correctly across calls within a run.
_routers: Dict[Tuple[str, Optional[str]], Router] = {}


def _get_router(full_model: str, api_base: Optional[str]) -> Router:
    key = (full_model, api_base)
    if key not in _routers:
        litellm_params: Dict[str, Any] = {"model": full_model}
        if api_base:
            litellm_params["api_base"] = api_base

        _routers[key] = Router(
            model_list=[
                {
                    "model_name": full_model,
                    "litellm_params": litellm_params,
                }
            ],
            retry_policy=RetryPolicy(
                RateLimitErrorRetries=6,
                InternalServerErrorRetries=3,
                TimeoutErrorRetries=2,
            ),
            num_retries=6,
            retry_after=30,       # minimum seconds between retries
            disable_cooldowns=True,  # cooldowns require multiple deployments; with one model they block all calls
        )
    return _routers[key]


def completion_with_retry(
    model: str,
    custom_llm_provider: Optional[str] = None,
    api_base: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """Drop-in replacement for litellm.completion with Router-based retry + cooldown.

    Accepts the same signature as litellm.completion.  When custom_llm_provider is
    given and not already embedded in model, it is prepended (e.g. "openai/gpt-4o").
    """
    if custom_llm_provider and "/" not in model:
        full_model = f"{custom_llm_provider}/{model}"
    else:
        full_model = model

    router = _get_router(full_model, api_base)
    return router.completion(model=full_model, **kwargs)
