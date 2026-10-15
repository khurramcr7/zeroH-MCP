# -*- coding: utf-8 -*-
"""
zeroH Sovereign Enclave Bridge (zeroh_mcp.enclave_bridge)
=========================================================
Routes verification requests across the split-enclave security boundary:
  1. Remote Sovereign Enclave Gateway (`ZEROH_API_URL` + `ZEROH_API_KEY`)
     -> Calls the remote HTTPS zeroH Enterprise Gateway where proprietary
        formulas and canonical ledgers execute inside a secure server enclave.
  2. Public Open-Boundary AST Verifier (default fallback when offline)
     -> Executes transparent exact rational arithmetic, algebraic substitution,
        and SHA-256 step-ledger verification locally with zero exposure of
        proprietary formulas.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from .models import DeterministicStatus
from .public_verifier import (
    PublicStepLedger,
    compute_exact,
    evaluate_bft_epistemic_quorum,
    generate_public_commitment_receipt,
    solve_algebraic_equation,
    validate_claim_open_boundary,
)


class SovereignEnclaveBridge:
    """
    Manages communication with the remote zeroH Sovereign Enclave API while
    providing seamless fallback to the public open-boundary AST verifier.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        self.api_url = (api_url or os.environ.get("ZEROH_API_URL", "")).strip().rstrip("/")
        self.api_key = (api_key or os.environ.get("ZEROH_API_KEY", "")).strip()
        self.timeout = timeout
        self._ledgers: Dict[str, PublicStepLedger] = {}

    @property
    def is_enclave_configured(self) -> bool:
        return bool(self.api_url)

    def _post_enclave(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.is_enclave_configured:
            return None
        url = f"{self.api_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "zeroH-MCP-Public-Client/1.0.0",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
                return self._sanitize_enclave_response(raw)
        except Exception:
            return None

    @staticmethod
    def _sanitize_enclave_response(raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strips any internal baseline fields if present, exposing only normalized
        Coherence Index [0.0-1.0], Confidence Score %, and Deterministic Status.
        """
        redacted_keys = {
            "invariant_baseline_mu",
            "boundary_ceiling_b_max",
            "S_AQL",
            "s_aql",
            "mu_test",
            "mu_note",
            "entropy_ceiling",
        }
        return {k: v for k, v in raw.items() if k not in redacted_keys}

    def validate_claim(self, claim: str, context: str = "general_domain") -> Dict[str, Any]:
        remote_res = self._post_enclave("/v1/validate", {"claim": claim, "context": context})
        if remote_res is not None:
            remote_res["execution_tier"] = "REMOTE_SOVEREIGN_ENCLAVE"
            return remote_res
        return validate_claim_open_boundary(claim, context=context).to_dict()

    def intercept_token(self, token: str) -> Dict[str, Any]:
        remote_res = self._post_enclave("/v1/intercept", {"token": token})
        if remote_res is not None:
            remote_res["execution_tier"] = "REMOTE_SOVEREIGN_ENCLAVE"
            return remote_res
        return {
            "token": token,
            "status": "ENCLAVE_REQUIRED",
            "deterministic_status": DeterministicStatus.NEEDS_REVIEW.value,
            "coherence_index": 0.0,
            "confidence_score": "0.0%",
            "message": (
                "Canonical ledger token interception requires an active Sovereign Enclave "
                "connection (set ZEROH_API_URL and ZEROH_API_KEY). Proprietary ledger "
                "tensors are not bundled in the public repository."
            ),
        }

    def verify_step(self, session: str, step: Dict[str, Any]) -> Dict[str, Any]:
        ledger = self._ledgers.setdefault(session or "default", PublicStepLedger(session or "default"))
        return ledger.submit_step(step)

    def session_report(self, session: str) -> Dict[str, Any]:
        name = session or "default"
        if name not in self._ledgers:
            return {
                "session": name,
                "seal": "NOT_PROVEN",
                "deterministic_status": DeterministicStatus.NEEDS_REVIEW.value,
                "coherence_index": 0.0,
                "confidence_score": "0.0%",
                "reason": "No steps were submitted for this session.",
            }
        return self._ledgers[name].report()

    def compute(self, expr: str) -> Dict[str, Any]:
        return compute_exact(expr)

    def solve_equation(
        self,
        equation: str,
        unknown: str = "x",
        claimed: Optional[list] = None,
    ) -> Dict[str, Any]:
        return solve_algebraic_equation(equation, unknown=unknown, claimed_solutions=claimed)

    def zk_verify_receipt(self, claim: str, authority: str = "zeroH_Public_Verifier") -> Dict[str, Any]:
        remote_res = self._post_enclave("/v1/zk-verify", {"claim": claim, "authority": authority})
        if remote_res is not None:
            remote_res["execution_tier"] = "REMOTE_SOVEREIGN_ENCLAVE"
            return remote_res
        return generate_public_commitment_receipt(claim, authority=authority)

    def epistemic_consensus(
        self,
        agent_id: str,
        proposal: str,
        confidence: float = 1.0,
        contradiction: float = 0.0,
    ) -> Dict[str, Any]:
        remote_res = self._post_enclave(
            "/v1/epistemic-bft",
            {
                "agent_id": agent_id,
                "proposal": proposal,
                "confidence": confidence,
                "contradiction": contradiction,
            },
        )
        if remote_res is not None:
            remote_res["execution_tier"] = "REMOTE_SOVEREIGN_ENCLAVE"
            return remote_res
        return evaluate_bft_epistemic_quorum(
            agent_id=agent_id,
            proposal=proposal,
            confidence=confidence,
            contradiction=contradiction,
        )

    def enclave_status(self) -> Dict[str, Any]:
        return {
            "server": "zeroh-mcp",
            "version": "1.0.0",
            "enclave_mode": "REMOTE_SOVEREIGN_ENCLAVE" if self.is_enclave_configured else "PUBLIC_OPEN_BOUNDARY_AST",
            "enclave_url_configured": self.is_enclave_configured,
            "proprietary_formulas_exposed": False,
            "ip_protection_status": "SOVEREIGN_VAULTED_SAFE",
            "coherence_index": 1.0,
            "confidence_score": "100.0%",
            "deterministic_status": DeterministicStatus.VERIFIED_COMPUTED_PASS.value,
        }
