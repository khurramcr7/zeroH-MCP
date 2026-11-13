# ONE XI™ & zeroH Public Paid Subscription MCP Suite (`zeroh-mcp` / `onexi-mcp`)

[![Protocol: MCP 2024-11-05](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io)
[![IP Protection: Sovereign Enclave Vaulted](https://img.shields.io/badge/Proprietary_Formulas-Vaulted_%26_Non--Exposed-success.svg)](./SECURITY_AND_IP_BOUNDARY.md)
[![License: MIT Client](https://img.shields.io/badge/License-MIT_Client-green.svg)](./LICENSE)

**ONE XI™ & zeroH MCP** is the official public **Model Context Protocol (MCP)** server and Python SDK for **ONE XI Technologies by Aalimbooks International** (`onexi.tech` | `kutublink.com` | `warith.io` | `islamicheritagepress.com/aalimbooks`).

It equips AI coding assistants, autonomous agents, and IDEs (**Claude Desktop**, **Antigravity IDE**, **Cursor**, **Windsurf**, and custom MCP hosts) with **15 deterministic MCP tools** spanning open-boundary mathematical verification, **ONE XI™ Paid Subscription Cloud MCPs** (Quantum Circuit Compilation, 8-Gate Executable Code & HPC Auditing, KutubLink 121.8M-Word Classical Corpus Concordance, and Aalim AI / Wārith.io Scholarly Verification), and the **Multi-Rail Sovereign Payment Gateway** (`Polar.sh` + `Stripe 3D-Secure`, `Payoneer`, `Meezan Bank Corporate IBAN`, and `Web3 USDT/USDC`).

> **Scope Policy**: Public MCP tools cover **ONE XI Cloud**, **ONE XI Quantum Suite**, **ONE XI 8-Gate HPC Sandbox**, **KutubLink**, and **Aalim Books / Wārith.io**. Bio/clinical tiers are retained **strictly inside the payment gateway (`onexi_payment_gateway`) for settlement only** and are **not exposed as public MCP tools yet**.

---

## Architectural Highlights & IP Boundary

`zeroh-mcp` (`onexi-mcp`) operates across a strict **Dual-Tier Split-Enclave & Paid Subscription Architecture**:

1. **Tier 1 — Public Open-Boundary Verification & Preview Telemetry (Zero-Config Local Mode)**:
   - Works out-of-the-box with zero external dependencies.
   - **Exact Rational Arithmetic (`compute`, `validate_claim`)**: Evaluates numerical expressions via Python `ast` and `fractions.Fraction` to eliminate floating-point drift and catch calculation hallucinations (`12 * 12 = 145` $\rightarrow$ `REJECTED_HALLUCINATION`).
   - **Algebraic Substitution Verification (`solve_equation`, `verify_step`)**: Solves equations and verifies every candidate root by exact substitution.
   - **Tamper-Evident SHA-256 Step Ledger (`verify_step`, `session_report`)**: Tracks step-by-step reasoning chains and issues a `FULLY_PROVEN` cryptographic seal only when every active step in the chain is verified.
   - **8-Gate AST Code Auditing, OpenQASM Resource Estimation, Uthmānī *Tashkīl* / Abjad Auditing & Exact Rational Zakāh / Farāʾiḍ Verification**: Runs locally with deterministic cryptographic receipts.

2. **Tier 2 — Paid Subscription Cloud Enclave (`ONEXI_API_KEY` + `ONEXI_API_URL`)**:
   - When configured with an active **ONE XI™ Paid Subscription Key** (`ONEXI_API_KEY` or `ONEXI_LICENSE_KEY`), the server unlocks full cloud enclave execution across `onexi_quantum_compiler`, `onexi_hpc_code_sandbox`, `onexi_kutublink_turath`, and `onexi_aalim_scholar`.
   - If a paid cloud action is invoked without an active subscription key, the MCP tool automatically returns `SUBSCRIPTION_REQUIRED` along with a **1-click Polar.sh + Stripe 3D-Secure checkout link**, **Payoneer B2B portal**, **Meezan Bank Corporate IBAN**, and **Web3 USDT/USDC settlement coordinates**.
   - All proprietary invariant constants, closed-form equations, compiler passes, and canonical database tensors remain 100% vaulted inside the remote Sovereign Enclave.

---

## Self-Serve Public Subscription Plans (`onexi.tech`)

| Tier ID | Plan Name | Price (USD) | Unlocked Public MCP Capabilities | 1-Click Checkout |
| :--- | :--- | :--- | :--- | :--- |
| `BOOK_15_SINGLE` | Single E-Book License | `$15` | KutubLink Single Classical Edition PDF | [Checkout (`$15`)](https://buy.polar.sh/polar_cl_IsodrKALkvXOZNwTAUe2jXIPirwcKrrUn4fMW2IvZSb) |
| `BOOK_29_DIGITAL` | 20-Volume E-Book Collection | `$29` | KutubLink 20-Volume Classical Bundle | [Checkout (`$29`)](https://buy.polar.sh/polar_cl_OY6kJpTMnbYcVss5frahza2pRh3bo8PkmlbFM42Psvg) |
| `FAST_49_PASS` | **ONE XI Cloud — Pro Pass** | **`$49 / mo`** | Developer API, 8-Gate Code Sandbox & Aalim Scholar Cloud | [Subscribe (`$49/mo`)](https://buy.polar.sh/polar_cl_yiaY2QaaJrj4WuWm1bpQWOIPNDogghaLT2A0o0JczDW) |
| `FAST_99_AUDIT` | Pro Compute Pack | `$99` | High-Throughput Simulation & Quantum Audit Pack | [Checkout (`$99`)](https://buy.polar.sh/polar_cl_Gz9p54IMeHEHkhJIbopPTKCX6LtlT3CI9isWR4PruOa) |
| `TURATH_150_SPRINT` | KutubLink OCR & Corpus Credits | `$150` | 121.8M-Word Classical Corpus Search & Manuscript OCR API | [Checkout (`$150`)](https://buy.polar.sh/polar_cl_yHVdCwtXLV6BmKR800Ww2zWs6rD7L9dhDGyPq1XtvVw) |
| `LAB_199_PACK` | **ONE XI Cloud — Team License** | **`$199 / mo`** | Multi-Seat Team SaaS, HPC Cloud Sandbox & API License | [Subscribe (`$199/mo`)](https://buy.polar.sh/polar_cl_2rGWKtRrTpFyrMjKTRwRSv9Cb8F4FZmvW322i16kIwX) |
| `CLINICAL_PILOT_250` | Batch API Compute Credits | `$250` | High-Throughput Batch API Compute Credits | [Checkout (`$250`)](https://buy.polar.sh/polar_cl_AAc3JcysPhTQFTF5r8RvXTwXdeH8eBHzzUxBO4Plnaz) |
| `BOOK_499_WAQF` | **Unlimited Cloud & Institutional Seat** | **`$499 / mo`** | Unlimited ONE XI Cloud + KutubLink Institutional Library Seat | [Subscribe (`$499/mo`)](https://buy.polar.sh/polar_cl_eXsIPJGpi0QnzjA913s581oKVvBz8ooPNUgOa49Ofe8) |
| `TURATH_PILOT_1500` | KutubLink Enterprise Corpus License | `$1,500 / yr` | Annual Full-Corpus Concordance & OpenITI/Shamela API | [Subscribe (`$1,500/yr`)](https://buy.polar.sh/polar_cl_mxNmmpL5zKWLFXrBBzMu7C1CEeM00enlnf0jk27GYzr) |
| `QUANTUM_AUDIT_2500` | ONE XI Quantum Compiler SDK | `$2,500` | Self-Serve Fault-Tolerant Quantum Circuit Compiler SDK | [Checkout (`$2,500`)](https://buy.polar.sh/polar_cl_ZRpW61YKd5LTSuG3q9aRPhWqdiwWiXVnd8cs51JEP28) |
| `CHIRAL_PRO_4950` | ONE XI Enterprise Full-Stack License | `$4,950 / yr` | Annual Enterprise Full-Stack SaaS & SDK License | [Subscribe (`$4,950/yr`)](https://buy.polar.sh/polar_cl_z06WyxPY8fRnaZ3G6dZrEKko3fp9rvq3JtNp91bdBx1) |
| `QUANTUM_SUITE_COMPILER_SEAT_ANNUAL` | ONE XI Quantum Suite Compiler Seat | `$25,000 / yr` | Dedicated Annual Enterprise EDA Quantum Compiler Seat | [Subscribe (`$25,000/yr`)](https://buy.polar.sh/polar_cl_Zz0MHK1CwG3AriaHXdd7Y0atV1Kd3PDgBAWHL2tKoIM) |

---

## Quick Start (Zero-Friction 1-Command Onboarding)

### 1. Instant Install via `uvx`, `pip`, or Smithery

```bash
# Option A: Run directly with uvx (Zero virtual-env setup)
uvx zeroh-mcp

# Option B: Install Python SDK + MCP Server via pip
pip install zeroh-mcp

# Option C: 1-Click Smithery IDE Installer
npx -y @smithery/cli install @khurramcr7/zeroH-MCP --client claude
```

*(For local source development: `git clone https://github.com/khurramcr7/zeroH-MCP.git && cd zeroH-MCP && pip install -e .`)*

### 2. Drop-In Python LLM Guardrail Decorator (`@zeroh_guardrail`)

Wrap any OpenAI, Anthropic, Google Gemini, LangChain, or custom agent function in **3 lines of Python** to intercept arithmetic/algebraic hallucinations and emit tamper-evident SHA-256 session Merkle receipts:

```python
from zeroh_mcp import zeroh_guardrail, ZeroHGuardrail, ZeroHHallucinationError

@zeroh_guardrail(strict=True)
def generate_financial_summary() -> str:
    # Any arithmetic or algebraic hallucination raises ZeroHHallucinationError
    # before reaching downstream users or regulated workflows!
    return "Quarterly allocation check: 1250 * 4 = 5000. Net balance verified."

# Or inspect arbitrary multi-sentence LLM completions programmatically:
guard = ZeroHGuardrail()
audit = guard.inspect_text("Step 1: 12 * 12 = 144. Step 2: 15 + 25 = 40.")
print(audit["overall_status"], audit["session_merkle_head"])
```

### 3. Configure in Claude Desktop / Cursor / Antigravity IDE / Windsurf

Add the following to your MCP configuration file (`claude_desktop_config.json`, `.cursor/mcp.json`, or Antigravity MCP settings):

```json
{
  "mcpServers": {
    "onexi-zeroh-mcp": {
      "command": "uvx",
      "args": ["zeroh-mcp"],
      "env": {
        "ONEXI_API_URL": "https://onexi.tech/api",
        "ONEXI_API_KEY": ""
      }
    }
  }
}
```

---

## Exposed MCP Tools (15 Deterministic Tools)

| Tool Name | Category | Description |
| :--- | :--- | :--- |
| `onexi_subscription_gate` | **ONE XI Paid Subscription** | Verifies `ONEXI_API_KEY` / `ONEXI_LICENSE_KEY`, lists public paid MCP plans (`$15`–`$25,000`), and generates 1-click upgrade checkout links. |
| `onexi_quantum_compiler` | **ONE XI Quantum Suite** | Fault-tolerant quantum circuit resource estimation & cloud compilation (`5.4126x` `invsqrt` T-gate reduction, `-91.34%` 64-bit & `-99.49%` 2048-bit adder Toffoli depth reduction, `-60.17%` QROM Toffoli reduction; Merkle Root `e8c2800b...`). |
| `onexi_hpc_code_sandbox` | **ONE XI Cloud Sandbox** | 8-Gate Python AST complexity, security, and SHA-256 code-seal auditing + paid cloud HPC execution (`$49/mo` / `$199/mo` / `$499/mo`). |
| `onexi_kutublink_turath` | **KutubLink & Aalim Books** | Uthmānī *Tashkīl* & Abjad auditing + paid cloud concordance search across `578` classical works (`121,843,480` vocalized words), `8,598` Shamela volumes & `14,107` OpenITI texts. |
| `onexi_aalim_scholar` | **Aalim AI & Wārith.io** | Exact rational Zakāh ($1/40 = 2.5\%$) and Farāʾiḍ inheritance verification + paid 7-Gate Translation QA (TQA) & Comparative Scholarly Cloud. |
| `onexi_payment_gateway` | **Multi-Rail Payment Gateway** | Manages all 16 Polar.sh + Stripe 3D-Secure checkout links (`$15` to `$120,000` USD, including payment-only Bio settlement tiers), Payoneer, Meezan Corporate IBAN, and Web3 USDT/USDC. |
| `validate_claim` | **zeroH Guardrail** | Intercepts and validates a factual, mathematical, or scientific claim (`Coherence Index`, `Confidence Score`, `Deterministic Status`). |
| `verify_step` | **zeroH Guardrail** | Submits a single reasoning or mathematical step (`compute`, `solve`, `reasoning`, `interpretation`) into the SHA-256 session ledger. |
| `session_report` | **zeroH Guardrail** | Seals a multi-step reasoning session (`FULLY_PROVEN` only if every active step is proven) and returns the SHA-256 Merkle head hash. |
| `compute` | **zeroH Guardrail** | Computes the exact rational fraction (`numerator/denominator`) and decimal value of an expression with zero floating-point drift. |
| `solve_equation` | **zeroH Guardrail** | Solves algebraic equations and verifies all solutions by exact substitution. |
| `intercept_token` | **zeroH Enclave** | Queries the remote Sovereign Enclave ledger for a canonical token/root tensor. |
| `zk_verify_receipt` | **zeroH Enclave** | Generates a SHA-256 cryptographic commitment receipt over a verified claim. |
| `epistemic_consensus` | **zeroH BFT Quorum** | Evaluates multi-agent proposals on the 4-tier BFT epistemic lattice (`QATI`, `ZANNI_GHALIB`, `SHAKK`, `WAHM`). |
| `enclave_status` | **zeroH Enclave** | Reports server health, active execution tier, and `SOVEREIGN_VAULTED_SAFE` IP protection status. |

---

## Security & Zero-Leakage Audit

Run the automated IP & Formula Non-Exposure Audit and test suite at any time:

```bash
python scripts/security_audit_no_leaks.py
pytest -v
```

See [`SECURITY_AND_IP_BOUNDARY.md`](./SECURITY_AND_IP_BOUNDARY.md) for full details on how proprietary formulas remain 100% isolated inside the Sovereign Enclave and how Bio divisions are restricted to payment-only settlement.
