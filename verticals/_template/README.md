<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- © 2026 Lutar, Stephen P. — SZL Holdings · ORCID 0009-0001-0110-4173 -->

# `_template` — copy this to start a new vertical readiness pack

This directory is the **scaffold**. It is intentionally excluded from the
offline validator (`validate_pack.py` skips `_template`) and from CI, because it
ships placeholder `<...>` values rather than a real example. To build a real
pack, copy it and replace every placeholder:

```bash
cp -r verticals/_template verticals/<your-vertical>
```

Then fill, in order:

1. **`pack.yaml`** — pick the organ (`sentra` / `killinchu` / `amaru` / `rosie` /
   `a11oy`), set `lambda_floor`, `span_name`, `image`, `namespace`. State
   real-vs-roadmap honestly in the `real:` / `roadmap:` lists.
2. **`adapter.yaml`** — map the challenge's INPUT fields into the canonical
   decision request, and the canonical decision back OUT into the challenge's
   output schema. Mirror the receipt block; never fabricate a signature.
3. **`sample-request.json`** — one concrete request in the challenge's input
   schema, conforming to `verticals/schemas/decision-request.schema.json`.
4. **`sample-response.json`** — the expected Λ-gated decision + receipt block,
   conforming to `verticals/schemas/decision.schema.json`. The `signature` is a
   real base64 DSSE signature **only if a key is present**, else the literal
   `UNSIGNED-NO-KEY-CONFIGURED` sentinel.
5. **`uds-package.yaml`** — the deploy wire: Namespace + Deployment + UDS
   `Package` CR for the one organ. Inter-organ mTLS is **roadmap** — do not add
   `PeerAuthentication` here and claim it runs.
6. **`README.md`** (this file) — replace with a two-paragraph brief: which
   Warhacker track, why this organ, and exactly what is real vs roadmap.

## Validate before you demo

```bash
python3 verticals/validate_pack.py verticals/<your-vertical>
```

A green run means the envelopes parse, the organ is valid, the Λ-gate + drift
logic is consistent, and the receipt is honest. Then apply the wire and drive
one request (see `verticals/README.md` §4).

---

Doctrine v11 — Λ = Conjecture 1 (never a theorem) · SLSA L1 honest · HONESTY OVER CHECKLIST

Signed-off-by: Stephen P. Lutar Jr. <stephenlutar2@gmail.com>
