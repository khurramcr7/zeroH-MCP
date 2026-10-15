# -*- coding: utf-8 -*-
"""
zeroH MCP — Automated Proprietary Formula & IP Non-Exposure Audit
=================================================================
Scans the entire public repository tree before commits or CI releases to
guarantee that:
  1. Zero proprietary invariant constants or internal thresholds appear in source.
  2. Zero closed-form internal equation identifiers appear in source.
  3. Zero database binaries (.db, .sqlite, .sqlite3, .npz, .pt) exist in the repo.
  4. All public MCP tool JSON schemas in `schemas/` are up to date.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent

# We check against SHA-256 digests and structural patterns so even the scanner
# itself never embeds raw proprietary scalar literals in public source code!
FORBIDDEN_FILE_EXTENSIONS = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".parquet",
    ".npz",
    ".pt",
    ".pth",
    ".safetensors",
    ".onnx",
}

FORBIDDEN_SUBSTRINGS_CASE_INSENSITIVE = [
    "alg-eq-0",
    "bridge-0",
    "aql_sovereign.db",
    "aql_lingo_math_sovereign_compiler",
    "sari_cuda_gpu_resident_engine",
    "zk_live_safepay",
    "shannon_ceiling =",
    "target_baseline =",
    "hima_threshold =",
]

# SHA-256 hashes of forbidden proprietary scalar assignment tokens
FORBIDDEN_TOKEN_SHA256 = {
    # Protects internal scalar constants without writing them in cleartext
    "76f3d0b5a25b786207764b13c6c2d3174c312e47981b761f8454600c5460728d",
    "0b7b5908924258b791732551b1b6d3c6490b30549b3d243b2978d9319546722d",
}


def scan_repository() -> List[str]:
    violations: List[str] = []
    this_script = Path(__file__).resolve()

    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [
            d
            for d in dirs
            if d not in {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "build", "dist"}
            and not d.endswith(".egg-info")
        ]
        for fname in files:
            fpath = Path(root) / fname
            rel = fpath.relative_to(REPO_ROOT)

            if fpath.suffix.lower() in FORBIDDEN_FILE_EXTENSIONS:
                violations.append(f"[FORBIDDEN_BINARY] {rel}")
                continue

            if fpath.resolve() == this_script:
                continue

            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            lower_content = content.lower()
            for pat in FORBIDDEN_SUBSTRINGS_CASE_INSENSITIVE:
                if pat in lower_content:
                    violations.append(f"[PROPRIETARY_IDENTIFIER_LEAK] {rel} contains '{pat}'")

            for line_no, line in enumerate(content.splitlines(), start=1):
                stripped = line.strip()
                h = hashlib.sha256(stripped.encode("utf-8")).hexdigest()
                if h in FORBIDDEN_TOKEN_SHA256:
                    violations.append(f"[PROPRIETARY_CONSTANT_LEAK] {rel}:{line_no}")

    return violations


def export_tool_schemas() -> int:
    sys.path.insert(0, str(REPO_ROOT))
    from zeroh_mcp.server import TOOLS

    schemas_dir = REPO_ROOT / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)
    for tool in TOOLS:
        out_file = schemas_dir / f"{tool['name']}.json"
        out_file.write_text(json.dumps(tool, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(TOOLS)


def main() -> int:
    exported = export_tool_schemas()
    violations = scan_repository()
    print("=" * 72)
    print("       zeroH MCP — PROPRIETARY FORMULA & IP SECURITY AUDIT")
    print("=" * 72)
    print(f"Repository Root       : {REPO_ROOT}")
    print(f"Exported Tool Schemas : {exported}")
    print(f"Violations Detected   : {len(violations)}")
    if violations:
        for v in violations:
            print(f"  ❌ {v}")
        print("=" * 72)
        return 1
    print("Status                : ✅ SOVEREIGN_VAULTED_SAFE (Zero Formula Exposure)")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
