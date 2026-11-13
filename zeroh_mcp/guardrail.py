# -*- coding: utf-8 -*-
"""
zeroH Drop-In LLM Guardrail & Decorator SDK (zeroh_mcp.guardrail)
=================================================================
Equips Python AI applications, autonomous agents, and RAG pipelines
(OpenAI, Anthropic, Google Gemini, LangChain, CrewAI, or custom endpoints)
with zero-config deterministic hallucination interception and tamper-evident
SHA-256 session proof ledgers.

When enclave-gated enterprise capabilities are requested without an active
ONEXI_API_KEY, structured upgrade metadata for ONE XI Cloud ($49/mo Pro,
$199/mo Team, $499/mo Unlimited) is attached automatically.
"""

from __future__ import annotations

import functools
import re
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from .client import ZeroHClient

F = TypeVar("F", bound=Callable[..., Any])

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?\n])\s+")

UPGRADE_TIERS_PUBLIC = {
    "pro_49": {
        "plan": "ONE XI Cloud — Pro Pass ($49/mo)",
        "checkout_url": "https://buy.polar.sh/polar_cl_yiaY2QaaJrj4WuWm1bpQWOIPNDogghaLT2A0o0JczDW",
    },
    "team_199": {
        "plan": "ONE XI Cloud — Team License ($199/mo)",
        "checkout_url": "https://buy.polar.sh/polar_cl_2rGWKtRrTpFyrMjKTRwRSv9Cb8F4FZmvW322i16kIwX",
    },
    "unlimited_499": {
        "plan": "ONE XI Cloud — Unlimited Institutional Seat ($499/mo)",
        "checkout_url": "https://buy.polar.sh/polar_cl_eXsIPJGpi0QnzjA913s581oKVvBz8ooPNUgOa49Ofe8",
    },
}


class ZeroHHallucinationError(RuntimeError):
    """Raised when strict guardrail mode intercepts a deterministic hallucination."""

    def __init__(self, message: str, report: Dict[str, Any]) -> None:
        super().__init__(message)
        self.report = report


def _extract_text_payload(output: Any) -> str:
    """Extracts text from raw strings, dicts, or common LLM SDK response objects."""
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        for key in ("content", "text", "output", "answer", "response"):
            val = output.get(key)
            if isinstance(val, str):
                return val
        choices = output.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
            if isinstance(msg.get("content"), str):
                return msg["content"]
    # Duck-typing for OpenAI / Anthropic / Google GenAI SDK objects
    if hasattr(output, "text") and isinstance(getattr(output, "text"), str):
        return getattr(output, "text")
    if hasattr(output, "choices"):
        choices = getattr(output, "choices")
        if choices and hasattr(choices[0], "message"):
            content = getattr(choices[0].message, "content", None)
            if isinstance(content, str):
                return content
    if hasattr(output, "content"):
        content = getattr(output, "content")
        if isinstance(content, str):
            return content
        if isinstance(content, list) and content and hasattr(content[0], "text"):
            return str(getattr(content[0], "text"))
    return str(output)


def split_candidate_claims(text: str) -> List[str]:
    """Splits an LLM completion into non-empty atomic sentence/line claims."""
    if not text or not text.strip():
        return []
    parts = _SENTENCE_SPLIT_RE.split(text.strip())
    claims: List[str] = []
    for part in parts:
        cleaned = part.strip()
        if cleaned:
            claims.append(cleaned)
    return claims


class ZeroHGuardrail:
    """
    Programmatic guardrail middleware for intercepting hallucinations in LLM outputs
    and sealing verified multi-claim responses in a SHA-256 step ledger.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        context: str = "general_domain",
        strict: bool = False,
        timeout: float = 10.0,
    ) -> None:
        self.client = ZeroHClient(api_url=api_url, api_key=api_key, timeout=timeout)
        self.context = context
        self.strict = strict

    def inspect_text(
        self,
        text: str,
        session_id: Optional[str] = None,
        strict: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Inspects a text completion, validates each atomic claim, records verified
        or rejected steps into a tamper-evident session ledger, and returns a
        cryptographically sealed audit report.
        """
        enforce_strict = self.strict if strict is None else strict
        sid = session_id or f"zeroh-guard-{uuid.uuid4().hex[:12]}"
        claims = split_candidate_claims(text)

        claim_results: List[Dict[str, Any]] = []
        rejected_claims: List[Dict[str, Any]] = []
        verified_count = 0

        for idx, claim in enumerate(claims, start=1):
            res = self.client.validate(claim=claim, context=self.context)
            det_status = str(res.get("deterministic_status", ""))
            is_rejected = det_status in {
                "REJECTED_HALLUCINATION",
                "BOUNDARY_BREACH",
                "REJECTED_SPECULATIVE",
            }
            if det_status == "VERIFIED_COMPUTED_PASS":
                verified_count += 1

            # Record step in tamper-evident SHA-256 session ledger
            self.client.verify_step(
                session=sid,
                step={
                    "id": f"step_{idx}",
                    "kind": "reasoning",
                    "claim": claim,
                    "verified": det_status == "VERIFIED_COMPUTED_PASS",
                    "status": det_status,
                },
            )

            entry = {
                "index": idx,
                "claim": claim,
                "deterministic_status": det_status,
                "coherence_index": res.get("coherence_index"),
                "confidence_score": res.get("confidence_score"),
                "receipt_id": res.get("receipt_id") or res.get("receipt_sha256"),
                "checks_performed": res.get("checks_performed") or res.get("findings", []),
            }
            claim_results.append(entry)
            if is_rejected:
                rejected_claims.append(entry)

        ledger_summary = self.client.session_report(session=sid)
        enclave_info = self.client.status()
        is_cloud_active = bool(enclave_info.get("remote_enclave_configured"))

        if rejected_claims:
            overall_status = "REJECTED_HALLUCINATION"
        elif verified_count > 0:
            overall_status = "VERIFIED_COMPUTED_PASS"
        else:
            overall_status = "NEEDS_REVIEW"

        report: Dict[str, Any] = {
            "guardrail": "zeroH Deterministic Guardrail v1.2",
            "session_id": sid,
            "overall_status": overall_status,
            "passed": len(rejected_claims) == 0,
            "total_claims_checked": len(claims),
            "verified_claims_count": verified_count,
            "rejected_count": len(rejected_claims),
            "rejected_claims": rejected_claims,
            "claims": claim_results,
            "session_merkle_head": (
                ledger_summary.get("merkle_head_hash")
                or ledger_summary.get("merkle_head_sha256")
                or ledger_summary.get("session_hash")
            ),
            "cloud_enclave_active": is_cloud_active,
        }

        if not is_cloud_active:
            report["upgrade_options"] = {
                "message": (
                    "Running in zeroH Open-Boundary Local Mode. Connect ONEXI_API_KEY "
                    "to unlock ONE XI Cloud Enclave verification across Quantum, 8-Gate "
                    "Executable Code Sandbox, and 121.8M-Word Classical Concordance."
                ),
                "plans": UPGRADE_TIERS_PUBLIC,
                "portal_url": "https://onexi.tech/zeroh",
            }

        if enforce_strict and rejected_claims:
            first_bad = rejected_claims[0]["claim"]
            raise ZeroHHallucinationError(
                f"zeroH Guardrail blocked hallucinated claim: {first_bad!r}",
                report=report,
            )

        return report

    def wrap(
        self,
        fn: F,
        *,
        strict: Optional[bool] = None,
        return_tuple: bool = False,
    ) -> Callable[..., Any]:
        """Wraps any synchronous LLM/agent callable with deterministic interception."""

        @functools.wraps(fn)
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            raw_output = fn(*args, **kwargs)
            extracted = _extract_text_payload(raw_output)
            report = self.inspect_text(extracted, strict=strict)
            if return_tuple:
                return raw_output, report
            if isinstance(raw_output, dict):
                enriched = dict(raw_output)
                enriched["_zeroh_audit"] = report
                return enriched
            return raw_output

        return _wrapped


def zeroh_guardrail(
    fn: Optional[F] = None,
    *,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    context: str = "general_domain",
    strict: bool = True,
    return_tuple: bool = False,
) -> Any:
    """
    Drop-in decorator for LLM calls and agent tools.

    Example:
        @zeroh_guardrail(strict=True)
        def ask_agent(prompt: str) -> str:
            return llm.complete(prompt)
    """
    guard = ZeroHGuardrail(
        api_url=api_url,
        api_key=api_key,
        context=context,
        strict=strict,
    )
    if fn is not None:
        return guard.wrap(fn, strict=strict, return_tuple=return_tuple)

    def _decorator(target: F) -> Callable[..., Any]:
        return guard.wrap(target, strict=strict, return_tuple=return_tuple)

    return _decorator
