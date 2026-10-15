# zeroH MCP (`zeroh-mcp`)

[![Protocol: MCP 2024-11-05](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io)
[![IP Protection: Sovereign Enclave Vaulted](https://img.shields.io/badge/Proprietary_Formulas-Vaulted_%26_Non--Exposed-success.svg)](./SECURITY_AND_IP_BOUNDARY.md)
[![License: MIT Client](https://img.shields.io/badge/License-MIT_Client-green.svg)](./LICENSE)

**zeroH MCP** is the official **Model Context Protocol (MCP)** server and Python SDK for the **zeroH Deterministic AI Hallucination Guardrail & Step-by-Step Proof Ledger**.

It enables AI coding assistants, autonomous agents, and IDE environments (**Claude Desktop**, **Antigravity IDE**, **Cursor**, **Windsurf**, and custom MCP hosts) to intercept arithmetic/algebraic hallucinations, seal multi-step reasoning chains with SHA-256 Merkle commitments, and bridge seamlessly to the **zeroH Sovereign Enclave**—while keeping all proprietary Sovereign Invariant Formulas, baselines, and canonical ledger tensors 100% vaulted and non-exposed.

---

## Architectural Highlights & IP Boundary

`zeroH-MCP` operates across a strict **Dual-Tier Split-Enclave Architecture**:

1. **Tier 1 — Public Open-Boundary AST Verifier (Zero-Config Local Mode)**:
   - Works out-of-the-box with zero external dependencies.
   - **Exact Rational Arithmetic (`compute`, `validate_claim`)**: Evaluates numerical expressions via Python `ast` and `fractions.Fraction` to eliminate floating-point drift and catch calculation hallucinations (`12 * 12 = 145` $\rightarrow$ `REJECTED_HALLUCINATION`).
   - **Algebraic Substitution Verification (`solve_equation`, `verify_step`)**: Solves equations and verifies every candidate root by exact substitution.
   - **Tamper-Evident SHA-256 Step Ledger (`verify_step`, `session_report`)**: Tracks step-by-step reasoning chains and issues a `FULLY_PROVEN` cryptographic seal only when every active step in the chain is verified.
   - **Byzantine Fault Tolerant (BFT) Epistemic Consensus (`epistemic_consensus`)**: Classifies multi-agent proposals across the 4-tier epistemic lattice (`QATI`, `ZANNI_GHALIB`, `SHAKK`, `WAHM`) with automatic hallucination veto.

2. **Tier 2 — Remote Sovereign Enclave Bridge (`ZEROH_API_URL` + `ZEROH_API_KEY`)**:
   - When configured with a zeroH Enterprise Enclave key, `zeroh-mcp` routes deep verification and canonical token interception (`intercept_token`, `validate_claim`, `zk_verify_receipt`) to the air-gapped Sovereign Enclave over HTTPS.
   - All proprietary invariant constants, closed-form equations, and canonical ledger tensors remain strictly inside the remote enclave; only normalized **Coherence Index** ($0.0 - 1.0$), **Confidence Score** ($0\% - 100\%$), **Deterministic Status**, and **Cryptographic Receipts** are returned.

---

## Quick Start

### 1. Installation

```bash
git clone https://github.com/khurramcr7/zeroH-MCP.git
cd zeroH-MCP
pip install -e .
```

*(Optional)* Install `sympy` for extended symbolic algebra support:
```bash
pip install -e ".[symbolic]"
```

### 2. Configure in Claude Desktop / Cursor / Antigravity IDE

Add the following to your MCP configuration file (`claude_desktop_config.json`, `.cursor/mcp.json`, or Antigravity MCP settings):

```json
{
  "mcpServers": {
    "zeroh-mcp": {
      "command": "python",
      "args": ["-m", "zeroh_mcp.server"],
      "env": {
        "ZEROH_API_URL": "",
        "ZEROH_API_KEY": ""
      }
    }
  }
}
```

---

## Exposed MCP Tools (9 Deterministic Tools)

| Tool Name | Description |
| :--- | :--- |
| `validate_claim` | Intercepts and validates a factual, mathematical, or scientific claim. Returns `Coherence Index`, `Confidence Score`, and `Deterministic Status`. |
| `verify_step` | Submits a single reasoning or mathematical step (`compute`, `solve`, `reasoning`, `interpretation`) into the SHA-256 session ledger. |
| `session_report` | Seals a multi-step reasoning session (`FULLY_PROVEN` only if every active step is proven) and returns the SHA-256 Merkle head hash. |
| `compute` | Computes the exact rational fraction (`numerator/denominator`) and decimal value of an expression with zero floating-point drift. |
| `solve_equation` | Solves algebraic equations and verifies all solutions by exact substitution. |
| `intercept_token` | Queries the remote Sovereign Enclave ledger for a canonical token/root tensor (requires `ZEROH_API_URL`). |
| `zk_verify_receipt` | Generates a SHA-256 cryptographic commitment receipt over a verified claim (or requests an R1CS proof from the Sovereign Enclave). |
| `epistemic_consensus` | Evaluates multi-agent proposals on the 4-tier BFT epistemic lattice (`QATI`, `ZANNI_GHALIB`, `SHAKK`, `WAHM`). |
| `enclave_status` | Reports server health, active execution tier, and `SOVEREIGN_VAULTED_SAFE` IP protection status. |

---

## Python SDK & CLI Usage

### CLI (`zeroh-cli`)

```bash
# Validate a claim from the terminal
python -m zeroh_mcp.cli "In exact arithmetic, 144 / 12 = 12"

# Output raw JSON receipt
python -m zeroh_mcp.cli --json "12 * 12 = 145"

# Check Sovereign Enclave & IP protection status
python -m zeroh_mcp.cli --status
```

### Python SDK (`ZeroHClient`)

```python
from zeroh_mcp import ZeroHClient

client = ZeroHClient()

# 1. Intercept calculation hallucinations
receipt = client.validate("The square of 15 is 15 * 15 = 225.")
print(receipt["deterministic_status"], receipt["confidence_score"])
# -> VERIFIED_COMPUTED_PASS 100.0%

# 2. Step-by-step cryptographic proof ledger
client.verify_step("session_1", {"kind": "compute", "expr": "3 * 19", "value": "57"})
client.verify_step("session_1", {"kind": "solve", "equation": "x**2 - 9 = 0", "claimed": {"x": 3}})
seal = client.session_report("session_1")
print(seal["seal"], seal["merkle_head_hash"])
# -> FULLY_PROVEN <64-char sha256>
```

---

## Security & Zero-Leakage Audit

Run the automated IP & Formula Non-Exposure Audit and test suite at any time:

```bash
python scripts/security_audit_no_leaks.py
pytest -v
```

See [`SECURITY_AND_IP_BOUNDARY.md`](./SECURITY_AND_IP_BOUNDARY.md) for full details on how proprietary formulas remain 100% isolated inside the Sovereign Enclave.
