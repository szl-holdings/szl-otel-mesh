<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- © 2026 Lutar, Stephen P. — SZL Holdings · ORCID 0009-0001-0110-4173 -->

# vendor-screening-889 — deny-by-default Section-889 screen (sentra)

**Warhacker track:** Tychee (reusable airgap deployment stacks — supply chain).
The challenge: screen a proposed vendor/component submission against the FY2019
NDAA **§889(a)(1)(B)** covered-telecommunications list and produce a signed,
auditable verdict. This pack maps that onto **sentra**, the SZL immune organ,
which is **fail-closed** and **deny-by-default**. The §889 list is *exactly five*
named entities — **Huawei, ZTE, Hytera, Hikvision, Dahua** (and their
subsidiaries/affiliates); the pack does not invent a sixth. A submission
(`submission_id`, `vendor_name`, `cage_code`, `components`, `submitted_at`) is
adapted into the canonical decision request; sentra returns `DENY` for a covered
entity (the sample shows Hikvision), with `lambda_value`, `governance_drift`, a
cited `finding`, and a DSSE receipt whose hash mirrors back into the output.

**Real vs roadmap.** REAL today: the sentra image is published and cosign-signed
on GHCR (`uds-v0.2.0`); the per-organ Deployment + UDS `Package` CR reconcile
against the UDS Operator; the screen → Λ-gate → DSSE receipt flow is implemented
(signed when a key is present, else the explicit `UNSIGNED-NO-KEY-CONFIGURED`
sentinel — never fabricated); and sentra's fail-closed invariant is enforced by
the validator (a covered entity can never map to `PERMIT`, and sentra never
PERMITs under governance drift). ROADMAP (NOT shipped): the inter-organ hop to
**a11oy** for receipt-substrate cross-check runs over Istio STRICT mTLS, which is
offline-validated only (`docs/roadmap/MESH_INTERCONNECT.md`, criteria 1–7).

```bash
python3 verticals/validate_pack.py verticals/vendor-screening-889
kubectl apply -f verticals/vendor-screening-889/uds-package.yaml
```

---

Doctrine v11 — Λ = Conjecture 1 (never a theorem) · SLSA L1 honest · HONESTY OVER CHECKLIST

Signed-off-by: Stephen P. Lutar Jr. <stephenlutar2@gmail.com>
