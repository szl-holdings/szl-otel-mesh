# Mesh deployment manifests (WU-2)

Real, offline-validatable Kubernetes/Istio surface for the UDS mesh, landed in the
**canonical home `szl-holdings/uds-mesh`** per **ADR-0001** (Canonical Home for the
UDS Mesh, ACCEPTED 2026-06-03).

## What's here

| Path | Purpose |
|------|---------|
| `istio/peer-authentication.yaml` | `PeerAuthentication` **STRICT** mTLS, one per organ namespace (a11oy, sentra, amaru, killinchu, rosie) |
| `istio/destination-rule.yaml` | `DestinationRule` pinning **ISTIO_MUTUAL** TLS to the mesh OTLP collector and organ services |
| `netpol/network-policies.yaml` | `NetworkPolicy` **default-deny** (ingress+egress) for the `szl-mesh` namespace + explicit allows: organ→collector OTLP (4317/4318), collector→vsp-otel (4318), DNS (53). L3/L4 complement to the Istio mTLS identity layer |
| `otel/collector.yaml` | OpenTelemetry Collector: **OTLP gRPC receiver (4317)** + HTTP (4318) → `memory_limiter`/`batch` → **OTLP exporter pipeline** forwarding to the vsp-otel Λ-gate verifier. Hardened: image **digest-pinned**, **non-root** `securityContext` (`readOnlyRootFilesystem`, `drop: [ALL]`, `seccomp: RuntimeDefault`), liveness/readiness probes on the `health_check` extension (:13133), resource requests+limits |

## HONESTY OVER CHECKLIST

- **No live cluster in CI.** These manifests are validated **offline** only. The mesh
  is not deployed by this PR; live Istio/k8s wiring is a disclosed boundary.
- The collector forwards to `vsp-otel-collector.szl-mesh.svc...:4318`, which is the
  Λ-gate exporter from **vsp-otel PR #61** (`feat/real-otlp-exporter`). Cross-repo
  composition, not a reimplementation.
- Section 889 vendor list unchanged: {Huawei, ZTE, Hytera, Hikvision, Dahua}. No
  Iron Bank / FedRAMP / CMMC L2+ / SWFT / Mission Owner claims. SLSA L1+L2 only.

## Offline validation

Native k8s objects (the collector + the NetworkPolicies) validate against the
bundled schema:

```bash
kubeconform -strict -summary manifests/otel/collector.yaml manifests/netpol/network-policies.yaml
# Summary: 7 resources found - Valid: 7, Invalid: 0
```

Istio CRs need the Istio CRD schemas (not bundled in kubeconform by default):

```bash
# Option A: kubeconform with the Istio schema location
kubeconform -strict -summary \
  -schema-location default \
  -schema-location 'https://raw.githubusercontent.com/istio/istio/master/manifests/charts/base/crds/{{ .ResourceKind }}.json' \
  manifests/istio/*.yaml

# Option B: client-side dry-run against a cluster that has the Istio CRDs installed
kubectl apply --dry-run=client -f manifests/istio/ -f manifests/otel/
```

CI runs `pytest tests/test_manifests.py`, which asserts the YAML parses and carries
the security invariants (STRICT mTLS on all 5 organs, ISTIO_MUTUAL, OTLP gRPC
receiver, forwarding exporter pipeline, NetworkPolicy default-deny + explicit
allows, collector digest-pin + non-root securityContext + probes) without needing
a cluster.

## NetworkPolicy vs. Istio mTLS — why both

`PeerAuthentication: STRICT` authenticates **identity** (a caller must present a
valid SPIFFE mTLS cert). `NetworkPolicy` constrains **reachability** at L3/L4 (which
pods can open a socket at all). They are independent layers: mTLS does not stop a
compromised in-mesh pod from reaching the collector's port, and a NetworkPolicy
does not verify identity. The `netpol/` default-deny + explicit allows give the
mesh namespace a real deny-by-default posture underneath the Istio identity layer.
**HONESTY:** these NetworkPolicies are offline-validated only; enforcement requires
a CNI that implements NetworkPolicy (Calico/Cilium) on a live cluster — not run in
CI. See `docs/MESH.md` §4.

---

*See `ADR_UDS_MESH_HOME.md` (ADR-0001). License: Apache-2.0.*

Doctrine v11 — 749/14/163 — c7c0ba17 · Λ = Conjecture 1 (never a theorem).

Signed-off-by: Yachay <yachay@szlholdings.ai>
Co-Authored-By: Perplexity Computer Agent <agent@perplexity.ai>
