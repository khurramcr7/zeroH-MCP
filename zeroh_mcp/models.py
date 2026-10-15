# -*- coding: utf-8 -*-
"""
zeroH MCP Public Data Models & Standardized Output Contracts
============================================================
Defines public-safe data structures returned by zeroH MCP tools.
All internal enclave baselines and proprietary equations remain abstracted
behind normalized [0.0, 1.0] coherence indices and cryptographic receipts.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
import datetime


class DeterministicStatus(str, Enum):
    VERIFIED_COMPUTED_PASS = "VERIFIED_COMPUTED_PASS"
    REJECTED_HALLUCINATION = "REJECTED_HALLUCINATION"
    BOUNDARY_BREACH = "BOUNDARY_BREACH"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class EpistemicTier(str, Enum):
    QATI = "QATI"                    # Definitive certainty (verified proof / zero contradiction)
    ZANNI_GHALIB = "ZANNI_GHALIB"    # Preponderant corroborated evidence
    SHAKK = "SHAKK"                  # Equiprobable doubt (staged for corroboration)
    WAHM = "WAHM"                    # Hallucination / contradicted assertion (automatic veto)


@dataclass
class ValidationReceipt:
    claim: str
    is_valid: bool
    deterministic_status: str
    coherence_index: float
    confidence_score: str
    execution_tier: str
    receipt_id: str
    checks_performed: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
