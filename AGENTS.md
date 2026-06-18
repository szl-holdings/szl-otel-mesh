# AGENTS.md

## Cursor Cloud specific instructions

This is the **canonical home of the UDS mesh** (ADR-0001). It contains the mesh
Python runtime (`mesh/`, `src/mesh/`), OTEL span schemas, deploy manifests
(`manifests/` — Istio mTLS, OTLP collector, NetworkPolicies), governance receipts,
UDS bundle manifests, and pointer manifests.

### Testing

Primary suite — the real pytest tests under `tests/` plus the substrate self-test:

```sh
python -m pytest -q                 # 270 passed, 1 skipped
python3 uds_v18_24_substrate.py     # OK 275 tests (178 doctests + 97 assertions)
```

Span-schema shell checks (also run by CI):

```sh
bash schemas/spans/test_graph_spans.sh   # a11oy.graph.* schema — 25 checks
bash schemas/spans/test_mesh_spans.sh    # 5 cross-organ span schemas — 65 checks
```

All must be run from the repo root.

### Linting

Pre-commit hooks are configured (`.pre-commit-config.yaml`). Run with:

```sh
pre-commit run --all-files
```

**Known issue:** The `check-yaml` hook reports a parsing error on `schemas/spans/a11oy.graph.yaml` because the file uses YAML list items under a mapping key without the expected block-end marker. This is a pre-existing condition in the repository and does not affect the CI test script.

### CI checks (replicated locally)

The CI workflow (`.github/workflows/ci.yml`) validates:
1. Required governance files exist (`README.md`, `LICENSE`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CITATION.cff`)
2. `CITATION.cff` contains the ORCID
3. `uds-bundle.yaml` manifest is present
4. Schema test passes (`bash schemas/spans/test_graph_spans.sh`)

### Build/run

The mesh runtime is importable Python (`mesh/`, `src/mesh/`) plus declarative
schemas and manifests; there is no long-running service to start. The TypeScript
mesh SDK under `mesh/sdk/` builds with `npm --prefix mesh/sdk run build`. Deploy
procedure and tested rollback for the `manifests/` surface: `docs/MESH_RUNBOOK.md`.
