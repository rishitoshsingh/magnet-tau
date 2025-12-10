import argparse
import json
import os
from collections import defaultdict
from typing import List

# ---------------------------------------------------------------------
# Tau-bench imports
# ---------------------------------------------------------------------
# Make sure we can import tau_bench from the repo root
import tau_bench.envs.airline.tools as airline_tools
import tau_bench.envs.retail.tools as retail_tools
import tau_bench.envs.telecom.tools as telecom_tools
import tau_bench.envs.telehealth.tools as telehealth_tools
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm

load_dotenv()

# ---------------------------------------------------------------------
# Structured output schema for neighbour classification
# ---------------------------------------------------------------------
class IsNeighbourResponse(BaseModel):
    answer: List[bool] = Field(
        ...,
        description=(
            "A list of boolean values indicating whether each candidate function "
            "is a neighbour of the target function. True if neighbour, False otherwise."
        ),
    )
    reason: List[str] = Field(
        ...,
        description=(
            "A list of detailed reasoning strings for each candidate function, "
            "explaining why it is or isn't a neighbour."
        ),
    )


# ---------------------------------------------------------------------
# Prompt (system + human)
# ---------------------------------------------------------------------
SYSTEM_PROMPT = """
You are an expert software engineer who can analyze API functions and determine relationships between them. Your task is to identify which candidate functions are related to a given target function based on their input-output relationships.
You will be provided with a target function and a list of candidate functions. Your job is to determine which candidate functions can be considered 'neighbours' of the target function meaning the candidate function can be called in a scenario based on the following criteria:
1) The output of the target function is used as input to the candidate function.
2) The output of the target function is part of the input to the candidate function.
3) The output of the target function directly influences the execution of the candidate function, for example consides a function to buy a product Buy(['Bat','Pad']) will need to use Calculate() that execute the expression and give the total amount due, and that calculate can be the last function to be called.

The functions given will be part of a customer service automation system. Analyze the function signatures and descriptions carefully to determine the relationships. Some functions can't have incoming edges, like
Some guidelines for some functions:
1) FindUserByEmail, FindUserByZIP, GetUserDetails, etc, as they are entry point for the system meaning no incoming edges as these are used to authenitcate the user.
2) All functions need user authentication meaning, other than FindUserByEmail, FindUserByZIP, GetUserDetails, etc, all other functions will have at least one incoming edge. This will ensure that before calling all other functions user is authenticated.
3) TransferToHumanAgent functions can't have any outgoing edges as they are called only when the user is not satisfied with the bot response, Thus they will only have incoming edges.

Your output will be used to build a graph of function relationships, which will be used to generate random customer service scenarios. You need to give me: 
1) list of boolean values indicating whether each candidate function is a neighbour of the target function based on the criteria mentioned above.
2) list of detailed reasoning for each candidate function on why it is or isn't a neighbour of the target function, what scenario you thought of while analyzing the functions.

REMEMBER that:
- The length of both lists must be equal to the number of candidate functions given.
- The order of boolean values and reasoning must correspond to the order of candidate functions provided.
- There can't be a self edge: the target function must not be considered its own neighbour.
"""

HUMAN_PROMPT = """
Target Function:
{target_function}

Candidate Functions:
{candidate_functions}

Now, identify which candidate functions are neighbours of the Target Function based on the criteria already defined and return the response in the exact structured format:
- answer: list[bool]
- reason: list[str]
"""


# ---------------------------------------------------------------------
# LLM factory (3 options: openai, gemini, vllm)
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
            rate_limiter=rate_limiter,
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

    else:
        raise RuntimeError(f"Unsupported provider: {provider}")


def build_neighbour_chain(provider: str, model_name: str, temperature: float, base_url: str | None):
    llm = make_llm(provider, model_name, temperature, base_url)
    model = llm.with_structured_output(IsNeighbourResponse)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    # LangChain Runnable: dict -> IsNeighbourResponse
    chain = prompt | model
    return chain


# ---------------------------------------------------------------------
# Tau-bench tool collection
# ---------------------------------------------------------------------
def get_taubench_tools(skip=["think", "calculate"]):
    domain_names = ["airline", "retail", "telecom", "telehealth"]
    tools_by_domain = defaultdict(list)

    for d_title, d_tools in zip(
        domain_names, [airline_tools, retail_tools, telecom_tools, telehealth_tools]
    ):
        for cls in d_tools.ALL_TOOLS:
            if cls.__name__.lower() in skip:
                print(f"Skipping tool: {cls.__name__}")
                continue
            tool = {
                "name": cls.__name__,
                "info": cls.get_info(),
            }
            tools_by_domain[d_title].append(tool)

    return tools_by_domain


# ---------------------------------------------------------------------
# Adjacency matrix builder – uses the chain directly
# ---------------------------------------------------------------------
def build_adjacency_matrix(tools, neighbour_chain):
    """
    tools: list[dict] from get_taubench_tools()[domain]
    neighbour_chain: LangChain runnable returning IsNeighbourResponse
    """
    results = {
        "tools": tools,
        "adjacency_matrix": [],  # list[list[bool]]
        "reason_matrix": [],     # list[list[str]]
    }

    for tool in tqdm(tools, desc="Finding neighbours"):
        result: IsNeighbourResponse = neighbour_chain.invoke(
            {
                "target_function": tool,
                "candidate_functions": tools,
            }
        )
        results["adjacency_matrix"].append(result.answer)
        results["reason_matrix"].append(result.reason)

    return results


# ---------------------------------------------------------------------
# Main CLI entrypoint
# ---------------------------------------------------------------------
def main(domains: list[str], provider: str, model_name: str, temperature: float, base_url: str | None):
    # still set envs if some downstream code expects them
    os.environ["model_name"] = model_name
    os.environ["temperature"] = str(temperature)

    neighbour_chain = build_neighbour_chain(provider, model_name, temperature, base_url)

    tau_tools = get_taubench_tools()
    base_output_dir = os.path.join("output", f"{provider}_{model_name}")
    os.makedirs(base_output_dir, exist_ok=True)

    for domain, tools in tau_tools.items():
        if domain not in domains:
            continue

        print(f"Building adjacency matrix for domain: {domain} with {len(tools)} tools")
        results = build_adjacency_matrix(tools, neighbour_chain)

        out_path = os.path.join(
            base_output_dir,
            f"{domain}_adjacency_matrix_{temperature}.json",
        )
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Adjacency matrix for domain: {domain} saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build tool neighbour adjacency matrices using LLM.")
    parser.add_argument(
        "--domains", 
        nargs="+",
        type=str,
        default=["airline", "retail", "telecom", "telehealth"],
        help="List of domains to process (default: all four).",
    )
    parser.add_argument(
        "--provider",
        type=str,
        required=True,
        choices=["openai", "gemini", "vllm"],
        help="LLM provider: openai | gemini | vllm (OpenAI-compatible, hosted via vLLM).",
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model name. For openai: gpt-4o/gpt-5; for gemini: gemini-2.0-flash; for vllm: any model name your server exposes.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Sampling temperature for the model.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Base URL for OpenAI-compatible vLLM server (required when provider=vllm).",
    )
    args = parser.parse_args()
    print(args)
    main(args.domains, args.provider, args.model, args.temperature, args.base_url)