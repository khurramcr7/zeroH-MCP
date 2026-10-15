# -*- coding: utf-8 -*-
"""
zeroH CLI Entry Point (zeroh_mcp.cli)
=====================================
Provides instant command-line verification for terminal workflows and CI pipelines.
"""

from __future__ import annotations

import argparse
import json
import sys

from .client import ZeroHClient

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="zeroH MCP — Deterministic AI Hallucination Guardrail & Verification CLI"
    )
    parser.add_argument(
        "claim",
        nargs="*",
        help="Text claim, mathematical statement, or payload to validate",
    )
    parser.add_argument("--api-url", default=None, help="Optional Remote Sovereign Enclave URL")
    parser.add_argument("--api-key", default=None, help="Optional Remote Sovereign Enclave API Key")
    parser.add_argument("--status", action="store_true", help="Show enclave & IP protection status")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")
    args = parser.parse_args()

    client = ZeroHClient(api_url=args.api_url, api_key=args.api_key)

    if args.status or not args.claim:
        print(json.dumps(client.status(), indent=2))
        return

    full_claim = " ".join(args.claim)
    res = client.validate(full_claim)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("=" * 76)
        print("                   zeroH MCP VERIFICATION RECEIPT")
        print("=" * 76)
        print(f"Claim            : {full_claim}")
        print(f"Status           : {res.get('deterministic_status')}")
        print(f"Coherence Index  : {res.get('coherence_index')} ({res.get('confidence_score')})")
        print(f"Execution Tier   : {res.get('execution_tier')}")
        print(f"Valid            : {res.get('is_valid')}")
        print(f"Receipt ID       : {res.get('receipt_id', 'N/A')}")
        print("=" * 76)


if __name__ == "__main__":
    main()
