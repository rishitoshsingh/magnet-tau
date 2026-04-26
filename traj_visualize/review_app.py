import json
import os
import re

from flask import Flask, render_template, request

app = Flask(__name__)


USER_ID_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+)+\b")
DOB_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
RESERVATION_RE = re.compile(r"\b[A-Z0-9]{6}\b")
FLIGHT_RE = re.compile(r"\b[A-Z]{3}\d{3}\b")
CARD_ENDING_RE = re.compile(r"(?:card\s+ending\s+in|ending\s+in)\s+(\d{4,8})", re.IGNORECASE)
PAYMENT_ID_RE = re.compile(r"\b(?:credit_card|gift_card|certificate)_\d+\b")
AIRPORT_PAIR_RE = re.compile(r"\bfrom\s+([A-Z]{3})\s+to\s+([A-Z]{3})\b")
PASSENGER_RE = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+\(DOB\s+(\d{4}-\d{2}-\d{2})\)",
    re.IGNORECASE,
)


def _normalize_tasks(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict) and isinstance(data.get("sampled_tasks"), list):
        normalized = []
        for sampled_task in data["sampled_tasks"]:
            for trial in sampled_task.get("trials", []):
                merged = dict(trial)
                merged.setdefault("task_id", sampled_task.get("task_id"))
                merged["source_file"] = sampled_task.get("source_file")
                merged["num_trials"] = sampled_task.get("num_trials")
                normalized.append(merged)
        return normalized

    raise ValueError(
        "Unsupported JSON format. Expected a list of tasks or an object with 'sampled_tasks'."
    )


def _extract_claims(text):
    reservation_ids = []
    for candidate in RESERVATION_RE.findall(text):
        if FLIGHT_RE.fullmatch(candidate):
            continue
        reservation_ids.append(candidate)

    claims = {
        "user_ids": sorted(set(USER_ID_RE.findall(text))),
        "dobs": sorted(set(DOB_RE.findall(text))),
        "reservation_ids": sorted(set(reservation_ids)),
        "flight_numbers": sorted(set(FLIGHT_RE.findall(text))),
        "card_endings": sorted(set(CARD_ENDING_RE.findall(text))),
        "payment_ids": sorted(set(PAYMENT_ID_RE.findall(text))),
        "airport_pairs": sorted(set(f"{origin}->{destination}" for origin, destination in AIRPORT_PAIR_RE.findall(text))),
        "named_passengers": sorted(
            set(f"{name.title()} ({dob})" for name, dob in PASSENGER_RE.findall(text))
        ),
    }
    return claims


def _claim_diffs(reference_claims, user_claims):
    mismatches = {}
    for key, user_values in user_claims.items():
        if not user_values:
            continue
        reference_values = set(reference_claims.get(key, []))
        if not reference_values:
            continue
        unsupported = sorted(value for value in user_values if value not in reference_values)
        if unsupported:
            mismatches[key] = unsupported
    return mismatches


def _messages_by_role(task, role):
    items = []
    for index, msg in enumerate(task.get("traj", []), start=1):
        if msg.get("role") == role:
            items.append(
                {
                    "turn_index": index,
                    "content": msg.get("content", ""),
                }
            )
    return items


def _prepare_task(task):
    task_details = task.get("info", {}).get("task") or {}
    instruction = task_details.get("instruction", "")
    user_messages = _messages_by_role(task, "user")
    user_text = "\n\n".join(msg["content"] for msg in user_messages if msg.get("content"))

    reference_claims = _extract_claims(instruction)
    user_claims = _extract_claims(user_text)
    possible_fabrications = _claim_diffs(reference_claims, user_claims)

    prepared = dict(task)
    prepared["task_details"] = task_details
    prepared["reward_details"] = task.get("info", {}).get("reward_info")
    prepared["instruction"] = instruction
    prepared["user_messages"] = user_messages
    prepared["reference_claims"] = reference_claims
    prepared["user_claims"] = user_claims
    prepared["possible_fabrications"] = possible_fabrications
    prepared["has_possible_fabrication"] = bool(possible_fabrications)
    return prepared


@app.route("/")
def index():
    return render_template("review_index.html")


@app.route("/review")
def review():
    file_path = request.args.get("file")
    if not file_path or not os.path.exists(file_path):
        return f"File not found: {file_path}", 404

    with open(file_path, "r") as f:
        data = json.load(f)

    try:
        tasks = _normalize_tasks(data)
    except ValueError as exc:
        return str(exc), 400

    prepared_tasks = [_prepare_task(task) for task in tasks]
    return render_template("review_tasks.html", data=prepared_tasks, file_path=file_path)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
