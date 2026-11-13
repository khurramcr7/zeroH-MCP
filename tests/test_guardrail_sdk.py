# -*- coding: utf-8 -*-
"""
Unit tests for zeroH Drop-In LLM Guardrail & Decorator SDK (zeroh_mcp.guardrail)
and Official MCP Ecosystem Manifests.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zeroh_mcp import (
    ZeroHGuardrail,
    ZeroHHallucinationError,
    __version__,
    zeroh_guardrail,
)


def test_version_alignment() -> None:
    assert __version__ == "1.2.0"
    repo_root = Path(__file__).resolve().parent.parent
    server_manifest = json.loads((repo_root / "server.json").read_text(encoding="utf-8"))
    assert server_manifest["version"] == "1.2.0"
    assert server_manifest["packages"][0]["version"] == "1.2.0"


def test_guardrail_inspect_verified_claims() -> None:
    guard = ZeroHGuardrail()
    report = guard.inspect_text("Budget verification: 125 * 8 = 1000. Margin check: 127 - 11 = 116.")
    assert report["passed"] is True
    assert report["overall_status"] == "VERIFIED_COMPUTED_PASS"
    assert report["rejected_count"] == 0
    assert report["total_claims_checked"] == 2
    assert report["session_merkle_head"]
    assert "upgrade_options" in report


def test_guardrail_intercepts_arithmetic_hallucination_strict() -> None:
    @zeroh_guardrail(strict=True)
    def hallucinating_agent() -> str:
        return "Invoice audit complete: 12 * 12 = 145."

    with pytest.raises(ZeroHHallucinationError) as exc_info:
        hallucinating_agent()

    err_report = exc_info.value.report
    assert err_report["passed"] is False
    assert err_report["overall_status"] == "REJECTED_HALLUCINATION"
    assert err_report["rejected_count"] == 1


def test_guardrail_dict_enrichment_non_strict() -> None:
    @zeroh_guardrail(strict=False)
    def agent_json_response() -> dict:
        return {"content": "Exact ratio check: 4095 - 21 = 4074."}

    out = agent_json_response()
    assert "_zeroh_audit" in out
    assert out["_zeroh_audit"]["passed"] is True
