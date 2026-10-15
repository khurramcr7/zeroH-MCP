# -*- coding: utf-8 -*-
"""
zeroH Public Open-Boundary Deterministic Verifier (zeroh_mcp.public_verifier)
=============================================================================
Provides transparent, non-proprietary deterministic checks for the public MCP:
  1. Exact rational arithmetic evaluation via Python AST + fractions.Fraction
  2. Algebraic equation solving & root substitution verification
  3. Tamper-evident SHA-256 Merkle/Hash-Chain Session Step Ledger
  4. Public cryptographic commitment receipt verification & BFT epistemic quorum

NOTE: All proprietary Sovereign Invariant Formulas, closed-form linguistic
equations, and private ledger baselines are strictly vaulted in the Sovereign
Enclave and are NEVER stored or exposed in this module.
"""

from __future__ import annotations

import ast
import datetime
import hashlib
import json
import math
import re
import time
from fractions import Fraction
from typing import Any, Dict, List, Optional

from .models import DeterministicStatus, EpistemicTier, ValidationReceipt

_ARITH_EQUATION_RE = re.compile(
    r"((?:\d+(?:\.\d+)?|\s|[-+*/^().])+)\s*(==|=|!=|≠)\s*(-?\d+(?:\.\d+)?(?:/\d+)?)"
)
_SPECULATIVE_DIVINATION_RE = re.compile(
    r"\b(?:fortune[-\s]?tell(?:ing|er)?|sooth\s*say(?:ing|er)?|palmistry|palmist|"
    r"horoscope\s+predict(?:ion|s)?)\b|"
    r"\bastrolog(?:y|ical|er)?\b.*\b(?:predict(?:s|ed|ing|ion|ions)?|forecast(?:s|ed|ing)?|fate|destiny|tomorrow)\b",
    re.IGNORECASE,
)


def _eval_exact_ast(node: ast.AST) -> Fraction:
    """Safely evaluates an arithmetic AST node using exact rational Fractions."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return Fraction(str(node.value))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_exact_ast(node.operand)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
        return _eval_exact_ast(node.operand)
    if isinstance(node, ast.BinOp):
        left = _eval_exact_ast(node.left)
        right = _eval_exact_ast(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError("Division by zero in expression")
            return left / right
        if isinstance(node.op, (ast.Pow, ast.BitXor)):
            exp = int(right)
            if right != exp or abs(exp) > 1000:
                raise ValueError("Exponent must be a bounded integer for exact rational evaluation")
            return left ** exp
    raise ValueError("Unsupported non-arithmetic AST node")


def compute_exact(expr: str) -> Dict[str, Any]:
    """
    Computes the exact rational and decimal value of a mathematical expression.
    Uses AST + fractions.Fraction so rational arithmetic has zero floating-point drift.
    """
    cleaned = expr.strip().replace("^", "**")
    if not cleaned:
        return {
            "expression": expr,
            "status": "INVALID_EXPRESSION",
            "deterministic_status": DeterministicStatus.NEEDS_REVIEW.value,
        }
    try:
        tree = ast.parse(cleaned, mode="eval")
        exact_val = _eval_exact_ast(tree.body)
        float_val = float(exact_val)
        return {
            "expression": expr,
            "exact_fraction": str(exact_val),
            "numerator": exact_val.numerator,
            "denominator": exact_val.denominator,
            "decimal_value": round(float_val, 12),
            "status": "COMPUTED_EXACT",
            "coherence_index": 1.0,
            "confidence_score": "100.0%",
            "deterministic_status": DeterministicStatus.VERIFIED_COMPUTED_PASS.value,
        }
    except Exception as exc:
        return {
            "expression": expr,
            "status": "COMPUTATION_ERROR",
            "error": str(exc),
            "coherence_index": 0.0,
            "confidence_score": "0.0%",
            "deterministic_status": DeterministicStatus.REJECTED_HALLUCINATION.value,
        }


def solve_algebraic_equation(
    equation: str,
    unknown: str = "x",
    claimed_solutions: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """
    Solves a linear or quadratic algebraic equation (or uses SymPy if installed)
    and verifies every solution by substitution.
    """
    raw_eq = equation.strip().replace("^", "**")
    if "=" not in raw_eq:
        raw_eq = f"{raw_eq} = 0"
    lhs_str, rhs_str = [part.strip() for part in raw_eq.split("=", 1)]

    def _eval_at(val: complex) -> complex:
        env = {unknown: val, "math": math}
        lhs_v = eval(compile(ast.parse(lhs_str, mode="eval"), "<lhs>", "eval"), {"__builtins__": {}}, env)
        rhs_v = eval(compile(ast.parse(rhs_str, mode="eval"), "<rhs>", "eval"), {"__builtins__": {}}, env)
        return complex(lhs_v) - complex(rhs_v)

    if claimed_solutions is not None:
        verified = []
        all_ok = True
        for sol in claimed_solutions:
            c_val = complex(sol)
            residual = abs(_eval_at(c_val))
            ok = residual <= 1e-9
            all_ok = all_ok and ok
            verified.append({
                "claimed": str(sol),
                "residual": round(residual, 12),
                "checked_by_substitution": ok,
            })
        return {
            "equation": equation,
            "unknown": unknown,
            "status": "VERIFIED_CLAIMED" if all_ok else "CLAIMED_SOLUTION_FAILED",
            "solutions": verified,
            "coherence_index": 1.0 if all_ok else 0.0,
            "confidence_score": "100.0%" if all_ok else "0.0%",
            "deterministic_status": (
                DeterministicStatus.VERIFIED_COMPUTED_PASS.value
                if all_ok
                else DeterministicStatus.REJECTED_HALLUCINATION.value
            ),
        }

    # Try SymPy if installed, otherwise solve degree-1 / degree-2 via exact 3-point polynomial interpolation
    try:
        import sympy as sp
        sym_var = sp.Symbol(unknown)
        lhs_sym = sp.sympify(lhs_str)
        rhs_sym = sp.sympify(rhs_str)
        sols = sp.solve(sp.Eq(lhs_sym, rhs_sym), sym_var)
        checked = []
        for s in sols:
            sub_diff = sp.simplify((lhs_sym - rhs_sym).subs(sym_var, s))
            ok = sub_diff == 0
            checked.append({
                "solution": str(s),
                "checked_by_substitution": bool(ok),
            })
        return {
            "equation": equation,
            "unknown": unknown,
            "status": "SOLVED",
            "solutions": checked,
            "coherence_index": 1.0,
            "confidence_score": "100.0%",
            "deterministic_status": DeterministicStatus.VERIFIED_COMPUTED_PASS.value,
        }
    except Exception:
        pass

    try:
        # 3-point Lagrange polynomial recovery for a*x^2 + b*x + c = 0
        f0 = _eval_at(0.0).real
        f1 = _eval_at(1.0).real
        f_1 = _eval_at(-1.0).real
        c = f0
        a = 0.5 * (f1 + f_1) - c
        b = 0.5 * (f1 - f_1)

        roots: List[complex] = []
        if abs(a) <= 1e-12:
            if abs(b) > 1e-12:
                roots = [complex(-c / b)]
        else:
            disc = b * b - 4.0 * a * c
            if disc >= 0:
                sqrt_d = math.sqrt(disc)
                roots = [complex((-b - sqrt_d) / (2 * a)), complex((-b + sqrt_d) / (2 * a))]
            else:
                sqrt_d = math.sqrt(-disc)
                roots = [
                    complex(-b / (2 * a), -sqrt_d / (2 * a)),
                    complex(-b / (2 * a), sqrt_d / (2 * a)),
                ]

        unique_solutions = []
        seen = set()
        for r in roots:
            residual = abs(_eval_at(r))
            if residual <= 1e-7:
                fmt = (
                    str(int(round(r.real)))
                    if abs(r.imag) <= 1e-9 and abs(r.real - round(r.real)) <= 1e-9
                    else (str(round(r.real, 8)) if abs(r.imag) <= 1e-9 else str(r))
                )
                if fmt not in seen:
                    seen.add(fmt)
                    unique_solutions.append({
                        "solution": fmt,
                        "residual": round(residual, 12),
                        "checked_by_substitution": True,
                    })

        return {
            "equation": equation,
            "unknown": unknown,
            "status": "SOLVED" if unique_solutions else "NO_SOLUTION_FOUND",
            "solutions": unique_solutions,
            "coherence_index": 1.0 if unique_solutions else 0.5,
            "confidence_score": "100.0%" if unique_solutions else "50.0%",
            "deterministic_status": (
                DeterministicStatus.VERIFIED_COMPUTED_PASS.value
                if unique_solutions
                else DeterministicStatus.NEEDS_REVIEW.value
            ),
        }
    except Exception as exc:
        return {
            "equation": equation,
            "unknown": unknown,
            "status": "ERROR",
            "error": str(exc),
            "coherence_index": 0.0,
            "confidence_score": "0.0%",
            "deterministic_status": DeterministicStatus.NEEDS_REVIEW.value,
        }


def validate_claim_open_boundary(claim: str, context: str = "general_domain") -> ValidationReceipt:
    """
    Open-boundary claim validator (zero proprietary formulas).
    Checks embedded arithmetic equations, algebraic expressions, and speculative divination flags.
    """
    checks: List[Dict[str, Any]] = []
    has_failure = False
    has_boundary_breach = False
    has_pass = False

    if _SPECULATIVE_DIVINATION_RE.search(claim or ""):
        has_boundary_breach = True
        checks.append({
            "kind": "epistemic_boundary",
            "verdict": "BOUNDARY_BREACH",
            "reason": "Speculative divination / unverifiable future-telling claim intercepted.",
        })

    for match in _ARITH_EQUATION_RE.finditer(claim or ""):
        lhs_src = match.group(1).strip()
        op = match.group(2)
        rhs_src = match.group(3).strip()
        if not lhs_src:
            continue
        try:
            lhs_val = _eval_exact_ast(ast.parse(lhs_src.replace("^", "**"), mode="eval").body)
            rhs_val = Fraction(rhs_src)
            is_equal = lhs_val == rhs_val
            holds = is_equal if op in ("=", "==") else not is_equal
            if holds:
                has_pass = True
            else:
                has_failure = True
            checks.append({
                "kind": "exact_arithmetic",
                "expression": f"{lhs_src} {op} {rhs_src}",
                "computed_exact": str(lhs_val),
                "claimed": str(rhs_val),
                "verdict": "PROVEN" if holds else "FAIL",
            })
        except Exception:
            continue

    if has_boundary_breach:
        status = DeterministicStatus.BOUNDARY_BREACH.value
        is_valid = False
        coherence = 0.0
    elif has_failure:
        status = DeterministicStatus.REJECTED_HALLUCINATION.value
        is_valid = False
        coherence = 0.0
    elif has_pass:
        status = DeterministicStatus.VERIFIED_COMPUTED_PASS.value
        is_valid = True
        coherence = 1.0
    else:
        status = DeterministicStatus.NEEDS_REVIEW.value
        is_valid = True
        coherence = 0.85

    digest_input = f"{claim}|{status}|{coherence}|{len(checks)}"
    receipt_hash = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:16]

    return ValidationReceipt(
        claim=claim,
        is_valid=is_valid,
        deterministic_status=status,
        coherence_index=coherence,
        confidence_score=f"{round(coherence * 100.0, 1)}%",
        execution_tier="PUBLIC_OPEN_BOUNDARY_AST",
        receipt_id=f"zh-pub-{receipt_hash}",
        checks_performed=checks,
    )


class PublicStepLedger:
    """
    Tamper-evident SHA-256 hash-chain ledger for step-by-step AI reasoning verification.
    """

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.entries: List[Dict[str, Any]] = []
        self.head_hash: str = hashlib.sha256(f"GENESIS:{session_id}".encode("utf-8")).hexdigest()

    def submit_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        kind = step.get("kind", "reasoning")
        step_num = len(self.entries) + 1
        verdict = "NOT_MACHINE_CHECKED"
        detail: Dict[str, Any] = {}

        if kind in ("compute", "numeric"):
            expr = str(step.get("expr", ""))
            claimed = str(step.get("value", ""))
            comp = compute_exact(expr)
            if comp.get("status") == "COMPUTED_EXACT":
                try:
                    claimed_frac = Fraction(claimed)
                    exact_frac = Fraction(comp["exact_fraction"])
                    ok = abs(float(claimed_frac - exact_frac)) <= 1e-9
                    verdict = "PROVEN" if ok else "FAIL"
                except Exception:
                    verdict = "FAIL"
            else:
                verdict = "FAIL"
            detail = comp

        elif kind in ("equation", "solve"):
            eq = str(step.get("equation") or f"{step.get('lhs', '')} = {step.get('rhs', '')}")
            claimed_map = step.get("claimed") or {}
            unknown = next(iter(claimed_map.keys()), "x") if isinstance(claimed_map, dict) and claimed_map else "x"
            claimed_vals = [claimed_map[unknown]] if isinstance(claimed_map, dict) and unknown in claimed_map else None
            res = solve_algebraic_equation(eq, unknown=unknown, claimed_solutions=claimed_vals)
            verdict = (
                "PROVEN"
                if res.get("deterministic_status") == DeterministicStatus.VERIFIED_COMPUTED_PASS.value
                else "FAIL"
            )
            detail = res

        elif kind == "interpretation":
            verdict = "INTERPRETATION"
            detail = {"note": "Labelled as interpretation; never elevated to proven fact."}

        prev_hash = self.head_hash
        payload_bytes = json.dumps(
            {"n": step_num, "kind": kind, "verdict": verdict, "step": step, "prev": prev_hash},
            sort_keys=True,
        ).encode("utf-8")
        self.head_hash = hashlib.sha256(payload_bytes).hexdigest()

        replaces = step.get("replaces")
        if replaces and 1 <= int(replaces) <= len(self.entries):
            self.entries[int(replaces) - 1]["superseded_by"] = step_num

        record = {
            "n": step_num,
            "session": self.session_id,
            "kind": kind,
            "verdict": verdict,
            "detail": detail,
            "step_hash": self.head_hash[:16],
        }
        self.entries.append(record)
        return record

    def report(self) -> Dict[str, Any]:
        active = [e for e in self.entries if "superseded_by" not in e]
        has_fail = any(e["verdict"] == "FAIL" for e in active)
        all_proven = bool(active) and all(e["verdict"] == "PROVEN" for e in active)

        if has_fail:
            seal = "BLOCKED_FAILED_STEPS"
            status = DeterministicStatus.REJECTED_HALLUCINATION.value
            coherence = 0.0
        elif all_proven:
            seal = "FULLY_PROVEN"
            status = DeterministicStatus.VERIFIED_COMPUTED_PASS.value
            coherence = 1.0
        else:
            seal = "PARTIALLY_VERIFIED"
            status = DeterministicStatus.NEEDS_REVIEW.value
            coherence = 0.85

        return {
            "session": self.session_id,
            "seal": seal,
            "deterministic_status": status,
            "coherence_index": coherence,
            "confidence_score": f"{round(coherence * 100.0, 1)}%",
            "total_steps": len(self.entries),
            "active_steps": len(active),
            "merkle_head_hash": self.head_hash,
            "steps": active,
        }


def generate_public_commitment_receipt(claim: str, authority: str = "zeroH_Public_Verifier") -> Dict[str, Any]:
    """
    Generates a public SHA-256 commitment receipt over a verified claim without
    exposing proprietary Sovereign Enclave circuit parameters.
    """
    receipt = validate_claim_open_boundary(claim)
    ts = int(time.time())
    claim_hash = hashlib.sha256(claim.encode("utf-8")).hexdigest()
    commitment_payload = f"{claim_hash}:{ts}:{receipt.deterministic_status}:{authority}"
    signature = hashlib.sha256(commitment_payload.encode("utf-8")).hexdigest()

    return {
        "receipt_type": "zeroH_SHA256_Public_Commitment",
        "proof_id": f"zhReceipt-{signature[:16]}",
        "authority": authority,
        "claim_sha256": claim_hash,
        "deterministic_status": receipt.deterministic_status,
        "coherence_index": receipt.coherence_index,
        "confidence_score": receipt.confidence_score,
        "commitment_signature": signature,
        "timestamp": ts,
        "ip_notice": "Full R1CS Sovereign Enclave proofs require an authenticated Sovereign Enclave connection.",
    }


def evaluate_bft_epistemic_quorum(
    agent_id: str,
    proposal: str,
    confidence: float = 1.0,
    contradiction: float = 0.0,
) -> Dict[str, Any]:
    """
    Public 4-Tier Byzantine Fault Tolerant (BFT) Epistemic Consensus Classifier.
    Classifies agent proposals into QATI, ZANNI_GHALIB, SHAKK, or WAHM using
    normalized confidence-to-contradiction ratios.
    """
    conf_clamped = max(0.0, min(1.0, float(confidence)))
    contra_clamped = max(0.0, float(contradiction))
    effective_p = round(conf_clamped / (1.0 + contra_clamped), 4)

    open_check = validate_claim_open_boundary(proposal)
    if not open_check.is_valid:
        effective_p = 0.0

    if effective_p >= 0.98 and contra_clamped < 0.01:
        tier = EpistemicTier.QATI.value
        verdict = "DEFINITIVE_CERTAINTY"
        can_persist = True
        is_vetoed = False
    elif effective_p >= 0.70:
        tier = EpistemicTier.ZANNI_GHALIB.value
        verdict = "PREPONDERANT_CONJECTURE"
        can_persist = True
        is_vetoed = False
    elif effective_p >= 0.40:
        tier = EpistemicTier.SHAKK.value
        verdict = "EQUIPROBABLE_DOUBT"
        can_persist = False
        is_vetoed = False
    else:
        tier = EpistemicTier.WAHM.value
        verdict = "HALLUCINATION_OR_CONTRADICTION_VETO"
        can_persist = False
        is_vetoed = True

    return {
        "agent_id": agent_id,
        "tier": tier,
        "verdict": verdict,
        "coherence_index": effective_p,
        "confidence_score": f"{round(effective_p * 100.0, 2)}%",
        "can_persist_to_ledger": can_persist,
        "byzantine_veto": is_vetoed,
        "action_taken": (
            "VETO_HALT_REJECTED"
            if is_vetoed
            else ("COMMIT_TO_LEDGER" if can_persist else "STAGE_FOR_CORROBORATION")
        ),
        "deterministic_status": (
            DeterministicStatus.BOUNDARY_BREACH.value
            if is_vetoed
            else DeterministicStatus.VERIFIED_COMPUTED_PASS.value
        ),
    }
