<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- © 2026 Lutar, Stephen P. — SZL Holdings · ORCID 0009-0001-0110-4173 -->

# counter-uas — Λ-gated counter-UAS engagement (killinchu)

**Warhacker track:** Cannonico (AI oversight for autonomous drones) and raven
tactical (AI at the edge). The challenge: given a detected hostile track and an
ROE profile, decide whether to engage — and produce an auditable, signed basis
for that decision. This pack maps that challenge onto **killinchu**, the SZL edge
organ, and binds the verdict into a DSSE interdiction receipt. A counter-UAS
track (`track_id`, `classification`, `range_m`, `roe_profile`, `detected_at`) is
adapted into the canonical SZL decision request; killinchu applies the Λ-gate and
returns `PERMIT | DENY | DEFER` with `lambda_value`, `governance_drift`, a cited
`rationale`, and a receipt whose hash mirrors back into the challenge output.

**Real vs roadmap.** REAL today: the killinchu image is published and
cosign-signed on GHCR (`uds-v0.2.0`); the per-organ Deployment + UDS `Package` CR
reconcile against the UDS Operator; and the engagement → Λ-gate → DSSE receipt
flow is implemented (receipt signed when a key is present, else the explicit
`UNSIGNED-NO-KEY-CONFIGURED` sentinel — never fabricated). ROADMAP (NOT shipped):
the inter-organ hop to **rosie** for human-on-the-loop confirmation runs over
Istio STRICT mTLS, which is offline-validated only (see
`docs/roadmap/MESH_INTERCONNECT.md`, criteria 1–7). This pack therefore demos
**killinchu end-to-end as one organ**, not a killinchu→rosie call chain over the
wire.

```bash
python3 verticals/validate_pack.py verticals/counter-uas
kubectl apply -f verticals/counter-uas/uds-package.yaml
```

---

Doctrine v11 — Λ = Conjecture 1 (never a theorem) · SLSA L1 honest · HONESTY OVER CHECKLIST

Signed-off-by: Stephen P. Lutar Jr. <stephenlutar2@gmail.com>
