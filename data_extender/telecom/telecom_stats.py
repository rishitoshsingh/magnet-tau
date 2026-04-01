from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data_extender.telecom_stats import print_stats


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="data_extender.telecom.telecom_stats",
        description="Validate and summarize a generated telecom dataset.",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=str(Path("data_extender") / "telecom" / "env" / "telecom"),
        help="Dataset directory containing customers.json/billing.json/etc",
    )
    parser.add_argument("--max-errors", type=int, default=25, help="Max validation errors to print")
    args = parser.parse_args()

    dataset_dir = Path(args.path).resolve()
    return print_stats(dataset_dir, max_errors=int(args.max_errors))


if __name__ == "__main__":
    raise SystemExit(main())
