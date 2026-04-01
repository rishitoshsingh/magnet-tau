from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data_extender.extend_telecom import (
    _deep_update,
    _default_config,
    _fix_existing_telecom_data,
    _load_yaml_config,
    _repo_root,
    generate_telecom_dataset,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="data_extender.telecom.extend_telecom",
        description="Generate an extended telecom benchmark dataset.",
    )
    parser.add_argument("N", type=int, help="Number of customers to generate (e.g., 200-500)")
    parser.add_argument("--seed", type=int, default=1337, help="RNG seed for reproducible generation")
    parser.add_argument(
        "--config",
        type=str,
        default=str(Path("data_extender") / "telecom" / "telecom_config.yaml"),
        help="YAML config path for weights/ranges.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(Path("data_extender") / "telecom" / "env" / "telecom"),
        help="Output directory for the generated telecom dataset.",
    )
    args = parser.parse_args()

    if args.N <= 0:
        raise SystemExit("N must be > 0")

    repo_root = _repo_root(Path.cwd())
    _fix_existing_telecom_data(repo_root)

    cfg = _default_config()
    config_path = Path(args.config)
    resolved_config = config_path if config_path.is_absolute() else (repo_root / config_path)
    if resolved_config.exists():
        loaded = _load_yaml_config(resolved_config)
        _deep_update(cfg, loaded)

    out_dir = Path(args.out)
    resolved_out = out_dir if out_dir.is_absolute() else (repo_root / out_dir)
    generate_telecom_dataset(args.N, args.seed, resolved_out, repo_root, cfg)
    print(f"Wrote extended telecom dataset to: {resolved_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
