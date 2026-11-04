# -*- coding: utf-8 -*-
"""
zeroH MCP — Rigorous Adversarial, Stress, Security & Protocol Verification Suite
================================================================================
Tests:
  1. IEEE-754 Floating-Point Drift Immunity & Exact Rational Arithmetic Stress
  2. Adversarial AST Code-Injection & Exponent-Bomb DoS Resistance
  3. Algebraic Equation Solver & False-Root Substitution Interception
  4. SHA-256 Merkle Step-Ledger Tamper Evidence & Step Superseding (`replaces`)
  5. Byzantine Fault Tolerant (BFT) Rogue-Agent Overconfident Hallucination Veto
  6. Enclave Response Sanitization (Redaction of Internal Proprietary Fields)
  7. Live Subprocess Stdio JSON-RPC 2.0 Protocol & Error-Code Conformance
  8. CLI Subprocess End-to-End Execution
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from zeroh_mcp import ZeroHClient, handle_mcp_request
from zeroh_mcp.enclave_bridge import SovereignEnclaveBridge
from zeroh_mcp.public_verifier import compute_exact, solve_algebraic_equation


# ---------------------------------------------------------------------------
# 1. IEEE-754 Drift Immunity & Exact Rational Arithmetic Stress
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "claim,expected_valid,expected_status",
    [
        # Classic IEEE-754 float trap: 0.1 + 0.2 == 0.30000000000000004 in float, but exact in Fraction!
        ("In exact decimal arithmetic, 0.1 + 0.2 = 0.3", True, "VERIFIED_COMPUTED_PASS"),
        ("Repeating rational sum: (1/3) + (1/3) + (1/3) = 1", True, "VERIFIED_COMPUTED_PASS"),
        ("Nested rational identity: ((144 / 12) + (81 / 9)) * 2 = 42", True, "VERIFIED_COMPUTED_PASS"),
        ("Exact power identity: 2^10 + 3^4 = 1105", True, "VERIFIED_COMPUTED_PASS"),
        ("Inequality holds: 7 * 8 != 55", True, "VERIFIED_COMPUTED_PASS"),
        # Subtle hallucinations
        ("Off-by-one hallucination: 17 * 19 = 322", False, "REJECTED_HALLUCINATION"),
        ("Float drift hallucination: 0.1 + 0.2 = 0.30000001", False, "REJECTED_HALLUCINATION"),
        ("False inequality: 12 * 12 != 144", False, "REJECTED_HALLUCINATION"),
        ("Multiple equations where second is false: 2 + 2 = 4 and 5 * 5 = 26", False, "REJECTED_HALLUCINATION"),
        # Speculative divination / Pillar IV boundary breach
        ("Using astrology predictions to forecast tomorrow's fate", False, "BOUNDARY_BREACH"),
        ("Palmistry reading guarantees financial fortune", False, "BOUNDARY_BREACH"),
    ],
)
def test_exact_arithmetic_and_boundary_stress(
    claim: str, expected_valid: bool, expected_status: str
) -> None:
    client = ZeroHClient()
    res = client.validate(claim)
    assert res["is_valid"] is expected_valid, f"Failed on claim: {claim} -> {res}"
    assert res["deterministic_status"] == expected_status


# ---------------------------------------------------------------------------
# 2. Adversarial AST Code-Injection & DoS Exponent-Bomb Hardening
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "malicious_expr",
    [
        "__import__('os').system('echo pwned')",
        "eval('1+1')",
        "(1).__class__.__base__.__subclasses__()",
        "[x for x in range(100)]",
        "lambda x: x + 1",
        "9 ** 999999",
        "1 / 0",
        "",
    ],
)
def test_ast_injection_and_dos_resistance(malicious_expr: str) -> None:
    res = compute_exact(malicious_expr)
    assert res["status"] in ("COMPUTATION_ERROR", "INVALID_EXPRESSION")
    assert res["deterministic_status"] in ("REJECTED_HALLUCINATION", "NEEDS_REVIEW")


# ---------------------------------------------------------------------------
# 3. Algebraic Equation Solver & Substitution Verification
# ---------------------------------------------------------------------------
def test_algebraic_solver_linear_quadratic_and_false_claims() -> None:
    # Linear equation
    r_lin = solve_algebraic_equation("3*x + 12 = 0", unknown="x")
    assert r_lin["deterministic_status"] == "VERIFIED_COMPUTED_PASS"
    assert any(s["solution"] == "-4" and s["checked_by_substitution"] for s in r_lin["solutions"])

    # Quadratic equation with two integer roots
    r_quad = solve_algebraic_equation("x^2 - 7*x + 12 = 0", unknown="x")
    assert r_quad["deterministic_status"] == "VERIFIED_COMPUTED_PASS"
    roots = {s["solution"] for s in r_quad["solutions"]}
    assert roots == {"3", "4"}

    # Claimed roots: valid vs invalid
    r_valid_claim = solve_algebraic_equation("x^2 - 7*x + 12 = 0", unknown="x", claimed_solutions=[3, 4])
    assert r_valid_claim["deterministic_status"] == "VERIFIED_COMPUTED_PASS"

    r_bad_claim = solve_algebraic_equation("x^2 - 7*x + 12 = 0", unknown="x", claimed_solutions=[3, 5])
    assert r_bad_claim["deterministic_status"] == "REJECTED_HALLUCINATION"


# ---------------------------------------------------------------------------
# 4. SHA-256 Merkle Step-Ledger & Step Superseding (`replaces`)
# ---------------------------------------------------------------------------
def test_step_ledger_failure_recovery_and_merkle_determinism() -> None:
    client = ZeroHClient()
    session = "rigorous_session_merkle"

    # Step 1: Valid compute
    s1 = client.verify_step(session, {"kind": "compute", "expr": "15 * 15", "value": "225"})
    assert s1["verdict"] == "PROVEN"

    # Step 2: Hallucinated compute -> FAIL
    s2 = client.verify_step(session, {"kind": "compute", "expr": "15 * 16", "value": "250"})
    assert s2["verdict"] == "FAIL"

    # Report while Step 2 is active must be BLOCKED_FAILED_STEPS
    rep_blocked = client.session_report(session)
    assert rep_blocked["seal"] == "BLOCKED_FAILED_STEPS"
    assert rep_blocked["deterministic_status"] == "REJECTED_HALLUCINATION"
    assert rep_blocked["coherence_index"] == 0.0

    # Step 3: Supersedes Step 2 (`replaces: 2`) with corrected calculation
    s3 = client.verify_step(
        session,
        {"kind": "compute", "expr": "15 * 16", "value": "240", "replaces": 2},
    )
    assert s3["verdict"] == "PROVEN"

    # Report now must be FULLY_PROVEN
    rep_proven = client.session_report(session)
    assert rep_proven["seal"] == "FULLY_PROVEN"
    assert rep_proven["deterministic_status"] == "VERIFIED_COMPUTED_PASS"
    assert rep_proven["coherence_index"] == 1.0
    assert rep_proven["total_steps"] == 3
    assert rep_proven["active_steps"] == 2
    assert rep_proven["merkle_head_hash"] != rep_blocked["merkle_head_hash"]


# ---------------------------------------------------------------------------
# 5. BFT Epistemic Quorum: Overconfident Rogue Agent Veto
# ---------------------------------------------------------------------------
def test_bft_rogue_agent_overconfident_hallucination_veto() -> None:
    client = ZeroHClient()

    # Rogue agent claims 100% confidence & 0% contradiction, but embeds a false equation
    rogue = client.epistemic_consensus(
        agent_id="rogue_llm_node",
        proposal="I am 100% certain that 25 * 4 = 105.",
        confidence=1.0,
        contradiction=0.0,
    )
    assert rogue["tier"] == "WAHM"
    assert rogue["byzantine_veto"] is True
    assert rogue["can_persist_to_ledger"] is False
    assert rogue["action_taken"] == "VETO_HALT_REJECTED"
    assert rogue["deterministic_status"] == "BOUNDARY_BREACH"

    # Zanni Ghalib tier (0.70 <= p < 0.98)
    zanni = client.epistemic_consensus(
        agent_id="research_node",
        proposal="25 * 4 = 100",
        confidence=0.85,
        contradiction=0.05,
    )
    assert zanni["tier"] == "ZANNI_GHALIB"
    assert zanni["can_persist_to_ledger"] is True
    assert zanni["byzantine_veto"] is False

    # Shakk tier (0.40 <= p < 0.70)
    shakk = client.epistemic_consensus(
        agent_id="uncertain_node",
        proposal="25 * 4 = 100",
        confidence=0.60,
        contradiction=0.20,
    )
    assert shakk["tier"] == "SHAKK"
    assert shakk["can_persist_to_ledger"] is False
    assert shakk["action_taken"] == "STAGE_FOR_CORROBORATION"


# ---------------------------------------------------------------------------
# 6. Sovereign Enclave Response Sanitization (Redaction of Proprietary Fields)
# ---------------------------------------------------------------------------
def test_enclave_response_redacts_internal_constants() -> None:
    raw_mock_enclave_payload = {
        "deterministic_status": "VERIFIED_COMPUTED_PASS",
        "coherence_index": 0.9912,
        "confidence_score": "99.12%",
        "is_valid": True,
        "invariant_baseline_mu": 999.99,
        "boundary_ceiling_b_max": 111.11,
        "S_AQL": 888.88,
        "s_aql": 888.88,
        "mu_test": {"secret": "internal"},
        "mu_note": "internal note",
        "entropy_ceiling": 777.77,
    }
    sanitized = SovereignEnclaveBridge._sanitize_enclave_response(raw_mock_enclave_payload)
    for forbidden_key in (
        "invariant_baseline_mu",
        "boundary_ceiling_b_max",
        "S_AQL",
        "s_aql",
        "mu_test",
        "mu_note",
        "entropy_ceiling",
    ):
        assert forbidden_key not in sanitized
    assert sanitized["deterministic_status"] == "VERIFIED_COMPUTED_PASS"
    assert sanitized["coherence_index"] == 0.9912


# ---------------------------------------------------------------------------
# 7. Live Subprocess Stdio JSON-RPC 2.0 Protocol & Error Handling
# ---------------------------------------------------------------------------
def test_live_stdio_subprocess_jsonrpc_protocol() -> None:
    messages_in = [
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"}),
        json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/list"}),
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "validate_claim",
                    "arguments": {"claim": "19 * 19 = 361"},
                },
            }
        ),
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "nonexistent_tool", "arguments": {}},
            }
        ),
        json.dumps({"jsonrpc": "2.0", "id": 6, "method": "unknown/method"}),
        "{malformed_json_line",
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    proc = subprocess.run(
        [sys.executable, "-m", "zeroh_mcp.server"],
        input="\n".join(messages_in) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO_ROOT),
        env=env,
        timeout=20,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    lines = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    by_id = {m.get("id"): m for m in lines}

    assert by_id[1]["result"]["serverInfo"]["name"] == "zeroh-mcp"
    assert by_id[2]["result"] == {}
    assert len(by_id[3]["result"]["tools"]) == 15

    call_res = json.loads(by_id[4]["result"]["content"][0]["text"])
    assert call_res["deterministic_status"] == "VERIFIED_COMPUTED_PASS"
    assert call_res["coherence_index"] == 1.0

    # Unknown tool -> -32602
    assert by_id[5]["error"]["code"] == -32602
    # Unknown method -> -32601
    assert by_id[6]["error"]["code"] == -32601
    # Malformed JSON -> -32700
    assert by_id[None]["error"]["code"] == -32700


# ---------------------------------------------------------------------------
# 8. CLI End-to-End Subprocess Verification
# ---------------------------------------------------------------------------
def test_cli_end_to_end_json_and_status() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)

    proc_status = subprocess.run(
        [sys.executable, "-m", "zeroh_mcp.cli", "--status"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO_ROOT),
        env=env,
        timeout=15,
        check=True,
    )
    status_data = json.loads(proc_status.stdout)
    assert status_data["ip_protection_status"] == "SOVEREIGN_VAULTED_SAFE"
    assert status_data["proprietary_formulas_exposed"] is False

    proc_claim = subprocess.run(
        [sys.executable, "-m", "zeroh_mcp.cli", "--json", "21 * 21 = 441"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO_ROOT),
        env=env,
        timeout=15,
        check=True,
    )
    claim_data = json.loads(proc_claim.stdout)
    assert claim_data["deterministic_status"] == "VERIFIED_COMPUTED_PASS"
    assert claim_data["is_valid"] is True


# ---------------------------------------------------------------------------
# 9. Regression Suite: Unicode Operators, Commas, Conditional Algebra,
#    Unchecked Claims, Inconsistent Equations, and BFT Self-Certification
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "claim,expected_valid,expected_status,expected_coherence",
    [
        ("14,266 + 218 = 14,484", True, "VERIFIED_COMPUTED_PASS", 1.0),
        ("3 × 4 = 12", True, "VERIFIED_COMPUTED_PASS", 1.0),
        ("10 ÷ 2 = 5", True, "VERIFIED_COMPUTED_PASS", 1.0),
        ("If x + 2 = 5 then x = 3", True, "VERIFIED_COMPUTED_PASS", 1.0),
        ("If x + 2 = 5 then x = 9", False, "REJECTED_HALLUCINATION", 0.0),
        ("5 × 4 = 4", False, "REJECTED_HALLUCINATION", 0.0),
        ("10 ÷ 2 = 2", False, "REJECTED_HALLUCINATION", 0.0),
        ("The root of هبط is ح-ب-ط", False, "NEEDS_REVIEW", 0.0),
        ("The Qur’an has 6,237 verses", False, "NEEDS_REVIEW", 0.0),
    ],
)
def test_claude_audit_regression_claims(
    claim: str, expected_valid: bool, expected_status: str, expected_coherence: float
) -> None:
    client = ZeroHClient()
    res = client.validate(claim)
    assert res["is_valid"] is expected_valid, f"Claim failed: {claim} -> {res}"
    assert res["deterministic_status"] == expected_status
    assert res["coherence_index"] == expected_coherence


def test_inconsistent_equation_and_irrational_and_bft_unverified() -> None:
    # 1. x = x + 1 has no solution; must not come back SOLVED at 100%
    no_sol = solve_algebraic_equation("x = x + 1", unknown="x")
    assert no_sol["status"] == "NO_SOLUTION_FOUND"
    assert no_sol["solutions"] == []
    assert no_sol["coherence_index"] == 0.0
    assert no_sol["deterministic_status"] == "NEEDS_REVIEW"

    # 2. √2 must not be labelled REJECTED_HALLUCINATION
    sqrt2 = compute_exact("√2")
    assert sqrt2["deterministic_status"] != "REJECTED_HALLUCINATION"

    # 3. Unchecked claim cannot self-certify as QATI or persist to ledger
    client = ZeroHClient()
    unverified_bft = client.epistemic_consensus(
        agent_id="self_cert_agent",
        proposal="The Qur’an has 6,237 verses",
        confidence=1.0,
        contradiction=0.0,
    )
    assert unverified_bft["tier"] != "QATI"
    assert unverified_bft["can_persist_to_ledger"] is False
    assert unverified_bft["deterministic_status"] == "NEEDS_REVIEW"

    # 4. Configured enclave fallback warning when unreachable
    bridge = SovereignEnclaveBridge(api_url="http://127.0.0.1:59999", timeout=0.2)
    fb_res = bridge.validate_claim("3 × 4 = 12")
    assert fb_res.get("enclave_fallback") is True
    assert "unreachable" in fb_res.get("enclave_warning", "")


def test_onexi_public_paid_subscription_mcps_and_bio_payment_only_policy() -> None:
    # 1. Subscription Gate: status & public plans (Bio excluded from public MCP plans, kept in payment gateway)
    sub_status_resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/call",
            "params": {"name": "onexi_subscription_gate", "arguments": {"action": "subscription_status"}},
        }
    )
    sub_status = json.loads(sub_status_resp["result"]["content"][0]["text"])
    assert sub_status["bio_public_mcp_exposed"] is False
    assert sub_status["bio_mcp_policy"] == "PAYMENT_ONLY_NOT_PUBLIC_YET"
    assert sub_status["available_public_plans_count"] == 12

    plans_resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 102,
            "method": "tools/call",
            "params": {"name": "onexi_subscription_gate", "arguments": {"action": "list_public_subscription_plans"}},
        }
    )
    plans = json.loads(plans_resp["result"]["content"][0]["text"])
    assert "PULSE_PER_PROCEDURE_SIMULATION" not in plans["public_mcp_plans"]
    assert "GENESIS_STARTER_BIOPHARMA_MONTHLY" not in plans["public_mcp_plans"]
    assert "FAST_49_PASS" in plans["public_mcp_plans"]
    assert "QUANTUM_AUDIT_2500" in plans["public_mcp_plans"]

    # 2. Payment Gateway STILL keeps all 16 tiers (including Bio payment tiers) for settlement
    gw_resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 103,
            "method": "tools/call",
            "params": {"name": "onexi_payment_gateway", "arguments": {"action": "list_checkout_catalog"}},
        }
    )
    gw_cat = json.loads(gw_resp["result"]["content"][0]["text"])
    assert gw_cat["products_count"] == 16
    assert gw_cat["catalog"]["PULSE_PER_PROCEDURE_SIMULATION"]["mcp_visibility"] == "PAYMENT_ONLY_NOT_PUBLIC_YET"
    assert gw_cat["catalog"]["GENESIS_STARTER_BIOPHARMA_MONTHLY"]["mcp_visibility"] == "PAYMENT_ONLY_NOT_PUBLIC_YET"
    assert gw_cat["catalog"]["FAST_49_PASS"]["mcp_visibility"] == "PUBLIC_PAID_MCP"

    # 3. Quantum Compiler: benchmark telemetry (free) vs compile_circuit (paid subscription gate)
    q_bench_resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 104,
            "method": "tools/call",
            "params": {"name": "onexi_quantum_compiler", "arguments": {"action": "benchmark_telemetry"}},
        }
    )
    q_bench = json.loads(q_bench_resp["result"]["content"][0]["text"])
    assert q_bench["merkle_priority_seal"] == "e8c2800b1f74c93cbc2546293f76caa550867559e5f46992843da9fce6c66ea2"

    q_unsub_resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 105,
            "method": "tools/call",
            "params": {"name": "onexi_quantum_compiler", "arguments": {"action": "compile_circuit", "qasm": "qreg q[4];\nccx q[0],q[1],q[2];"}},
        }
    )
    q_unsub = json.loads(q_unsub_resp["result"]["content"][0]["text"])
    assert q_unsub["status"] == "SUBSCRIPTION_REQUIRED"
    assert "polar_stripe_card_checkout" in q_unsub["checkout_session"]["one_click_checkout_urls"]

    q_sub_resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 106,
            "method": "tools/call",
            "params": {
                "name": "onexi_quantum_compiler",
                "arguments": {
                    "action": "compile_circuit",
                    "qasm": "qreg q[4];\nccx q[0],q[1],q[2];",
                    "license_key": "ONEXI_QUANTUM_AUDIT_2500_LIVEKEY",
                },
            },
        }
    )
    q_sub = json.loads(q_sub_resp["result"]["content"][0]["text"])
    assert q_sub["status"] == "AUTHENTICATED_ENCLAVE_READY"
    assert q_sub["active_tier"] == "QUANTUM_AUDIT_2500"

    # 4. 8-Gate HPC Code Sandbox
    hpc_resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 107,
            "method": "tools/call",
            "params": {
                "name": "onexi_hpc_code_sandbox",
                "arguments": {"action": "audit_code_8gate", "code": "def add_exact(a: int, b: int) -> int:\n    return a + b\n"},
            },
        }
    )
    hpc = json.loads(hpc_resp["result"]["content"][0]["text"])
    assert hpc["gates_passed"] == 8
    assert hpc["deterministic_status"] == "VERIFIED_COMPUTED_PASS"

    # 5. KutubLink & Aalim Scholar MCPs
    kl_resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 108,
            "method": "tools/call",
            "params": {
                "name": "onexi_kutublink_turath",
                "arguments": {"action": "audit_tashkil_and_abjad", "text": "بِسْمِ ٱللَّهِ"},
            },
        }
    )
    kl = json.loads(kl_resp["result"]["content"][0]["text"])
    assert kl["is_vocalized"] is True
    assert kl["abjad_mashriqi_total"] > 0

    al_resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 109,
            "method": "tools/call",
            "params": {
                "name": "onexi_aalim_scholar",
                "arguments": {"action": "calculate_zakah_exact", "net_zakatable_wealth": "4000", "nisab_threshold": "595"},
            },
        }
    )
    al = json.loads(al_resp["result"]["content"][0]["text"])
    assert al["zakah_due_exact_fraction"] == "100"
    assert al["deterministic_status"] == "VERIFIED_COMPUTED_PASS"


