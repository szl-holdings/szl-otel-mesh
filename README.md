<div align="center">

# 🌐 uds-mesh

**mesh / nervous**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20434276.svg)](https://doi.org/10.5281/zenodo.20434276) [![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-a6ce39?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173) [![Doctrine](https://img.shields.io/badge/Doctrine-v7-7c5cff?style=flat-square)](https://github.com/szl-holdings/.github/blob/main/DOCTRINE_V7.md) [![SLSA](https://img.shields.io/badge/SLSA-L1_honest-22c55e?style=flat-square)](https://slsa.dev/spec/v1.0/levels)

[Hugging Face](https://huggingface.co/SZLHOLDINGS) · [Demo](https://szlholdings-readme.static.hf.space/) · [GitHub Org](https://github.com/szl-holdings)

`receipts.in ≡ receipts.out`

</div>

---
# uds-mesh — Unified Data System Governance Span Mesh

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-0B1F3A.svg?style=flat-square&logo=apache&logoColor=00D4FF)](https://www.apache.org/licenses/LICENSE-2.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20434276.svg)](https://doi.org/10.5281/zenodo.20434276)
[![CI](https://github.com/szl-holdings/uds-mesh/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/ci.yml)
[![Tests](https://github.com/szl-holdings/uds-mesh/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/tests.yml)
[![CodeQL](https://github.com/szl-holdings/uds-mesh/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/codeql.yml)
[![GHAS Code Security](https://img.shields.io/badge/GHAS-Code_Security-2DA44E.svg?style=flat-square&logo=github)](https://github.com/szl-holdings/uds-mesh/security/code-scanning)
[![Secret Protection](https://img.shields.io/badge/GHAS-Secret_Protection-2DA44E.svg?style=flat-square&logo=github)](https://github.com/szl-holdings/uds-mesh/security/secret-scanning)
[![SBOM](https://github.com/szl-holdings/uds-mesh/actions/workflows/sbom.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/sbom.yml)
[![SLSA L1 (SBOM + DCO)](https://img.shields.io/badge/SLSA-L1_(SBOM_%2B_DCO)-0B1F3A.svg?style=flat-square)](https://slsa.dev/spec/v1.0/levels)
[![DCO](https://github.com/szl-holdings/uds-mesh/actions/workflows/dco.yml/badge.svg?branch=main)](https://github.com/szl-holdings/uds-mesh/actions/workflows/dco.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/szl-holdings/uds-mesh/badge)](https://securityscorecards.dev/viewer/?uri=github.com/szl-holdings/uds-mesh)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-A6CE39.svg?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173)


> **NOTE:** SLSA Level 1 (source + build provenance documented). L2/L3 require Sigstore + isolated builders (roadmap).

> Cross-component span schemas and governance receipts for OTEL-style observability, grounded in Doctrine v7 graph topology with A15 persistent-homology (ELZ) invariant.  
> Doctrine v7 · DOI [10.5281/zenodo.20434276](https://doi.org/10.5281/zenodo.20434276)

**uds-mesh** implements the Unified Data System span schema layer for the SZL Holdings governed AI platform. It emits DSSE-wrapped governance receipts, maintains gRPC/Protobuf span contracts, and guarantees topological continuity of audit fibers across component boundaries through the A15 ELZ invariant (STAGED — topology claim is axiom-structured, pending `lake build` fix in lutar-lean).

---

## On Hugging Face

[SZLHOLDINGS on Hugging Face](https://huggingface.co/SZLHOLDINGS) — 26 Spaces · 29 datasets · 2 models

| Surface | Artifact |
|---------|----------|
| Source mirror | [uds-mesh-source](https://huggingface.co/datasets/SZLHOLDINGS/uds-mesh-source) |

---

## What is real today

| Metric | Count | Verify |
|--------|-------|--------|
| Span schema pytest tests | 33 | `tests/test_span_schemas.py` |
| DSSE receipt chain tests | 20 | `tests/test_attestation_chain.py` |
| Bundle manifest tests | 17 | `tests/test_bundle_manifests.py` |
| Formula receipt tests | 93 | `tests/test_formula_receipts.py` |
| Substrate self-tests (doctests + asserts) | 269 | `uds_v18_24_substrate.py` |
| Lean declarations (org) | 626 | [lutar-lean](https://github.com/szl-holdings/lutar-lean) |
| Lean axioms (org) | 15 | [lutar-lean](https://github.com/szl-holdings/lutar-lean) |
| HF Spaces (org) | 26 | [SZLHOLDINGS HF org](https://huggingface.co/SZLHOLDINGS) |
| HF datasets (org) | 29 | [SZLHOLDINGS HF org](https://huggingface.co/SZLHOLDINGS) |
| Zenodo DOIs (org) | 7 | [Zenodo community](https://zenodo.org/communities/szl-holdings) |

---

## Architecture

```
Component A ──span──► uds-mesh schema validator ──receipt──► DSSE wrapper
Component B ──span──►                            ──receipt──► OTLP exporter (vsp-otel)
Component C ──span──►                            ──receipt──► Audit fiber bundle
```

gRPC/Protobuf span contracts govern the schema across components. A15 ELZ invariant (STAGED) provides the topological guarantee that no audit-fiber severing can occur at component boundaries.

---

## Quick start

```bash
pip install -e .
pytest tests/                          # 163 tests (33 schema + 20 chain + 17 bundle + 93 formula)
python uds_v18_24_substrate.py         # 269 self-tests
```

---

## License

[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) — SZL Holdings

---

## Citation

```
S. P. Lutar Jr., "uds-mesh — UDS Governance Span Mesh,"
Zenodo, DOI 10.5281/zenodo.20434276, 2026.
```
ORCID: [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173)

---

## Security

See [SECURITY.md](./SECURITY.md) for responsible-disclosure policy.
