# uds-mesh

**Status:** ACTIVE — resurrected 2026-06-03 for the per-flagship `.uds` payload build.

UDS cross-component span schemas + DSSE governance receipts onto the Khipu Merkle DAG.
This repo defines how the five SZL flagship organs talk to each other across the
mesh: the OTEL span schemas they emit, the cross-organ DSSE receipt envelope that
binds those spans to the provenance chain, and the pointer manifest that pins the
mesh at an immutable version.

> Previously archived (config was mirrored into szl-fleet-overlay). Un-archived so
> the five per-organ `.uds` payloads — `a11oy`, `sentra`, `amaru`, `killinchu`,
> `rosie` — are fully readable for the customer environment build.

---

## The five flagship organs

| Organ | Role | Span schema | Namespace / Service |
|---|---|---|---|
| **a11oy** | Policy + receipt substrate orchestrator (Λ governance, GraphLambda) | `schemas/spans/a11oy.graph.yaml` | `szl-a11oy` / `szl-a11oy` |
| **sentra** | Cyber-resilience runtime, fail-closed Safety Gate (NIST CSF 2.0 + D3FEND) | `schemas/spans/sentra.gate.yaml` | `szl-sentra` / `szl-sentra` |
| **amaru** | Convergent data-sync, KL-drift bounded replication + proof receipts | `schemas/spans/amaru.sync.yaml` | `szl-amaru` / `szl-amaru` |
| **killinchu** | Receipt/transport courier — DSSE receipt relay across organs | `schemas/spans/killinchu.courier.yaml` | `szl-killinchu` / `szl-killinchu` |
| **rosie** | Governed decision fabric — mandatory witnesses on every decision (ROSIE-V1) | `schemas/spans/rosie.decision.yaml` | `szl-rosie` / `szl-rosie` |

All five span schemas share a common cross-organ envelope (`szl.mesh.*` attributes:
`organ`, `receipt_hash`, `dsse_payload_type`, `image_digest`, `lambda_value`,
`governance_drift`, `upstream_organ`) so the mesh can correlate a single decision
as it crosses organ boundaries. `a11oy.graph.yaml` additionally carries the
graph-Lambda attributes (`szl.graph.*`).

Validate all five schemas:

```bash
bash schemas/spans/test_mesh_spans.sh
```

## Mesh wiring (how organs talk)

Each organ is registered with the UDS Operator (uds-core) via a `Package` CR
(`kind: Package`, `apiVersion: uds.dev/v1alpha1`) which provisions:

- **mTLS** — Istio sidecar injection (managed by UDS Core).
- **Service discovery** — `network.expose` (host `<organ>`, gateway `tenant`) and
  UDS-operated NetworkPolicies (Ingress IntraNamespace + scoped Egress).
- **DSSE receipt egress** — every organ has an Egress allow to the `szl-receipts`
  server (port 8080) where its DSSE governance receipts are sealed into the Khipu
  Merkle DAG.
- **SSO** — a Keycloak OIDC client `uds-szl-<organ>`.

The cross-organ receipt path: an organ emits a span → seals a DSSE receipt →
**killinchu** couriers the receipt to the destination organ's sink (fail-closed
signature verification) → the receipt is bound into the provenance chain.

## Mesh pointer manifest

`uds-mesh-pointer-manifest.yaml` is the single authoritative record of what
constitutes the mesh at `uds-v0.2.0`. It binds all five organs:
the four with published, cosign-signed release tarballs (a11oy, sentra, amaru,
rosie) by tarball SHA-256, and killinchu by its live cosign-signed ghcr.io image
digest.

## Deployable payloads (the five `.uds` packages)

The mesh defines the schemas and receipts; the **deployable** per-organ payloads
(Zarf packages + Helm charts) live in:

- `szl-holdings/uds-bundles` → `bundles/szl-<organ>/` (per-organ Zarf package +
  Helm chart + policies + SBOM + attestations)
- `szl-holdings/szl-uds-deployment` → `packages/<organ>/` (Zarf package) and
  `bundles/szl-uds-bundle/uds-bundle.yaml` (the composed customer bundle)

Customer one-liner (Windows + WSL2):

```bash
uds deploy oci://ghcr.io/szl-holdings/szl-uds-bundle:uds-v0.2.0 --confirm
```

---

*SLSA provenance: L1 (honest). Apache-2.0. Doctrine v11 — 749/14/163.*

*Signed-off-by: Yachay <yachay@szlholdings.ai>*
*Co-Authored-By: Perplexity Computer Agent <agent@perplexity.ai>*
