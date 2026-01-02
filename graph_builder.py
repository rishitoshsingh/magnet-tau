import argparse
import json
import os
from collections import defaultdict
from typing import List

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.rate_limiters import InMemoryRateLimiter

# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from tau_bench.envs.airline.wiki import WIKI as AIRLINE_WIKI
from tau_bench.envs.retail.wiki import WIKI as RETAIL_WIKI
from tau_bench.envs.telecom.wiki import WIKI as TELECOM_WIKI
from tau_bench.envs.telehealth.wiki import WIKI as TELEHEALTH_WIKI
from tqdm import tqdm

# ---------------------------------------------------------------------
# Tau-bench imports
# ---------------------------------------------------------------------
# Make sure we can import tau_bench from the repo root
import tracer.envs.airline.tools as airline_tools
import tracer.envs.retail.tools as retail_tools
import tracer.envs.telecom.tools as telecom_tools
import tracer.envs.telehealth.tools as telehealth_tools

load_dotenv()

# ---------------------------------------------------------------------
# Structured output schema for neighbour classification
# ---------------------------------------------------------------------
# class IsNeighbourResponse(BaseModel):
#     answer: List[bool] = Field(
#         ...,
#         description=(
#             "A list of boolean values indicating whether each candidate function "
#             "is a neighbour of the target function. True if neighbour, False otherwise."
#         ),
#     )
#     reason: List[str] = Field(
#         ...,
#         description=(
#             "A list of detailed reasoning strings for each candidate function, "
#             "explaining why it is or isn't a neighbour."
#         ),
#     )

class IsNeighbourResponse(BaseModel):
    answer: List[bool] = Field(
        ...,
        description=(
            "A list of boolean values indicating whether each candidate function "
            "is a logical neighbour of the target function. True if neighbour, False otherwise. "
            "Order and length must match the provided candidate_functions list."
        ),
    )
    reason: List[str] = Field(
        ...,
        description=(
            "A list of concise reasoning strings (1–3 sentences each) corresponding to each candidate. "
            "For a candidate marked True, the reason must state the realistic customer/agent scenario "
            "that makes the follow-up plausible and explicitly list the specific inputs the user "
            "would need to provide (or that the agent can obtain immediately) to call the candidate tool "
            "(e.g., order_id, account_id, record_id). For a candidate marked False, briefly "
            "explain why the follow-up is implausible (mismatched intent, high cost without trigger, "
            "edge-case only, etc.)."
        ),
    )
    is_root: bool = Field(
        ...,
        description=(
            "Boolean indicating whether the target function can act as a root (entry-point) in a "
            "customer-support interaction. True only if the function can reasonably be the agent's "
            "first meaningful action and its required inputs are naturally available at the start of "
            "an interaction (provided directly by the customer or obtainable without other tool calls)."
        ),
    )
    is_root_reason: str = Field(
        ...,
        description=(
            "A brief justification (1–3 sentences) for the is_root decision. If True, explain why the "
            "function is callable as a first action and what inputs are typically available; if False, "
            "explain which prerequisite steps or inputs are usually required before this function can be called."
        ),
    )

# ---------------------------------------------------------------------
# Prompt (system + human)
# ---------------------------------------------------------------------
SYSTEM_PROMPT = """
You are an expert software engineer and product-minded conversation designer. Your job is to analyze a single **target_function** and a list of **candidate_functions** (all part of a customer-service automation system) and decide which candidate functions should be considered **logical neighbours** of the target function.

Crucial framing
Imagine a real customer contacting support with a specific problem or request that would cause the agent to use the **target_function** as the primary action for that turn. Judgments must be made from the perspective of the customer’s intent and an agent’s practical workflow. Do **not** require that the target’s outputs map mechanically to candidate inputs — ignore any I/O-mapping rule. Use common sense and agent workflow logic to determine plausibility across any business domain.

Inputs you will receive
• `target_function`: signature, short description, and response schema.
• `candidate_functions`: ordered list of functions; each has signature, short description, and response schema.
• `domain_wiki` (optional): a short domain knowledge note (use it only to resolve ambiguous business rules).

Few functions will be ommitted from the candidate list; like functions used for authentication and getting the customer deatils, which will be called by the agent as a prerequisite step before calling any domain specific function, so assume that such prerequisite steps have already been taken care of by the agent.

Decision rules (apply in order)
1. Customer-intent & agent-flow (primary): For each candidate, ask whether there exists a realistic, commonly encountered customer-support scenario in which the agent would plausibly call that candidate **immediately after** the target. Think: the customer’s goal, what the agent must do next, and which follow-ups are routine (confirm, change, cancel, refund, compensate, rebook, correct, verify, escalate).
2. Temporal & cost sensitivity: High-friction, costly, or terminal actions (e.g., full cancellations, large refunds, full rebookings, irreversible state changes) require strong, common-sense justification to be neighbours. Prefer conservative linking for such actions.
3. Edge-case exclusion: Do not mark a neighbour if the only plausible justification depends on rare, contrived, or internal/admin scenarios (debugging, system recovery, race conditions). Prefer not connecting unless the follow-up is a normal, customer-facing step.
4. Independent evaluation: Evaluate each candidate **only** in the context of the current target and a single realistic customer interaction. You will be invoked repeatedly with different targets; reciprocal links may appear across runs — that is expected.
5. Use `domain_wiki` only to resolve ambiguous business rules. If the wiki contradicts your intuition, follow the wiki.


Root eligibility (how to judge is_root)

Decide whether the target_function itself can be a realistic root (entry-point) for a customer support interaction.
A function is a root only if all of the following are true:
• A customer could reasonably initiate contact with a problem or request whose first meaningful agent action would be to call this function.
• The function does not require implicit, multi-step prerequisite workflows outside a normal single support turn (e.g., full search + selection + pricing flows, complex eligibility checks, or back-office approvals).
• All required inputs for the function are either human-facing or deterministically derivable, meaning:
	•	The input is typically provided directly by customers or easily stated in natural language (e.g., order number, account id, email, phone number, product name, commonly known SKU), or
	•	The input is not human-facing but can be unambiguously and deterministically derived from the provided domain_wiki using the human-facing inputs (e.g., fixed mappings, documented business rules, or guaranteed lookups described in the wiki).

A function must be marked not a root if:
• It requires internal-only identifiers (opaque database ids, internal product ids, record ids) that customers do not know and that cannot be reliably derived from the domain_wiki.
• It assumes prior discovery, selection, or context that is normally established through other domain-specific tools.
• Deriving required inputs would involve ambiguity, probabilistic inference, or additional multi-step discovery.

If it is unclear whether required inputs are human-facing or safely derivable, prefer is_root = false and explicitly state which inputs or prerequisite steps prevent root eligibility.

Important clarifications:
• **Internal-only identifiers** (internal database ids, internal `product_id`, opaque record ids) are **not** considered human-facing. If a function requires only internal identifiers and there is no declared lightweight helper (e.g., `search_by_name`) in `omitted_tools_light`, mark the function **not** a root.
• If you are given a list `omitted_tools_light` (routine helpers like authenticate, ask_identifier, search_by_name), treat those helpers as single-turn clarifying steps the agent can perform; they do **not** disqualify a function from being a root. If `omitted_tools_heavy` contains required helpers, treat those as multi-step prerequisites that disqualify a function from being a root unless strong justification exists.
• If tool metadata includes `user_facing_inputs`, prefer that authoritative information when judging root eligibility.

If it is ambiguous whether inputs are human-facing, prefer `is_root = false` and explain which prerequisites or discovery steps are typically required.


Rules for the output:
• `answer` must be a boolean list with the same length and order as `candidate_functions`. `true` means the candidate is a plausible immediate follow-up; `false` means it is not.  
• `reason` must be a list of concise justifications (1–3 sentences, max ~50 words each), aligned index-wise with `answer`. For `true`, state the realistic customer/agent scenario that makes the follow-up plausible and list any **user-provided inputs** that the agent would rely on or request at that moment (e.g., reservation id, order number, patient id). For `false`, state briefly why the follow-up is implausible (e.g., mismatched intent, high cost without trigger, only valid in edge cases). If you rely on an assumption, state it briefly.  
• `is_root` is a single boolean indicating whether the target can reasonably be the initial agent action for a customer contact.  
• `is_root_reason` is a concise (1–3 sentences) justification: if `true`, explain why the function is callable as a first action and what inputs are typically available; if `false`, explain which prerequisite steps or inputs are normally required.

Style & constraints
• Be conservative — prefer **not** connecting unless plausibly useful.  
• No self-edges: if a candidate equals the target, set that `answer` entry to `false` and the corresponding `reason` to `"self — ignored"`.  
• Keep reasons direct, plain-language, and short.  
• Do **not** output anything other than the single JSON object (no commentary, no extra formatting).

Failure handling
If you cannot reliably judge a candidate, answer `false` and provide a brief reason explaining insufficient grounds (e.g., "insufficient domain info").

Follow these instructions exactly.
"""
# Root eligibility (how to judge `is_root`)
# Decide whether the **target_function** itself can be a realistic **root (entry-point)** for a customer support interaction.

# A function is a root **only if all** of the following are true:
# • A customer could reasonably initiate contact whose **first meaningful agent action** would be to call this function.
# • The function does not require implicit, multi-step prerequisite workflows outside a normal single support turn (e.g., full search+selection+pricing flows or back-office approvals).
# • **All of the inputs for the function is human-facing** — that is, they are typically provided directly by customers (order number, account id, email, phone, product name, SKU when commonly known) or can be obtained by the agent via a single clarifying question in the same turn.

# Root eligibility (how to judge `is_root`)
# Decide whether the **target_function** itself can be a realistic **root (entry-point)** for a customer support interaction. A function is a root **only if**:
# • a customer could reasonably initiate contact with a problem whose **first meaningful agent action** would be to call this function, and  
# • the function can be executed without requiring implicit prior steps that are not part of the available toolset (search/lookup/selection/prerequisite actions), and  
# • the necessary inputs for the function are naturally available at the start of an interaction (either provided directly by the customer or reasonably obtainable by the agent without calling other domain tools first).

# If the function typically requires prior discovery/selection or structured data produced by other tools, mark it **not** a root and explain which prerequisite steps or inputs are required.
# SYSTEM_PROMPT = """
# You are an expert software engineer and product-minded conversation designer. Your job is to analyze a target function and a list of candidate functions (all from a customer-service automation system) and decide which candidate functions should be considered logical neighbours of the target function.

# Crucial framing

# Imagine a real customer calling support with a problem that would cause the agent to use the target_function as the primary action for that turn. Given that context (the customer’s intent and the agent’s practical workflow), decide which candidate functions the agent would plausibly call next, assuming the available tools are connected and usable.

# Use business sense and realistic agent workflows.
# Do not rely on mechanical I/O compatibility; ignore any requirement that the target’s outputs must map to candidate inputs.

# ⸻

# Inputs available to you
# 	•	target_function: signature + description + response schema.
# 	•	candidate_functions: ordered list of functions, each with signature + description + response schema.
# 	•	domain_wiki (optional): short KB describing domain rules and common flows.

# ⸻

# Decision rules (apply in order)
# 	1.	Customer-intent & agent-flow rule (primary):
# Decide whether there is a realistic, commonly encountered customer-support scenario where the agent would plausibly call the candidate immediately after the target. Think about:
# 	•	the customer’s original problem,
# 	•	what the agent needs to accomplish next,
# 	•	and which follow-ups are routine (confirm, change, cancel, refund, compensate, rebook, correct data).
# 	2.	Temporal & cost sensitivity:
# Actions that are high-friction, costly, or terminal in customer support (e.g., cancellations, large refunds, full rebookings) require strong, common-sense justification to be neighbours of a prior step. Prefer conservative linking for such actions.
# 	3.	Edge-case exclusion:
# Do not link functions when the only plausible rationale depends on rare, contrived, or internal-admin scenarios (debugging, system recovery, race conditions). Prefer not connecting unless the follow-up is a normal, customer-facing step.
# 	4.	Independent evaluation:
# You will be invoked multiple times with different target functions from the same pool. Bidirectional links may emerge naturally across runs. Judge each candidate only in the context of the current target and a single realistic customer interaction.
# 	5.	Domain guidance:
# Use domain_wiki to resolve ambiguous business rules. If the wiki contradicts your intuition, follow the wiki.

# ⸻
# Root eligibility

# In addition to neighbour decisions, determine whether the target_function itself can act as a root (entry-point) in a customer-support interaction.

# A target function is a root only if all of the following are true:
# 	•	A customer could reasonably contact support with a problem or request whose first meaningful agent action would be to call this function.
# 	•	The function can be executed without requiring implicit prior steps that are not part of the current tool set (e.g., search, lookup, discovery, or prerequisite actions).
# 	•	The required inputs for the function are naturally available at the start of a support interaction, either because:
# 	•	the customer typically provides them directly (e.g., reservation ID, user ID), or
# 	•	the agent can reasonably obtain them without calling other domain-specific tools first.

# A function is not a root if:
# 	•	it assumes the results of prior actions (e.g., search, selection, pricing, eligibility checks),
# 	•	it requires structured data that is typically produced by other tools (even if technically the fields are simple),
# 	•	or it is normally invoked only as part of a multi-step workflow after context has already been established.
    
# """


# SYSTEM_PROMPT = """
# You are an expert software engineer who can analyze API functions and determine relationships between them. Your task is to identify which candidate functions are related to a given target function based on their input-output relationships.
# You will be provided with a target function and a list of candidate functions. Your job is to determine which candidate functions can be considered 'neighbours' of the target function meaning the candidate function can be called in a scenario based on the following criteria:
# 1) The output of the target function is used as input to the candidate function.
# 2) The output of the target function is part of the input to the candidate function.
# 3) The output of the target function directly influences the execution of the candidate function, for example consides a function to buy a product 

# The functions given are part of a customer service automation system which is used to solve or help customers in various tasks. Analyze the function signatures with parameters and response with descriptions carefully to determine the relationships. You will also be provided a brief knowkedge base (wiki) for the domain the functions belong to, which may help you understand the context better.

# Your output will be used to build a graph of function relationships, which will be used to generate random customer service scenarios. You need to give me: 
# 1) list of boolean values indicating whether each candidate function is a neighbour of the target function based on the criteria mentioned above.
# 2) list of detailed reasoning for each candidate function on why it is or isn't a neighbour of the target function, what scenario you thought of while analyzing the functions.

# REMEMBER that:
# - The length of both lists must be equal to the number of candidate functions given.
# - The order of boolean values and reasoning must correspond to the order of candidate functions provided.
# - There can't be a self edge: the target function must not be considered its own neighbour.
# """

HUMAN_PROMPT = """
{message}

Domain Knowledge Base (wiki):
{wiki}

Target Function:
{target_function}

Candidate Functions:
{candidate_functions}

Now, identify which candidate functions are neighbours of the Target Function based on the criteria already defined and return the response in the exact structured format:
- answer: list[bool]
- reason: list[str]
- is_root: bool
- is_root_reason: str
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
        if model_name not in {"gpt-4o", "gpt-5", "gpt-5.1", "gpt-5.2"}:
            raise ValueError("For provider 'openai', model must be one of: gpt-4o, gpt-5, gpt-5.1")

        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_retries=2,
            rate_limiter=rate_limiter,
        )

    elif provider == "gemini":
        if model_name != "gemini-2.0-flash" and model_name != "gemini-2.5-flash":
            raise ValueError("For provider 'gemini', model must be 'gemini-2.0-flash' or 'gemini-2.5-flash'")

        pass
        # return ChatGoogleGenerativeAI(
        #     model=model_name,
        #     temperature=temperature,
        #     max_tokens=None,
        #     timeout=None,
        #     max_retries=2,
        #     rate_limiter=rate_limiter,
        # )

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
def get_taubench_tools(skip=["think", "calculate", "transfert_to_agent"]):
    domain_names = ["airline", "retail", "telecom", "telehealth"]
    tools_by_domain = defaultdict(list)

    for d_title, d_tools in zip(
        # domain_names, [airline_tools, retail_tools]
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
def build_adjacency_matrix(tools, wiki, neighbour_chain):
    """
    tools: list[dict] from get_taubench_tools()[domain]
    neighbour_chain: LangChain runnable returning IsNeighbourResponse
    """
    results = {
        "tools": tools,
        "adjacency_matrix": [],  # list[list[bool]]
        "reason_matrix": [],     # list[list[str]]
        "is_root": [],            # list[bool]
        "is_root_reason": [],     # list[str]
    }
    expected_len = len(tools)
    for tool in tqdm(tools, desc="Finding neighbours"):
        result: IsNeighbourResponse = neighbour_chain.invoke(
            {
                "message": f"I have {expected_len} candidate functions, so I will expect {expected_len} boolean values and {expected_len} reasoning strings in the response.",
                "wiki": wiki,
                "target_function": tool,
                "candidate_functions": tools,
            }
        )
        if len(result.answer) != expected_len or len(result.reason) != expected_len:
            print("Retrying due to length mismatch...")
            result = neighbour_chain.invoke(
                {
                    "message": f"You gave me {len(result.answer)} boolean values and {len(result.reason)} reasoning strings, I was expecting {expected_len} of each since I have {expected_len} candidate functions. Please try again and ensure the lengths match exactly.",
                    "wiki": wiki,
                    "target_function": tool,
                    "candidate_functions": tools,
                }
            )
        results["adjacency_matrix"].append(result.answer)
        results["reason_matrix"].append(result.reason)
        results["is_root"].append(result.is_root)
        results["is_root_reason"].append(result.is_root_reason)

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
    base_output_dir = os.path.join("output", "graphs", f"{provider}_{model_name}")
    os.makedirs(base_output_dir, exist_ok=True)

    for domain, tools in tau_tools.items():
        if domain not in domains:
            continue

        print(f"Building adjacency matrix for domain: {domain} with {len(tools)} tools")
        if domain == "airline":
            wiki = AIRLINE_WIKI
        elif domain == "retail":
            wiki = RETAIL_WIKI
        elif domain == "telecom":
            wiki = TELECOM_WIKI
        elif domain == "telehealth":
            wiki = TELEHEALTH_WIKI
        else:
            wiki = "No wiki available."
        results = build_adjacency_matrix(tools, wiki, neighbour_chain)

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