<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- © 2026 Lutar, Stephen P. — SZL Holdings · ORCID 0009-0001-0110-4173 -->

# intel-triage — cited reasoning that refuses to fabricate (amaru)

**Warhacker track:** HANGAR2APPS (commander visibility) and the NATO
Explainability & Traceability theme. The challenge: triage raw intel reports
against a question and produce an assessment a commander can *trust and trace* —
one that cites its sources and declines to assert what the evidence does not
support. This pack maps that onto **amaru**, the SZL memory organ. A query
(`query_id`, `question`, `reports[]`, `requested_at`) is adapted into the
canonical decision request; amaru returns an assessment with `lambda_value`
(strength of the cited evidence), `governance_drift`, a `rationale` carrying its
citations inline, and a DSSE receipt. When the evidence is too thin — as in the
sample, where one report confirms only movement and another is an unconfirmed
source — amaru returns **`DEFER`** and says so, rather than fabricating a finding.

**Real vs roadmap.** REAL today: the amaru image is published and cosign-signed
on GHCR (`uds-v0.2.0`); the per-organ Deployment + UDS `Package` CR reconcile
against the UDS Operator; and the cited-triage → Λ-gate → DSSE rationale-receipt
flow is implemented (signed when a key is present, else the explicit
`UNSIGNED-NO-KEY-CONFIGURED` sentinel — never fabricated). The refuse-to-fabricate
behavior shows up here as a low-Λ `DEFER` with explicit citations. ROADMAP (NOT
shipped): the inter-organ hop to **rosie** for human-on-the-loop adjudication runs
over Istio STRICT mTLS, which is offline-validated only
(`docs/roadmap/MESH_INTERCONNECT.md`, criteria 1–7).

```bash
python3 verticals/validate_pack.py verticals/intel-triage
kubectl apply -f verticals/intel-triage/uds-package.yaml
```

---

Doctrine v11 — Λ = Conjecture 1 (never a theorem) · SLSA L1 honest · HONESTY OVER CHECKLIST

Signed-off-by: Stephen P. Lutar Jr. <stephenlutar2@gmail.com>
