# Security & Proprietary IP Boundary Specification (`zeroH-MCP`)

## 1. Zero-Exposure Architectural Guarantee

`zeroH-MCP` is engineered using a strict **Dual-Tier Split-Enclave Architecture** so that AI agents, IDEs (Claude Desktop, Cursor, Antigravity IDE, Windsurf), and enterprise pipelines can integrate deterministic hallucination interception via the **Model Context Protocol (MCP)** while **zero proprietary formulas, internal invariant constants, or private ledger databases are ever exposed in public source code**.

```
+-----------------------------------------------------------------------+
|                    PUBLIC REPOSITORY (zeroH-MCP)                      |
|  - Model Context Protocol (MCP) JSON-RPC 2.0 Stdio & HTTP Server      |
|  - Open-Boundary Exact AST Fraction Arithmetic & Algebraic Verifier   |
|  - SHA-256 Merkle Step-Ledger (`verify_step`, `session_report`)       |
|  - Public Receipt Signature & BFT Quorum Aggregator                   |
|  - Sovereign Enclave HTTPS / Private Bridge Client (`enclave_bridge`) |
+-----------------------------------+-----------------------------------+
                                    |
                     HTTPS API (`ZEROH_API_URL`) or
                     Air-Gapped Local Enclave Plugin
                                    v
+-----------------------------------------------------------------------+
|             PROPRIETARY SOVEREIGN ENCLAVE (NON-EXPOSED)               |
|  - Closed-Form Invariant Baselines & Boundary Thresholds (VAULTED)    |
|  - 7-Equation Lingo-Math Compiler & Tensor Operators (VAULTED)        |
|  - Canonical Sovereign SQLite & Matrix Ledgers (VAULTED)              |
|  - Returns ONLY: Coherence Index [0.0-1.0], Confidence %, Verdict,    |
|    and Cryptographic Commitment Receipt (`zkAQL-...`)                 |
+-----------------------------------------------------------------------+
```

## 2. What Is Included in This Public Repository

1. **Standard MCP Protocol Transport (`zeroh_mcp/server.py`)**:
   - Full JSON-RPC 2.0 `stdio` and `http` server supporting `initialize`, `tools/list`, `tools/call`, and `ping`.
2. **Open-Boundary Deterministic Verification (`zeroh_mcp/public_verifier.py`)**:
   - **Exact Rational Arithmetic (`compute`, `validate_claim`)**: Uses Python's abstract syntax tree (`ast`) and exact `fractions.Fraction` arithmetic to recompute numeric assertions and intercept LLM calculation hallucinations without floating-point drift.
   - **Algebraic Substitution Verification (`solve_equation`, `verify_step`)**: Verifies claimed solutions to algebraic equations by exact symbolic/rational substitution.
   - **SHA-256 Step-Ledger Sealing (`verify_step`, `session_report`)**: Maintains a tamper-evident cryptographic hash chain across multi-step reasoning turns. A session receives the `FULLY_PROVEN` seal if and only if every step in the chain is verified.
   - **Byzantine Epistemic Quorum Interface (`epistemic_consensus`, `zk_verify_receipt`)**: Evaluates multi-agent proposals across the 4-tier epistemic lattice (`QATI`, `ZANNI_GHALIB`, `SHAKK`, `WAHM`) with automatic hallucination (`WAHM`) veto.
3. **Sovereign Enclave Bridge (`zeroh_mcp/enclave_bridge.py`)**:
   - Automatically routes requests to a remote Sovereign Enclave Gateway when `ZEROH_API_URL` and `ZEROH_API_KEY` are configured, or to a locally installed private enclave binary when present on an authorized workstation.

## 3. What Is Strictly Excluded (Proprietary & Vaulted)

- **No Internal Invariant Constants**: All proprietary baseline scalars, harmonic thresholds, and boundary ceilings are strictly excluded from this repository.
- **No Closed-Form Linguistic-Mathematical Equations**: No proprietary compiler equations, root-manifold matrices, or private operator weights are present in this codebase.
- **No Raw Ledger Databases**: No `.db`, `.sqlite`, or canonical corpus dumps are stored in git history.

## 4. Automated Pre-Commit & CI IP Leakage Audit

Every commit and pull request is verified by `scripts/security_audit_no_leaks.py`, which scans the entire repository tree to guarantee:
- Zero forbidden constant literals or internal equation identifiers.
- Zero database binaries or model weight artifacts.
- Zero hardcoded API keys or secrets.
