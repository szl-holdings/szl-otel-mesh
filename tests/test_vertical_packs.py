"""
tests/test_vertical_packs.py — vertical readiness pack tests

Exercises verticals/validate_pack.py against every shipped pack so each pack
stays honest in CI: envelopes conform to verticals/schemas/*.json, the Λ-gate +
drift logic is consistent, fail-closed organs never PERMIT under drift, and the
receipt block is present + honest (a real base64 signature OR the explicit
UNSIGNED-NO-KEY-CONFIGURED sentinel — never a fabricated placeholder).

This test lives under tests/ (not verticals/) so the tests.yml path filter
triggers it in CI.

Run: pytest tests/test_vertical_packs.py -v

SPDX-License-Identifier: Apache-2.0
© 2026 Lutar, Stephen P. — SZL Holdings · Doctrine v11 (Λ = Conjecture 1).
"""
import importlib.util
import os

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
VERTICALS_DIR = os.path.join(REPO_ROOT, "verticals")
VALIDATOR_PATH = os.path.join(VERTICALS_DIR, "validate_pack.py")

# Packs we expect to ship and that MUST validate clean.
EXPECTED_PACKS = ("counter-uas", "vendor-screening-889", "intel-triage")


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_pack", VALIDATOR_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vp = _load_validator()


def _pack_dir(name):
    return os.path.join(VERTICALS_DIR, name)


def test_validator_exists():
    assert os.path.isfile(VALIDATOR_PATH)


def test_schemas_exist():
    for s in ("decision-request.schema.json", "decision.schema.json"):
        assert os.path.isfile(os.path.join(VERTICALS_DIR, "schemas", s)), s


def test_expected_packs_present():
    discovered = {os.path.basename(p) for p in vp.discover_packs()}
    for name in EXPECTED_PACKS:
        assert name in discovered, f"expected pack '{name}' not discovered"


def test_template_excluded_from_discovery():
    discovered = {os.path.basename(p) for p in vp.discover_packs()}
    assert "_template" not in discovered
    assert "schemas" not in discovered


@pytest.mark.parametrize("name", EXPECTED_PACKS)
def test_pack_validates_clean(name):
    errs = vp.validate_pack(_pack_dir(name))
    assert errs == [], f"{name} failed validation:\n" + "\n".join(errs)


def test_all_discovered_packs_validate_clean():
    failures = {}
    for pack_dir in vp.discover_packs():
        errs = vp.validate_pack(pack_dir)
        if errs:
            failures[os.path.basename(pack_dir)] = errs
    assert not failures, f"packs failed validation: {failures}"


# ─── Honesty invariants the validator must enforce (negative tests) ──────────

def _good_response():
    return {
        "request_id": "x",
        "verdict": "DENY",
        "lambda_value": 0.5,
        "governance_drift": False,
        "receipt": {
            "receipt_hash": "a" * 64,
            "dsse_payload_type": "application/vnd.in-toto+json",
            "signature": vp.UNSIGNED_SENTINEL,
            "key_id": None,
        },
    }


def test_fabricated_signature_rejected():
    resp = _good_response()
    resp["receipt"]["signature"] = "PLACEHOLDER-sig"
    errs = vp.validate_decision(resp, 0.10, "sentra")
    assert any("fabricated placeholder" in e for e in errs)


def test_unsigned_sentinel_accepted():
    resp = _good_response()
    errs = vp.validate_decision(resp, 0.10, "sentra")
    assert errs == [], errs


def test_real_base64_signature_accepted():
    resp = _good_response()
    resp["receipt"]["signature"] = "TUVRVUFCQ0RFRkc="  # base64, not a placeholder
    errs = vp.validate_decision(resp, 0.10, "sentra")
    assert errs == [], errs


def test_lambda_out_of_range_rejected():
    resp = _good_response()
    resp["lambda_value"] = 1.5
    errs = vp.validate_decision(resp, 0.10, "amaru")
    assert any("outside [0,1]" in e for e in errs)


def test_drift_inconsistent_rejected():
    resp = _good_response()
    resp["lambda_value"] = 0.05   # below floor → drift should be True
    resp["governance_drift"] = False
    errs = vp.validate_decision(resp, 0.10, "amaru")
    assert any("governance_drift" in e for e in errs)


def test_fail_closed_organ_cannot_permit_under_drift():
    resp = _good_response()
    resp["lambda_value"] = 0.05   # drift
    resp["governance_drift"] = True
    resp["verdict"] = "PERMIT"
    errs = vp.validate_decision(resp, 0.10, "sentra")
    assert any("fail-closed organ" in e for e in errs)


def test_bad_receipt_hash_rejected():
    resp = _good_response()
    resp["receipt"]["receipt_hash"] = "not-hex"
    errs = vp.validate_decision(resp, 0.10, "sentra")
    assert any("receipt_hash" in e for e in errs)
