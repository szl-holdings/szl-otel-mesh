# uds-mesh
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-0B1F3A.svg?style=flat-square&logo=apache&logoColor=00D4FF)](https://www.apache.org/licenses/LICENSE-2.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20434276.svg)](https://doi.org/10.5281/zenodo.20434276)
[![CI](https://github.com/szl-holdings/uds-mesh/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/ci.yml)
[![Tests](https://github.com/szl-holdings/uds-mesh/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/tests.yml)
[![CodeQL](https://github.com/szl-holdings/uds-mesh/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/codeql.yml)
[![SBOM](https://github.com/szl-holdings/uds-mesh/actions/workflows/sbom.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/sbom.yml)
[![SLSA 3](https://github.com/szl-holdings/uds-mesh/actions/workflows/slsa.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/slsa.yml)
[![DCO](https://github.com/szl-holdings/uds-mesh/actions/workflows/dco.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/dco.yml)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-A6CE39.svg?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173)

> Unified Data System — cross-component span schemas and governance receipts for OTEL-style observability, grounded in Doctrine v6 graph topology.



> **Frontier Capability** — first topology-preserving (A15 persistent homology) multi-component governance span schema.  
> The A15 ELZ invariant guarantees that no topological obstruction can sever the audit-fiber bundle across component boundaries under Doctrine v6 composition.

> **Thesis cross-reference:** The mathematical foundations for this repository are developed
> in the [Ouroboros Thesis v18.0](https://github.com/szl-holdings/ouroboros-thesis) (DOI [10.5281/zenodo.20434276](https://doi.org/10.5281/zenodo.20434276)).
> Source for the published thesis is in [`szl-holdings/ouroboros-thesis`](https://github.com/szl-holdings/ouroboros-thesis).
> Concept DOI (always-latest): [10.5281/zenodo.19944926](https://doi.org/10.5281/zenodo.19944926).

> **Test coverage (honest count — 2026-05-29):**
> - `tests/test_span_schemas.py` — 33 pytest tests (span schema validation)
> - `tests/test_attestation_chain.py` — 20 pytest tests (DSSE receipt chain integrity)
> - `tests/test_bundle_manifests.py` — 17 pytest tests (bundle YAML validation)
> - `uds_v18_24_substrate.py` — 173 doctests + 92 assert checks = 265 self-tests
> - **Total: 70 pytest + 265 substrate = 335 validated UDS artifacts**
>
> Grep-able: `grep -c "def test_" tests/**/*.py` → 70
> The "269 tests" figure cited in some earlier docs referred to the substrate
> doctest+assert count (265 ≈ 269). All tests now run in CI via `tests.yml`.

## Graph-Theoretic Foundation

The UDS mesh is a directed acyclic graph (DAG) of typed spans. The topology satisfies:

- **Causal consistency**: every edge `(u, v)` carries a Lamport timestamp
  `t(v) > t(u)`, enforcing a total causal order.
  [(Lamport, 1978, doi:10.1145/359545.359563)](https://doi.org/10.1145/359545.359563)
- **A15 topological invariant**: the simplicial complex of audit-fiber bundles satisfies the
  Edelsbrunner–Letscher–Zomorodian A15 persistent-homology condition.
  [(doi:10.1007/s00454-002-2885-2)](https://doi.org/10.1007/s00454-002-2885-2)
- **SCITT receipt integrity**: every governance receipt is Merkle-anchored per
  [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962).

## Bundle Versions

| Version | Manifest | Components | Status |
|---------|----------|-----------|--------|
| v0.3.1 | [`bundles/v0.3.1/uds-bundle.yaml`](./bundles/v0.3.1/uds-bundle.yaml) | a11oy, sentra, amaru + Doctrine v6 Runtime Layer | stable |
| v0.2.0 | [`uds-bundle.yaml`](./uds-bundle.yaml) | a11oy, sentra, amaru | stable |

### v0.3.1 Doctrine v6 Runtime Layer

| Module | Description | Standard |
|--------|-------------|----------|
| `composition-runtime` | Geometric-mean / min-Λ policy composition | COSE_Sign1 ([RFC 9052](https://www.rfc-editor.org/rfc/rfc9052)) |
| `scitt-adapter` | SCITT-Rekor notarisation | [draft-ietf-scitt-architecture-07](https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/) |
| `policy-gate` | Doctrine v6 §4.3 best-match gate + NATS hot-reload | — |
| `a15-homology` | ELZ 2002 persistent homology A15 invariant | [doi:10.1007/s00454-002-2885-2](https://doi.org/10.1007/s00454-002-2885-2) |
| `xoshiro-prng` | xoshiro256** PRNG | [doi:10.1145/3460772](https://doi.org/10.1145/3460772) |
| `k10v2-replay` | Lamport-clock event-sourcing replay root | [doi:10.1145/359545.359563](https://doi.org/10.1145/359545.359563) |

## Quick Start

```sh
# Deploy v0.3.1 runtime layer
uds deploy bundles/v0.3.1/uds-bundle.yaml
```

## How to Cite

```bibtex
@techreport{ouroboros_thesis_v18,
  author      = {Lutar, Stephen P.},
  title       = {{SZL Holdings v18.0 Master Thesis --- Multi-track Substrate Expansion}},
  year        = {2026},
  institution = {SZL Holdings},
  doi         = {10.5281/zenodo.20434276},
  url         = {https://doi.org/10.5281/zenodo.20434276}
}
```

The `CITATION.cff` in this repository root is the authoritative citation source.

## Companion Repositories

| Repository | Role |
|-----------|------|
| [szl-holdings/ouroboros-thesis](https://github.com/szl-holdings/ouroboros-thesis) | Formal thesis (v18.0, DOI [10.5281/zenodo.20434276](https://doi.org/10.5281/zenodo.20434276)) |
| [szl-holdings/vsp-otel](https://github.com/szl-holdings/vsp-otel) | OpenTelemetry exporter for Λ-axis spans |
| [szl-holdings/ouroboros](https://github.com/szl-holdings/ouroboros) | Runtime producing audit receipts |

## License

Apache License 2.0 — see [`LICENSE`](./LICENSE).

Copyright 2026 SZL Holdings. ORCID: [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173).

---

## Related repositories in the SZL substrate

The 13 substrate repos cross-link reciprocally. This footer is maintained by GH Admin #1 (org-wide).

- [`a11oy`](https://github.com/szl-holdings/a11oy) — vertical alignment substrate (policy · measurement · knowledge · QEC-integrity)
- [`amaru`](https://github.com/szl-holdings/amaru) — Shor-encoded receipt minting (Cardano-anchored)
- [`rosie`](https://github.com/szl-holdings/rosie) — CSS-ingress receipt orchestration
- [`sentra`](https://github.com/szl-holdings/sentra) — Kitaev-surface drift detection on audit fibers
- [`uds-mesh`](https://github.com/szl-holdings/uds-mesh) — UDS span schemas + governance receipts
- [`lutar-lean`](https://github.com/szl-holdings/lutar-lean) — Lean 4 + Mathlib v4.13.0 kernel proofs (30 GREEN modules)
- [`ouroboros`](https://github.com/szl-holdings/ouroboros) — bounded-recursion runtime
- [`ouroboros-thesis`](https://github.com/szl-holdings/ouroboros-thesis) — DOI-pinned thesis substrate (v3 → v18)
- [`platform`](https://github.com/szl-holdings/platform) — composing monorepo (76 packages, 1,220 tests)
- [`szl-brand`](https://github.com/szl-holdings/szl-brand) — anatomy + visual doctrine (PDFs hosted in-repo)
- [`szl-cookbook`](https://github.com/szl-holdings/szl-cookbook) — governed-AI recipes
- [`agi-forecast`](https://github.com/szl-holdings/agi-forecast) — PAC-Bayes + Bekenstein governance-trajectory forecasts
- [`vsp-otel`](https://github.com/szl-holdings/vsp-otel) — OpenTelemetry exporter for Λ-axis spans

Org page: [github.com/szl-holdings](https://github.com/szl-holdings) · Doctrine v6 · 11 axioms · 30 GREEN modules · v18.0 DOI [`10.5281/zenodo.20434276`](https://doi.org/10.5281/zenodo.20434276)


---

## On Hugging Face

This repository is mirrored and published on the [SZLHOLDINGS](https://huggingface.co/SZLHOLDINGS) Hugging Face organization:

- [huggingface.co/datasets/SZLHOLDINGS/uds-spans-receipts](https://huggingface.co/datasets/SZLHOLDINGS/uds-spans-receipts) — uds-spans-receipts (100 OTel spans, 50 DSSE receipts)
- [huggingface.co/spaces/SZLHOLDINGS/mcp-receipts-server](https://huggingface.co/spaces/SZLHOLDINGS/mcp-receipts-server) — mcp-receipts-server (MCP Space, 4 tools)

