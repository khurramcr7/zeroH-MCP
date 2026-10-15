# -*- coding: utf-8 -*-
"""
zeroH MCP Public Test Suite
===========================
Verifies:
  1. JSON-RPC 2.0 MCP Server lifecycle (`initialize`, `tools/list`, `tools/call`, `ping`)
  2. Exact AST rational arithmetic evaluation & hallucination interception
  3. Algebraic equation solver & root substitution verification
  4. SHA-256 Step-Ledger hash-chain sealing (`verify_step`, `session_report`)
  5. BFT Epistemic Quorum evaluation (`QATI`, `ZANNI_GHALIB`, `SHAKK`, `WAHM`)
  6. Zero proprietary formula / constant exposure across the entire repository
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from zeroh_mcp import ZeroHClient, handle_mcp_request
from scripts.security_audit_no_leaks import scan_repository


def test_mcp_initialize_and_tools_list() -> None:
    init_resp = handle_mcp_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert init_resp is not None
    assert init_resp["result"]["serverInfo"]["name"] == "zeroh-mcp"

    list_resp = handle_mcp_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert list_resp is not None
    tool_names = {t["name"] for t in list_resp["result"]["tools"]}
    expected = {
        "validate_claim",
        "verify_step",
        "session_report",
        "compute",
        "solve_equation",
        "intercept_token",
        "zk_verify_receipt",
        "epistemic_consensus",
        "enclave_status",
    }
    assert expected.issubset(tool_names)


def test_validate_claim_arithmetic_pass_and_fail() -> None:
    client = ZeroHClient()

    valid_res = client.validate("In exact arithmetic, 12 * 12 = 144.")
    assert valid_res["is_valid"] is True
    assert valid_res["deterministic_status"] == "VERIFIED_COMPUTED_PASS"
    assert valid_res["coherence_index"] == 1.0

    hallucinated_res = client.validate("The model claimed that 12 * 12 = 145.")
    assert hallucinated_res["is_valid"] is False
    assert hallucinated_res["deterministic_status"] == "REJECTED_HALLUCINATION"
    assert hallucinated_res["coherence_index"] == 0.0


def test_compute_and_solve_equation() -> None:
    client = ZeroHClient()

    comp = client.compute("(1/3) + (1/6)")
    assert comp["exact_fraction"] == "1/2"
    assert comp["decimal_value"] == 0.5
    assert comp["deterministic_status"] == "VERIFIED_COMPUTED_PASS"

    sol = client.solve_equation("x**2 - 5*x + 6 = 0", unknown="x")
    assert sol["deterministic_status"] == "VERIFIED_COMPUTED_PASS"
    roots = {s["solution"] for s in sol["solutions"]}
    assert {"2", "3"} == roots

    bad_claim = client.solve_equation("x**2 - 5*x + 6 = 0", unknown="x", claimed=[4])
    assert bad_claim["deterministic_status"] == "REJECTED_HALLUCINATION"


def test_step_ledger_and_merkle_seal() -> None:
    client = ZeroHClient()
    session = "test_chain_01"

    s1 = client.verify_step(session, {"kind": "compute", "expr": "7 * 8", "value": "56"})
    assert s1["verdict"] == "PROVEN"

    s2 = client.verify_step(
        session,
        {"kind": "solve", "equation": "2*x - 10 = 0", "claimed": {"x": 5}},
    )
    assert s2["verdict"] == "PROVEN"

    rep = client.session_report(session)
    assert rep["seal"] == "FULLY_PROVEN"
    assert rep["deterministic_status"] == "VERIFIED_COMPUTED_PASS"
    assert len(rep["merkle_head_hash"]) == 64


def test_bft_epistemic_consensus() -> None:
    client = ZeroHClient()

    qati = client.epistemic_consensus("agent_1", "10 + 10 = 20", confidence=0.99, contradiction=0.0)
    assert qati["tier"] == "QATI"
    assert qati["byzantine_veto"] is False

    wahm = client.epistemic_consensus("agent_2", "10 + 10 = 99", confidence=0.95, contradiction=0.0)
    assert wahm["tier"] == "WAHM"
    assert wahm["byzantine_veto"] is True
    assert wahm["deterministic_status"] == "BOUNDARY_BREACH"


def test_zero_proprietary_formula_leakage() -> None:
    violations = scan_repository()
    assert violations == [], f"Proprietary IP leakage detected: {violations}"
    status = ZeroHClient().status()
    assert status["proprietary_formulas_exposed"] is False
    assert status["ip_protection_status"] == "SOVEREIGN_VAULTED_SAFE"
