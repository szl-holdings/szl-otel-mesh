<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- © 2026 Lutar, Stephen P. — SZL Holdings · ORCID 0009-0001-0110-4173 -->

# Vertical Readiness Packs — adapt the SZL mesh to a new schema in <30 min

**Canonical home:** `szl-holdings/uds-mesh` (ADR-0001).
**Doctrine:** v11 LOCKED — 749/14/163 @ `c7c0ba17` · Λ = **Conjecture 1** (never a theorem) · SLSA L1 honest · **HONESTY OVER CHECKLIST**.

A **vertical readiness pack** is a thin, declarative adapter that lets one SZL organ
answer a third-party "challenge schema" — the kind a Warhacker vertical/track hands a
team — *without writing new organ code*. The pack maps the challenge's input schema to a
canonical **SZL decision request**, names which organ evaluates it, applies the **Λ-gate**,
and binds the verdict into a **DSSE receipt** whose hash is mirrored back into the
challenge's output schema.

The point is speed at the booth: when a vertical says *"here is our schema, can you test
it?"*, an operator copies `_template/`, fills four files, runs the validator, and demos.

---

## 1. What a pack is (and is NOT)

A pack is **four declarative files + a sample fixture** that sit on top of the *already
deployed* organ. It is NOT new application code, NOT a new container image, NOT a new
chart. The organ images (`a11oy`, `sentra`, `amaru`, `rosie`, `killinchu`) ship in
`szl-mesh:v0.4.0` and are unchanged. A pack only describes **how to feed them a new
schema and read the receipt back out**.

```
            challenge input schema
                     │  (1) adapter mapping  ── adapter.yaml
                     ▼
        SZL decision request  (canonical envelope, schemas/decision-request.schema.json)
                     │  (2) organ + Λ-gate   ── pack.yaml  (organ, lambda_floor)
                     ▼
        Λ-gated decision  {verdict, lambda_value, governance_drift}
                     │  (3) DSSE receipt      ── pinn_dsse.py / formula_receipts.py
                     ▼
        signed receipt  {receipt_hash, signature|UNSIGNED, dsse_payload_type}
                     │  (4) output mapping    ── adapter.yaml (response section)
                     ▼
            challenge output schema  (+ szl.receipt.* fields)
```

---

## 2. Files in a pack

Copy `_template/` to `verticals/<your-vertical>/` and edit:

| File | Purpose | Required |
|------|---------|----------|
| `pack.yaml` | Pack manifest: which organ, Λ-floor, span name, GHCR image, namespace, real-vs-roadmap flags. | ✅ |
| `adapter.yaml` | Field-by-field mapping: `input_schema → decision_request` and `decision → output_schema`. | ✅ |
| `sample-request.json` | One concrete request in the **challenge's** input schema. | ✅ |
| `sample-response.json` | The expected output **including a signed receipt block** (`szl.receipt.*`). | ✅ |
| `uds-package.yaml` | The UDS `Package` CR + Deployment wiring used to deploy the organ (the "wire"). | ✅ |
| `README.md` | Two-paragraph human brief: which Warhacker track, why this organ, what's real. | ✅ |

The **canonical decision-request / decision / receipt envelopes** are shared and live in
`verticals/schemas/`. Every pack maps *into* and *out of* those — that is what makes a new
pack a 30-minute job instead of a redesign.

---

## 3. The canonical SZL decision envelope

Defined once in `verticals/schemas/decision-request.schema.json` and
`verticals/schemas/decision.schema.json`. Every pack speaks this dialect.

**Decision request** (what the organ evaluates):

```json
{
  "request_id": "string (caller-supplied id)",
  "vertical": "string (pack name, e.g. counter-uas)",
  "organ": "a11oy | sentra | amaru | rosie | killinchu",
  "subject": { "...": "the thing being decided about — vertical-specific" },
  "context": { "...": "optional ROE / policy / evidence the organ needs" },
  "ts": "RFC3339 UTC"
}
```

**Decision** (Λ-gated verdict the organ returns):

```json
{
  "request_id": "string (echoed)",
  "verdict": "PERMIT | DENY | DEFER",
  "lambda_value": 0.0,
  "governance_drift": false,
  "rationale": "string (cited where the organ supports citation)",
  "receipt": {
    "receipt_hash": "sha256 hex (64)",
    "dsse_payload_type": "application/vnd.in-toto+json",
    "signature": "base64 | UNSIGNED-NO-KEY-CONFIGURED",
    "key_id": "string | null"
  }
}
```

### Λ-gate discipline (ABSOLUTE)

- `lambda_value ∈ [0,1]` is **Conjecture 1**, never a theorem. No pack may describe Λ as
  proven.
- `governance_drift = true` iff `lambda_value < lambda_floor` (default floor `0.10`,
  matching `mesh.sdk.mesh.LAMBDA_FLOOR_MESH`) or `lambda_value > 1.0`.
- The verdict mapping is **fail-closed for safety organs**: when the organ cannot
  positively confirm a PERMIT, it returns DENY (sentra) or DEFER (rosie/amaru). A pack
  must not invert this.

### Receipt honesty (ABSOLUTE)

- `signature` is a **real** DSSE signature **only when a signing key is present** (Ed25519
  secret or `SZL_COSIGN_PRIVATE_PEM` / HMAC dev key in CI). When no key is configured the
  pack emits the explicit sentinel `UNSIGNED-NO-KEY-CONFIGURED` — **never a fabricated
  signature.** This mirrors `pinn_dsse` and the `szl-receipt-on-deploy.ts` Pepr policy.
- `receipt_hash` is integrity-bound regardless of signing: it is the SHA-256 over the
  canonical PAE payload and verifies once a key is supplied.

---

## 4. Instantiate a new vertical in <30 minutes

Assumes `szl-mesh:v0.4.0` is already deployed into a UDS Core cluster (see
`audit_uds.md` Tower Test Recipe) and `python3` + `pyyaml` are available locally.

```bash
# 0. (2 min) pick the organ that fits the challenge:
#    sentra    → screen/deny something against a policy/denylist (fail-closed)
#    killinchu → evaluate an engagement / edge interdiction (Λ-gate)
#    amaru     → triage / cited reasoning that refuses to fabricate
#    rosie     → human-on-the-loop confirm/authorize with witnesses
#    a11oy     → governance / receipt-substrate decision (source of truth)

# 1. (1 min) copy the template
cp -r verticals/_template verticals/<your-vertical>

# 2. (10 min) fill the four files for the challenge schema:
#    - pack.yaml      : set organ, lambda_floor, span_name, namespace, image
#    - adapter.yaml   : map their input fields → subject/context; decision → their output
#    - sample-request.json / sample-response.json : one real example pair w/ receipt block

# 3. (3 min) validate the pack offline (no cluster needed)
python3 verticals/validate_pack.py verticals/<your-vertical>
#    → checks pack.yaml/adapter.yaml parse, organ is valid, sample request/response
#      conform to the canonical envelopes, Λ floor + drift logic is consistent,
#      and the receipt block is present + honest (no fabricated signature).

# 4. (5 min) deploy the wire (the organ is already running; this applies the Package CR)
#    REAL today: per-organ Deployment + UDS Package CR + DSSE receipt annotation.
#    ROADMAP:    inter-organ Istio mTLS / PeerAuthentication (see §6).
kubectl apply -f verticals/<your-vertical>/uds-package.yaml

# 5. (5 min) drive one request and read the signed receipt back
#    (port-forward the organ; POST sample-request.json; confirm receipt_hash in response)
kubectl port-forward -n <namespace> deploy/<organ-deploy> 8080:8080 &
curl -sf -XPOST localhost:8080/api/<organ>/v1/decision \
  -H 'content-type: application/json' \
  --data @verticals/<your-vertical>/sample-request.json | jq .receipt
```

If step 3 passes and step 5 returns a `receipt_hash`, the pack is demo-ready.

---

## 5. Example packs (mapped to published Warhacker tracks)

| Pack | Warhacker track (published problem) | Organ | What it decides |
|------|-------------------------------------|-------|-----------------|
| [`counter-uas/`](counter-uas/README.md) | **Cannonico** — AI oversight for autonomous drones; **raven tactical** — AI at the edge | `killinchu` | Λ-gated counter-UAS engagement on a hostile track, signed interdiction receipt |
| [`vendor-screening-889/`](vendor-screening-889/README.md) | **Tychee** — reusable airgap deployment stacks (supply chain) | `sentra` | Deny-by-default Section-889 vendor screen (exactly 5 banned vendors), signed verdict |
| [`intel-triage/`](intel-triage/README.md) | **HANGAR2APPS** — commander visibility; **NATO Explainability/Traceability** | `amaru` | Cited intel-triage reasoning that refuses to fabricate, signed rationale receipt |

Each example pack's `README.md` cites its track and states real-vs-roadmap explicitly.

---

## 6. What is REAL vs ROADMAP (read before you demo)

**REAL today (v0.4.0):**

- The **organ images** are published, public, and cosign-signed on GHCR
  (`a11oy`/`sentra`/`amaru`/`rosie`/`killinchu` at `uds-v0.2.0`); the `szl-mesh:v0.4.0`
  bundle bakes them (see `audit_uds.md` §1).
- **Per-organ deploy** via `ZarfPackageConfig` + a UDS `Package` CR (`network.expose`,
  SSO, `monitor`) — these reconcile against the UDS Operator in UDS Core.
- The **decision → Λ-gate → DSSE receipt** flow: the receipt envelope, PAE hashing, and
  signing modes are implemented (`pinn_dsse.py`, `formula_receipts.py`,
  `mesh/sdk/mesh.py`). Receipts are **signed when a key is present, honestly UNSIGNED
  otherwise**.
- The **receipt annotation on Deployments** (`szl.receipt.*`) via the
  `szl-receipt-on-deploy.ts` Pepr policy (deployed from `szl-uds-deployment`, FAIL_OPEN).

**ROADMAP (NOT shipped — do not claim it works):**

- **Inter-organ mesh networking** — Istio STRICT mTLS / `PeerAuthentication` /
  `AuthorizationPolicy` and Kubernetes-DNS service discovery between organs. The manifests
  in `manifests/istio/` are **offline-validated only**; no live Istio control plane runs
  them. Full acceptance criteria are in `docs/roadmap/MESH_INTERCONNECT.md` (1–7). A pack
  therefore demos **one organ end-to-end**, not a cross-organ call chain over the wire.
- **`szl-receipts` in the bundle** — the receipts server is deployed separately, not baked
  into `szl-mesh:v0.4.0` (image/visibility blockers in `audit_uds.md` §7.4).
- **SLSA scope** — bundle + organs are **SLSA L1 honest**; killinchu is L1. No L2/L3 live,
  no Iron Bank / FedRAMP / CMMC.

This boundary is the same one stated in `docs/MESH.md` §4 — the packs do not move it.

---

## 7. Validation in CI

`verticals/validate_pack.py` is exercised by `tests/test_vertical_packs.py` (part of the
repo pytest suite, `tests.yml`). Every pack under `verticals/` (except `_template`) is
loaded, its envelopes checked against `verticals/schemas/*.json`, and its receipt-honesty
invariant asserted. A pack that fabricates a signature or mis-wires the Λ-gate fails CI.

---

*License: Apache-2.0 · © 2026 Lutar, Stephen P. — SZL Holdings*

Doctrine v11 LOCKED — 749/14/163 @ `c7c0ba17` · Λ = Conjecture 1 (never a theorem) · SLSA L1 honest · HONESTY OVER CHECKLIST

Signed-off-by: Stephen P. Lutar Jr. <stephenlutar2@gmail.com>
