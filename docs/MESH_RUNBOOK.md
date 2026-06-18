<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- © 2026 Lutar, Stephen P. — SZL Holdings · ORCID 0009-0001-0110-4173 -->

# UDS-Mesh deploy + rollback runbook

**Canonical home:** `szl-holdings/uds-mesh` (ADR-0001).
**Doctrine v11 — 749/14/163 — c7c0ba17 · HONESTY OVER CHECKLIST.**

Operational runbook for the offline-validatable mesh surface in `manifests/`
(Istio mTLS, OTLP collector, NetworkPolicies). It covers what runs in CI today,
how to deploy onto a real cluster, and a **tested rollback** path.

> **Honest scope.** Everything under `manifests/` is **declared + offline-validated**
> and is **not deployed to a production cluster** by this repo (see `docs/MESH.md` §4).
> The deploy steps below are the documented procedure for an operator who *does* have
> a UDS Core cluster; the rollback steps in §3 are validated with `--dry-run=client`
> (offline) here and are runnable for real on a live cluster.

---

## 1. What CI verifies (no cluster)

```bash
# Manifest invariants — runs in .github/workflows/tests.yml
python -m pytest tests/test_manifests.py -v
# 9 passed: STRICT mTLS ×5, ISTIO_MUTUAL, OTLP gRPC receiver + exporter pipeline,
#           collector digest-pin + non-root securityContext + probes + limits,
#           NetworkPolicy default-deny + explicit allows.

# Full mesh suite + substrate self-test
python -m pytest -q                # 270 passed, 1 skipped
python3 uds_v18_24_substrate.py    # OK 275 tests
```

Offline schema validation (requires `kubeconform` locally — not in CI):

```bash
kubeconform -strict -summary \
  manifests/otel/collector.yaml manifests/netpol/network-policies.yaml
# Summary: 7 resources found - Valid: 7, Invalid: 0
```

---

## 2. Deploy onto a UDS Core cluster (operator procedure)

Prereqs: a UDS Core cluster with Istio + a NetworkPolicy-capable CNI
(Calico/Cilium), `kubectl` context pointed at it, and the five organ namespaces
labelled `szl.mesh/organ-namespace=true`.

```bash
# 0. Sanity: never apply blind. Diff first.
kubectl apply --dry-run=client -f manifests/istio/ -f manifests/otel/ -f manifests/netpol/

# 1. Identity layer (mTLS) BEFORE reachability layer, so enrolled pods can talk.
kubectl apply -f manifests/istio/peer-authentication.yaml
kubectl apply -f manifests/istio/destination-rule.yaml

# 2. Telemetry collector.
kubectl apply -f manifests/otel/collector.yaml
kubectl -n szl-mesh rollout status deploy/mesh-otlp-collector --timeout=120s

# 3. Reachability layer (NetworkPolicy). Apply the ALLOWs together with the deny
#    in one `kubectl apply -f file` so there is no window where default-deny is
#    active without its allow-rules.
kubectl apply -f manifests/netpol/network-policies.yaml
```

**Verify:**

```bash
kubectl -n szl-mesh get pod -l app=mesh-otlp-collector          # Running, READY 1/1
kubectl -n szl-mesh get networkpolicy                           # 4 policies
istioctl x describe pod -n szl-mesh <collector-pod>             # mTLS: STRICT
```

---

## 3. Rollback (tested)

Rollback is **resource deletion in reverse dependency order**: drop the
reachability layer first (so nothing is stranded behind a default-deny with its
allows removed), then telemetry, then the identity layer.

```bash
# 1. Remove NetworkPolicies first. Deleting the whole file removes the deny AND
#    its allows together — it does NOT leave a bare default-deny in place.
kubectl delete -f manifests/netpol/network-policies.yaml

# 2. Remove the collector.
kubectl delete -f manifests/otel/collector.yaml

# 3. Remove the Istio mTLS posture LAST.
kubectl delete -f manifests/istio/destination-rule.yaml
kubectl delete -f manifests/istio/peer-authentication.yaml
```

**Pitfall (validated):** deleting *only* `default-deny-all` while leaving the
allow-rules, or deleting the allow-rules while leaving `default-deny-all`, both
leave the namespace in a broken state (the latter blocks all collector traffic).
Always delete the whole `network-policies.yaml` as a unit. This is why the file
bundles deny + allows together.

### Rollback dry-run validated offline in this repo

```bash
# Confirms the delete targets resolve and the manifests are well-formed, without
# a cluster. Run from repo root:
for f in manifests/netpol/network-policies.yaml manifests/otel/collector.yaml \
         manifests/istio/destination-rule.yaml manifests/istio/peer-authentication.yaml; do
  python3 -c "import yaml,sys; list(yaml.safe_load_all(open('$f'))); print('parse-OK', '$f')"
done
```

### Partial-deploy recovery

If step 2 (collector rollout) fails, the safe state is **no NetworkPolicies
applied yet** (step 3 not reached): organ pods retain whatever uds-core baseline
policy they had. Fix the collector, re-run step 2, then proceed to step 3. Never
apply step 3 (default-deny) while the collector is not Ready, or organ telemetry
will be dropped with no destination.

---

## 4. Image provenance

The collector image is **pinned by digest** in `manifests/otel/collector.yaml`:

```
otel/opentelemetry-collector-contrib:0.104.0@sha256:e07e325e303e86f4a87a617491e921b579a92da6d404007394757ac910bf9587
```

Re-resolve / verify the digest before a bump:

```bash
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:otel/opentelemetry-collector-contrib:pull" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
curl -sI -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.oci.image.index.v1+json" \
  https://registry-1.docker.io/v2/otel/opentelemetry-collector-contrib/manifests/0.104.0 \
  | grep -i docker-content-digest
# docker-content-digest: sha256:e07e325e303e86f4a87a617491e921b579a92da6d404007394757ac910bf9587
```

---

*License: Apache-2.0 · © 2026 Lutar, Stephen P. — SZL Holdings*

Doctrine v11 — 749/14/163 — c7c0ba17 · Λ = Conjecture 1 (never a theorem) · SLSA L1+L2 · HONESTY OVER CHECKLIST
