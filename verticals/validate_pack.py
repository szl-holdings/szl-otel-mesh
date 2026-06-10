#!/usr/bin/env python3
"""validate_pack.py — offline validator for SZL vertical readiness packs.

A vertical readiness pack adapts a third-party "challenge schema" to one SZL organ:
    challenge input -> SZL decision request -> Lambda-gated decision -> DSSE receipt
    -> challenge output.

This validator checks a pack WITHOUT a cluster. It is dependency-light (stdlib +
PyYAML, both already in the repo's test env) and is exercised by
tests/test_vertical_packs.py so every pack stays honest in CI.

What it checks (per pack dir under verticals/, excluding _template metadata-only):
  1. Required files exist and parse (pack.yaml, adapter.yaml, sample-request.json,
     sample-response.json, uds-package.yaml, README.md).
  2. pack.yaml names a real organ and a sane Lambda floor in [0,1].
  3. sample-request.json conforms to the canonical decision-request envelope.
  4. sample-response.json conforms to the canonical decision envelope.
  5. Lambda discipline: lambda_value in [0,1]; governance_drift is consistent with
     the pack's lambda_floor; safety organs (sentra) never PERMIT on drift.
  6. Receipt honesty: the receipt block is present, receipt_hash is 64-hex, and the
     signature is EITHER a base64 string OR the explicit UNSIGNED sentinel — never
     an obviously fabricated placeholder.

Usage:
    python3 verticals/validate_pack.py verticals/<pack>        # one pack
    python3 verticals/validate_pack.py --all                   # every pack
    python3 verticals/validate_pack.py                         # every pack (default)

Exit code 0 = all validated packs pass; 1 = at least one failed.

SPDX-License-Identifier: Apache-2.0
Author: Lutar, Stephen P. — SZL Holdings · Doctrine v11 (Lambda = Conjecture 1).
"""
from __future__ import annotations

import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("PyYAML required: pip install pyyaml\n")
    raise

VERTICALS_DIR = os.path.dirname(os.path.abspath(__file__))

ORGANS = ("a11oy", "sentra", "amaru", "rosie", "killinchu")
VERDICTS = ("PERMIT", "DENY", "DEFER")
FAIL_CLOSED_ORGANS = ("sentra",)  # must never PERMIT under governance drift
DEFAULT_LAMBDA_FLOOR = 0.10
UNSIGNED_SENTINEL = "UNSIGNED-NO-KEY-CONFIGURED"
RECEIPT_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
# Placeholder signatures a pack must NOT ship (would imply a fabricated sig).
FORBIDDEN_SIG_TOKENS = ("TODO", "FIXME", "FAKE", "PLACEHOLDER", "XXXXXX", "changeme")

REQUIRED_FILES = (
    "pack.yaml",
    "adapter.yaml",
    "sample-request.json",
    "sample-response.json",
    "uds-package.yaml",
    "README.md",
)


class PackError(Exception):
    pass


def _load_yaml(path: str) -> dict:
    with open(path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise PackError(f"{os.path.basename(path)} did not parse to a mapping")
    return data


def _load_yaml_all(path: str) -> list[dict]:
    """Load a multi-document YAML file (e.g. Namespace + Deployment + Package CR)."""
    with open(path) as f:
        docs = [d for d in yaml.safe_load_all(f) if d is not None]
    if not docs:
        raise PackError(f"{os.path.basename(path)} parsed to no documents")
    for d in docs:
        if not isinstance(d, dict):
            raise PackError(f"{os.path.basename(path)} has a non-mapping document")
    return docs


def _load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _check_required(obj: dict, required: list[str], where: str) -> list[str]:
    missing = [k for k in required if k not in obj]
    return [f"{where}: missing required field '{k}'" for k in missing]


def validate_decision_request(req: dict) -> list[str]:
    errs: list[str] = []
    errs += _check_required(req, ["request_id", "vertical", "organ", "subject", "ts"],
                            "sample-request")
    if req.get("organ") and req["organ"] not in ORGANS:
        errs.append(f"sample-request: organ '{req['organ']}' not in {ORGANS}")
    subj = req.get("subject")
    if not isinstance(subj, dict) or not subj:
        errs.append("sample-request: 'subject' must be a non-empty object")
    if "context" in req and not isinstance(req["context"], dict):
        errs.append("sample-request: 'context' must be an object when present")
    return errs


def validate_decision(resp: dict, lambda_floor: float, organ: str) -> list[str]:
    errs: list[str] = []
    errs += _check_required(
        resp, ["request_id", "verdict", "lambda_value", "governance_drift", "receipt"],
        "sample-response")
    verdict = resp.get("verdict")
    if verdict is not None and verdict not in VERDICTS:
        errs.append(f"sample-response: verdict '{verdict}' not in {VERDICTS}")

    lam = resp.get("lambda_value")
    if not isinstance(lam, (int, float)):
        errs.append("sample-response: lambda_value must be a number")
    else:
        if not (0.0 <= lam <= 1.0):
            errs.append(f"sample-response: lambda_value {lam} outside [0,1] "
                        "(Lambda = Conjecture 1, in-range required)")
        drift = resp.get("governance_drift")
        expect_drift = (lam < lambda_floor) or (lam > 1.0)
        if isinstance(drift, bool) and drift != expect_drift:
            errs.append(
                f"sample-response: governance_drift={drift} inconsistent with "
                f"lambda_value={lam} and lambda_floor={lambda_floor} "
                f"(expected {expect_drift})")
        # Fail-closed organs must not PERMIT while drifting.
        if organ in FAIL_CLOSED_ORGANS and expect_drift and verdict == "PERMIT":
            errs.append(
                f"sample-response: fail-closed organ '{organ}' must not PERMIT "
                "under governance drift")

    errs += _validate_receipt(resp.get("receipt"))
    return errs


def _validate_receipt(receipt) -> list[str]:
    errs: list[str] = []
    if not isinstance(receipt, dict):
        return ["sample-response: 'receipt' must be an object"]
    errs += _check_required(receipt, ["receipt_hash", "dsse_payload_type", "signature"],
                            "sample-response.receipt")
    h = receipt.get("receipt_hash", "")
    if not RECEIPT_HASH_RE.match(str(h)):
        errs.append("sample-response.receipt: receipt_hash must be 64 lowercase hex chars")
    sig = receipt.get("signature", "")
    if not isinstance(sig, str) or not sig:
        errs.append("sample-response.receipt: signature must be a non-empty string")
    elif sig != UNSIGNED_SENTINEL:
        # A present signature must look like base64 and must not be a placeholder.
        upper = sig.upper()
        if any(tok.upper() in upper for tok in FORBIDDEN_SIG_TOKENS):
            errs.append(
                "sample-response.receipt: signature looks like a fabricated placeholder; "
                f"use a real signature or the '{UNSIGNED_SENTINEL}' sentinel")
        if not re.match(r"^[A-Za-z0-9+/=]+$", sig):
            errs.append("sample-response.receipt: signature is neither base64 nor the "
                        f"'{UNSIGNED_SENTINEL}' sentinel")
    return errs


def validate_pack(pack_dir: str) -> list[str]:
    """Return a list of error strings; empty list means the pack is valid."""
    name = os.path.basename(pack_dir.rstrip("/"))
    errs: list[str] = []

    for fname in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(pack_dir, fname)):
            errs.append(f"[{name}] missing required file: {fname}")
    if errs:
        return errs  # cannot proceed without the files

    try:
        pack = _load_yaml(os.path.join(pack_dir, "pack.yaml"))
        _load_yaml(os.path.join(pack_dir, "adapter.yaml"))
        req = _load_json(os.path.join(pack_dir, "sample-request.json"))
        resp = _load_json(os.path.join(pack_dir, "sample-response.json"))
        wire_docs = _load_yaml_all(os.path.join(pack_dir, "uds-package.yaml"))
    except (PackError, json.JSONDecodeError, yaml.YAMLError) as e:
        return [f"[{name}] parse error: {e}"]

    # The wire must carry a real UDS Package CR (this is what the UDS Operator
    # reconciles). Inter-organ mTLS stays roadmap, so a PeerAuthentication here
    # would be a false claim — flag it.
    kinds = {d.get("kind") for d in wire_docs}
    if "Package" not in kinds:
        errs.append(f"[{name}] uds-package.yaml: missing a UDS 'Package' CR (the wire)")
    if "PeerAuthentication" in kinds or "AuthorizationPolicy" in kinds:
        errs.append(f"[{name}] uds-package.yaml: ships inter-organ mTLS CR "
                    "(PeerAuthentication/AuthorizationPolicy) — that is ROADMAP, not REAL; "
                    "remove it from the pack wire")

    organ = pack.get("organ")
    if organ not in ORGANS:
        errs.append(f"[{name}] pack.yaml: organ '{organ}' not in {ORGANS}")
    lambda_floor = pack.get("lambda_floor", DEFAULT_LAMBDA_FLOOR)
    if not isinstance(lambda_floor, (int, float)) or not (0.0 <= lambda_floor <= 1.0):
        errs.append(f"[{name}] pack.yaml: lambda_floor must be a number in [0,1]")
        lambda_floor = DEFAULT_LAMBDA_FLOOR

    # The request must target the organ the pack declares.
    if req.get("organ") and organ and req["organ"] != organ:
        errs.append(f"[{name}] sample-request.organ '{req.get('organ')}' "
                    f"!= pack.yaml organ '{organ}'")
    # request_id must round-trip to the response.
    if req.get("request_id") and resp.get("request_id") and \
            req["request_id"] != resp["request_id"]:
        errs.append(f"[{name}] sample-response.request_id does not echo "
                    "sample-request.request_id")

    errs += [f"[{name}] {e}" for e in validate_decision_request(req)]
    errs += [f"[{name}] {e}" for e in validate_decision(resp, float(lambda_floor),
                                                         organ or "")]
    return errs


def discover_packs() -> list[str]:
    out = []
    for entry in sorted(os.listdir(VERTICALS_DIR)):
        full = os.path.join(VERTICALS_DIR, entry)
        if not os.path.isdir(full):
            continue
        if entry in ("schemas", "__pycache__", "_template"):
            continue
        out.append(full)
    return out


def main(argv: list[str]) -> int:
    args = [a for a in argv if a != "--all"]
    if args:
        packs = [os.path.abspath(a) for a in args]
    else:
        packs = discover_packs()

    if not packs:
        print("no packs found under verticals/")
        return 0

    total_errs = 0
    for pack_dir in packs:
        name = os.path.basename(pack_dir.rstrip("/"))
        errs = validate_pack(pack_dir)
        if errs:
            total_errs += len(errs)
            print(f"FAIL: {name} ({len(errs)} issue(s))")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"PASS: {name}")

    print(f"\n=== {len(packs)} pack(s) checked, {total_errs} issue(s) ===")
    return 1 if total_errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
