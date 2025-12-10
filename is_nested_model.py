import json
import os
import sys
from collections import defaultdict
from typing import List

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm

load_dotenv()
class IsNeighbourResponse(BaseModel):
    answer: List[bool] = Field(
        ...,
        description="A list of boolean values indicating whether the function G_i is nested within function F."
    )


# ---------------------------------------------------------------------
# Prompt (system + human)
# ---------------------------------------------------------------------
# SYSTEM_PROMPT = """
# You will be given two function (F and G) information including their descriptions, parameters, response info etc. Your task is to determine whether the two functions can be nested, meaning the function G can be called after function F?
# Definition of Nested Functions:
# 1. Nested function is definitely a neighbour function but a neighbour function is not always nested.
# 2. Two functions are considered nested if the second function can be called immdeiately after the first function because some parameter values required by the second function can be obtained from the output of the first function.
# Illustrative Examples:
# 1. For example, when the first function is convert_usd_from_rmb(rmb_number=), and the second function is set_budget_limit(budget_limit_in_usd=). The two functions are nested because set_budget_limit needs a parameter value in dollars and convert_usd_from_rmb could output a dollar value.
# 2. As another example, when the first function is get_airport_symbol_by_city(city=,range=), the second function get_flight_by_airport(airport_symbol=). The two functions are nested because the second function needs a symbol of airport while the first function provides that in the output
# """

# HUMAN_PROMPT = """
# Function F:
# {function_f}

# Function G:
# {function_g}

# Now, identify whether the function G is nested with function F based on the criteria mentioned in the system prompt. Output your answer as a JSON object: {{"answer": true or false}}
# """

SYSTEM_PROMPT = """
You will be given one function F and a list of neighbour functions [G1, G2...Gn] with their descriptions, parameters, response info etc. Your task is to determine which of the Gi function can be nested with nested with Function F, meaning the function Gi can be called after function F?
Definition of Nested Functions:
1. Nested function is definitely a neighbour function but a neighbour function is not always nested.
2. Two functions are considered nested if the second function can be called immdeiately after the first function because some parameter values required by the second function can be obtained from the output of the first function.
Illustrative Examples:
1. For example, when the first function is convert_usd_from_rmb(rmb_number=), and the second function is set_budget_limit(budget_limit_in_usd=). The two functions are nested because set_budget_limit needs a parameter value in dollars and convert_usd_from_rmb could output a dollar value.
2. As another example, when the first function is get_airport_symbol_by_city(city=,range=), the second function get_flight_by_airport(airport_symbol=). The two functions are nested because the second function needs a symbol of airport while the first function provides that in the output

Always return a list of booleans where result[i] == true iff Gi can be nested after F.

"""

HUMAN_PROMPT = """
Function F:
{function_f}

List of Functions Gi:
{function_g}

Now, identify which function Gi can be nested with function F based on the criteria mentioned in the system prompt. Output your answer as a JSON object: {{"answer": [true/false, .. ,...]}}
"""


# ---------------------------------------------------------------------
# LLM factory (4 options: openai, gemini, vllm, deepseek)
# ---------------------------------------------------------------------
def make_llm(provider: str, model_name: str, temperature: float, base_url: str | None):
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=0.1,
        check_every_n_seconds=0.1,
        max_bucket_size=10,
    )

    provider = provider.lower()

    if provider == "openai":
        # Hard-restrict to gpt-4o / gpt-5 if you want
        if model_name not in {"gpt-4o", "gpt-5"}:
            raise ValueError("For provider 'openai', model must be one of: gpt-4o, gpt-5")

        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_retries=2,
            # rate_limiter=rate_limiter,
        )

    elif provider == "gemini":
        if model_name != "gemini-2.0-flash" and model_name != "gemini-2.5-flash":
            raise ValueError("For provider 'gemini', model must be 'gemini-2.0-flash' or 'gemini-2.5-flash'")

        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            rate_limiter=rate_limiter,
        )

    elif provider == "vllm":
        if not base_url:
            raise ValueError("For provider 'vllm', you must supply --base-url (OpenAI-compatible endpoint).")

        # Assumes an OpenAI-compatible endpoint exposed by vLLM.
        # Use VLLM_API_KEY or fall back to a dummy key if not needed.
        api_key = os.getenv("VLLM_API_KEY", "EMPTY")

        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_retries=2,
            base_url=base_url,
            api_key=api_key,
        )

    elif provider == "deepseek":
        # Assumes an OpenAI-compatible endpoint for DeepSeek.
        # Use DEEPSEEK_API_KEY or fall back to a dummy key if not needed.
        api_key = os.getenv("DEEPSEEK_API_KEY", "EMPTY")

        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_retries=2,
            base_url="https://api.deepseek.com/v1",
            api_key=api_key,
        )

    else:
        raise RuntimeError(f"Unsupported provider: {provider}")


def build_chain(provider: str, model_name: str, temperature: float, base_url: str | None):
    llm = make_llm(provider, model_name, temperature, base_url)
    
    if provider.lower() == "deepseek":
        # DeepSeek doesn't support structured output, so use raw LLM
        model = llm
    else:
        model = llm.with_structured_output(IsNeighbourResponse)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    # LangChain Runnable: dict -> response (IsNeighbourResponse or str for DeepSeek)
    chain = prompt | model
    return chain