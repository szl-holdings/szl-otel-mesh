# uds-mesh

> Unified Data System — cross-component span schemas and governance receipts for OTEL-style observability, grounded in Doctrine v6 graph topology.

[![CI](https://github.com/szl-holdings/uds-mesh/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/ci.yml)
[![CodeQL](https://github.com/szl-holdings/uds-mesh/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/codeql.yml)
[![DOI v18.0](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20434276-blue?style=flat-square&logo=doi&logoColor=white)](https://doi.org/10.5281/zenodo.20434276)
[![Concept DOI](https://img.shields.io/badge/concept%20DOI-10.5281%2Fzenodo.19944926-805AD5?style=flat-square&logo=doi&logoColor=white)](https://doi.org/10.5281/zenodo.19944926)
[![License](https://img.shields.io/badge/license-Apache%202.0-2DA44E?style=flat-square)](./LICENSE)
[![Doctrine v6](https://img.shields.io/badge/doctrine-v6-01696F?style=flat-square)](https://github.com/szl-holdings/ouroboros-thesis)

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
