# -*- coding: utf-8 -*-
"""
zeroH MCP Server — Public Model Context Protocol Server (zeroh_mcp.server)
==========================================================================
Exposes deterministic hallucination interception, exact arithmetic/algebraic
verification, SHA-256 step-ledger proofs, BFT epistemic quorum evaluation,
and Sovereign Enclave bridging over standard MCP JSON-RPC 2.0 (stdio & HTTP).

Run via Stdio (default for Claude Desktop, Cursor, Antigravity IDE, Windsurf):
    python -m zeroh_mcp.server
    zeroh-mcp

Run via HTTP:
    python -m zeroh_mcp.server --http --port 8090
"""

from __future__ import annotations

import json
import sys
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, List, Optional

from .enclave_bridge import SovereignEnclaveBridge

if sys.platform == "win32":
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SERVER_NAME = "zeroh-mcp"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

_BRIDGE = SovereignEnclaveBridge()


def _schema(properties: Dict[str, Any], required: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(required or []),
    }


TOOLS: List[Dict[str, Any]] = [
    {
        "name": "validate_claim",
        "description": (
            "Intercept and validate a factual, mathematical, or scientific claim before presenting it. "
            "Returns Coherence Index (0.0-1.0), Confidence Score (0%-100%), and Deterministic Status "
            "(VERIFIED_COMPUTED_PASS, REJECTED_HALLUCINATION, BOUNDARY_BREACH, or NEEDS_REVIEW)."
        ),
        "inputSchema": _schema(
            {
                "claim": {
                    "type": "string",
                    "description": "The text proposition, calculation, or claim to validate.",
                },
                "context": {
                    "type": "string",
                    "description": "Validation domain or context (default: 'general_domain').",
                },
            },
            required=["claim"],
        ),
    },
    {
        "name": "verify_step",
        "description": (
            "Submit a single reasoning or mathematical step to the tamper-evident SHA-256 session ledger "
            "before stating it. Supported step kinds: 'compute' {expr, value}, 'solve' {equation, claimed: {x: val}}, "
            "'reasoning' {text}, 'interpretation' {text}."
        ),
        "inputSchema": _schema(
            {
                "session": {
                    "type": "string",
                    "description": "Session identifier for the multi-step reasoning chain.",
                },
                "step": {
                    "type": "object",
                    "description": "Step object containing 'kind' and kind-specific parameters.",
                },
            },
            required=["session", "step"],
        ),
    },
    {
        "name": "session_report",
        "description": (
            "Seal and audit all steps submitted in a reasoning session. Returns FULLY_PROVEN only if "
            "every active step was deterministically proven, along with the SHA-256 Merkle head hash."
        ),
        "inputSchema": _schema(
            {
                "session": {
                    "type": "string",
                    "description": "Session identifier to seal and report.",
                }
            },
            required=["session"],
        ),
    },
    {
        "name": "compute",
        "description": (
            "Compute the exact rational fraction and decimal value of a numeric expression using "
            "zero-drift AST rational arithmetic."
        ),
        "inputSchema": _schema(
            {
                "expr": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '(144 / 12) + 7').",
                }
            },
            required=["expr"],
        ),
    },
    {
        "name": "solve_equation",
        "description": (
            "Solve an algebraic equation and verify every solution by exact substitution."
        ),
        "inputSchema": _schema(
            {
                "equation": {
                    "type": "string",
                    "description": "Algebraic equation (e.g., 'x**2 - 5*x + 6 = 0').",
                },
                "unknown": {
                    "type": "string",
                    "description": "Variable symbol to solve for (default: 'x').",
                },
                "claimed": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Optional list of claimed solutions to check by substitution.",
                },
            },
            required=["equation"],
        ),
    },
    {
        "name": "intercept_token",
        "description": (
            "Query the Sovereign Enclave canonical ledger for a token or root reference. "
            "Requires an authenticated Sovereign Enclave connection (ZEROH_API_URL)."
        ),
        "inputSchema": _schema(
            {
                "token": {
                    "type": "string",
                    "description": "Token or reference identifier to look up in the Sovereign Enclave.",
                }
            },
            required=["token"],
        ),
    },
    {
        "name": "zk_verify_receipt",
        "description": (
            "Generate a cryptographic commitment receipt over a verified claim (or request an R1CS proof "
            "from a connected Sovereign Enclave)."
        ),
        "inputSchema": _schema(
            {
                "claim": {
                    "type": "string",
                    "description": "Claim text to bind into a cryptographic verification receipt.",
                },
                "authority": {
                    "type": "string",
                    "description": "Verification authority label (default: 'zeroH_Public_Verifier').",
                },
            },
            required=["claim"],
        ),
    },
    {
        "name": "epistemic_consensus",
        "description": (
            "Byzantine Fault Tolerant (BFT) Multi-Agent Epistemic Consensus Gate. Evaluates agent proposals "
            "across the 4-tier epistemic lattice (QATI, ZANNI_GHALIB, SHAKK, WAHM) with automatic hallucination veto."
        ),
        "inputSchema": _schema(
            {
                "agent_id": {
                    "type": "string",
                    "description": "Identifier of the proposing agent.",
                },
                "proposal": {
                    "type": "string",
                    "description": "Proposed statement or calculation to evaluate.",
                },
                "confidence": {
                    "type": "number",
                    "description": "Reported confidence score in [0.0, 1.0].",
                },
                "contradiction": {
                    "type": "number",
                    "description": "Measured contradiction evidence in [0.0, 1.0].",
                },
            },
            required=["proposal"],
        ),
    },
    {
        "name": "enclave_status",
        "description": (
            "Check the health, execution tier, and IP protection status of the zeroH MCP server and "
            "Sovereign Enclave bridge."
        ),
        "inputSchema": _schema({}),
    },
]

HANDLERS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "validate_claim": lambda a: _BRIDGE.validate_claim(
        claim=str(a.get("claim", "")),
        context=str(a.get("context", "general_domain")),
    ),
    "verify_step": lambda a: _BRIDGE.verify_step(
        session=str(a.get("session", "default")),
        step=dict(a.get("step") or {}),
    ),
    "session_report": lambda a: _BRIDGE.session_report(
        session=str(a.get("session", "default")),
    ),
    "compute": lambda a: _BRIDGE.compute(
        expr=str(a.get("expr", "")),
    ),
    "solve_equation": lambda a: _BRIDGE.solve_equation(
        equation=str(a.get("equation", "")),
        unknown=str(a.get("unknown", "x")),
        claimed=a.get("claimed"),
    ),
    "intercept_token": lambda a: _BRIDGE.intercept_token(
        token=str(a.get("token", "")),
    ),
    "zk_verify_receipt": lambda a: _BRIDGE.zk_verify_receipt(
        claim=str(a.get("claim", "")),
        authority=str(a.get("authority", "zeroH_Public_Verifier")),
    ),
    "epistemic_consensus": lambda a: _BRIDGE.epistemic_consensus(
        agent_id=str(a.get("agent_id", "agent_worker")),
        proposal=str(a.get("proposal", "")),
        confidence=float(a.get("confidence", 1.0)),
        contradiction=float(a.get("contradiction", 0.0)),
    ),
    "enclave_status": lambda _a: _BRIDGE.enclave_status(),
}


def _wrap_text_content(payload: Any) -> Dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            }
        ]
    }


def handle_mcp_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Processes a single JSON-RPC 2.0 MCP request."""
    method = req.get("method")
    msg_id = req.get("id")

    if method == "notifications/initialized" or msg_id is None:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                },
                "capabilities": {
                    "tools": {},
                },
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS},
        }

    if method == "tools/call":
        params = req.get("params") or {}
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        if tool_name not in HANDLERS:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: '{tool_name}'",
                },
            }
        try:
            res = HANDLERS[tool_name](arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": _wrap_text_content(res),
            }
        except Exception as exc:
            traceback.print_exc(file=sys.stderr)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}],
                },
            }

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: '{method}'",
        },
    }


def serve_stdio() -> None:
    """Runs the MCP JSON-RPC 2.0 loop over standard input/output."""
    for line in sys.stdin:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            req = json.loads(stripped)
            resp = handle_mcp_request(req)
        except json.JSONDecodeError as exc:
            resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def serve_http(host: str = "127.0.0.1", port: int = 8090) -> None:
    """Runs a lightweight HTTP JSON-RPC 2.0 server for remote/containerized MCP clients."""

    class MCPHTTPHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path in ("/", "/health"):
                body = json.dumps(_BRIDGE.enclave_status(), indent=2).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_error(404)

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            try:
                req = json.loads(raw)
                resp = handle_mcp_request(req) or {"jsonrpc": "2.0", "result": "ok"}
                code = 200
            except Exception as exc:
                resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
                code = 400
            body = json.dumps(resp, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = HTTPServer((host, port), MCPHTTPHandler)
    print(f"zeroH MCP HTTP Server listening on http://{host}:{port}", file=sys.stderr)
    server.serve_forever()


def main() -> None:
    if "--http" in sys.argv:
        port = 8090
        if "--port" in sys.argv:
            idx = sys.argv.index("--port")
            if idx + 1 < len(sys.argv):
                port = int(sys.argv[idx + 1])
        serve_http(port=port)
    else:
        serve_stdio()


if __name__ == "__main__":
    main()
