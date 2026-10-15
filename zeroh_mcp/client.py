# -*- coding: utf-8 -*-
"""
zeroH Public Python SDK Client (zeroh_mcp.client)
=================================================
Provides a clean programmatic interface to the zeroH verification engine
across both Open-Boundary local mode and Remote Sovereign Enclave mode.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .enclave_bridge import SovereignEnclaveBridge


class ZeroHClient:
    """
    Public SDK client for zeroH MCP & Sovereign Enclave verification.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        self._bridge = SovereignEnclaveBridge(
            api_url=api_url,
            api_key=api_key,
            timeout=timeout,
        )

    def validate(self, claim: str, context: str = "general_domain") -> Dict[str, Any]:
        return self._bridge.validate_claim(claim=claim, context=context)

    def validate_batch(self, claims: List[str], context: str = "general_domain") -> List[Dict[str, Any]]:
        return [self.validate(c, context=context) for c in claims]

    def verify_step(self, session: str, step: Dict[str, Any]) -> Dict[str, Any]:
        return self._bridge.verify_step(session=session, step=step)

    def session_report(self, session: str) -> Dict[str, Any]:
        return self._bridge.session_report(session=session)

    def compute(self, expr: str) -> Dict[str, Any]:
        return self._bridge.compute(expr=expr)

    def solve_equation(
        self,
        equation: str,
        unknown: str = "x",
        claimed: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        return self._bridge.solve_equation(equation=equation, unknown=unknown, claimed=claimed)

    def intercept(self, token: str) -> Dict[str, Any]:
        return self._bridge.intercept_token(token=token)

    def zk_verify_receipt(self, claim: str, authority: str = "zeroH_Public_Verifier") -> Dict[str, Any]:
        return self._bridge.zk_verify_receipt(claim=claim, authority=authority)

    def epistemic_consensus(
        self,
        agent_id: str,
        proposal: str,
        confidence: float = 1.0,
        contradiction: float = 0.0,
    ) -> Dict[str, Any]:
        return self._bridge.epistemic_consensus(
            agent_id=agent_id,
            proposal=proposal,
            confidence=confidence,
            contradiction=contradiction,
        )

    def status(self) -> Dict[str, Any]:
        return self._bridge.enclave_status()
