"""Command-line interface for the computational supplement."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .families import (
    aeaqec_family,
    eaqec_family,
    paper_3_20_family,
    write_aeaqec_csv,
    write_eaqec_csv,
    write_paper_aeaqec_csv,
)
from .quantum import direct_constacyclic_pair
from .reproduce import reproduce
from .verify import run_verification


def _destination(value: str):
    return sys.stdout if value == "-" else Path(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m eaqec",
        description="EAQEC/AEAQEC parameter generation and explicit verification",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    family = subparsers.add_parser("family", help="generate a parameter family as CSV")
    family.add_argument("kind", choices=("eaqec", "aeaqec", "paper"))
    family.add_argument("--p", type=int, required=True, help="odd prime p")
    family.add_argument("--m", type=int, default=1, help="field extension degree; q=p^m")
    family.add_argument(
        "--orientation",
        choices=("natural", "swapped", "both"),
        default="natural",
        help="constituent orientation for validated AEAQEC output",
    )
    family.add_argument("--output", default="-", help="CSV path, or - for stdout")

    direct = subparsers.add_parser("direct", help="explicit generator-matrix computation")
    direct.add_argument("--p", type=int, required=True)
    direct.add_argument("--s", type=int, required=True)
    direct.add_argument("--j", type=int, required=True)
    direct.add_argument("--t", type=int, required=True)
    direct.add_argument("--root1", type=int, default=1)
    direct.add_argument("--root2", type=int, default=2)
    direct.add_argument("--max-codewords", type=int, default=2_000_000)
    direct.add_argument("--output", default="-", help="JSON path, or - for stdout")

    verify = subparsers.add_parser("verify", help="run independent exact checks")
    verify.add_argument("--deep", action="store_true", help="check every nontrivial F_7 pair")
    verify.add_argument("--output", default="-", help="JSON path, or - for stdout")

    reproduce_parser = subparsers.add_parser("reproduce", help="generate all tables and reports")
    reproduce_parser.add_argument("--output", default="results")
    reproduce_parser.add_argument("--quick", action="store_true", help="selected rather than all F_7 pairs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "family":
        destination = _destination(args.output)
        if args.kind == "eaqec":
            write_eaqec_csv(eaqec_family(args.p, args.m), destination)
        elif args.kind == "aeaqec":
            write_aeaqec_csv(
                aeaqec_family(args.p, args.m, orientation=args.orientation), destination
            )
        else:
            write_paper_aeaqec_csv(paper_3_20_family(args.p, args.m), destination)
        return 0

    if args.command == "direct":
        result = direct_constacyclic_pair(
            args.p,
            args.s,
            args.j,
            args.t,
            root1=args.root1,
            root2=args.root2,
            max_codewords=args.max_codewords,
        )
        text = json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n"
        if args.output == "-":
            sys.stdout.write(text)
        else:
            Path(args.output).write_text(text, encoding="utf-8")
        return 0

    if args.command == "verify":
        result = run_verification(deep=args.deep)
        text = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output == "-":
            sys.stdout.write(text)
        else:
            Path(args.output).write_text(text, encoding="utf-8")
        return 0 if result["pass"] else 1

    if args.command == "reproduce":
        manifest = reproduce(args.output, deep=not args.quick)
        print(json.dumps(manifest["verification"], indent=2, sort_keys=True))
        print(f"Tables and reports written to {Path(args.output).resolve()}")
        return 0

    raise AssertionError(f"unhandled command {args.command}")
