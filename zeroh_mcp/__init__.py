# -*- coding: utf-8 -*-
"""
zeroH MCP — Public Model Context Protocol Server & Verification SDK
===================================================================
Provides deterministic hallucination interception, step-by-step cryptographic
proof ledgers, exact rational arithmetic/algebraic verification, and seamless
bridging to the zeroH Sovereign Enclave without exposing proprietary formulas.
"""

__version__ = "1.2.0"

from .models import (
    DeterministicStatus,
    EpistemicTier,
    ValidationReceipt,
)
from .client import ZeroHClient
from .guardrail import (
    ZeroHGuardrail,
    ZeroHHallucinationError,
    zeroh_guardrail,
)
from .server import handle_mcp_request, serve_stdio, serve_http

__all__ = [
    "__version__",
    "DeterministicStatus",
    "EpistemicTier",
    "ValidationReceipt",
    "ZeroHClient",
    "ZeroHGuardrail",
    "ZeroHHallucinationError",
    "zeroh_guardrail",
    "handle_mcp_request",
    "serve_stdio",
    "serve_http",
]
