"""WU-2 manifest validation (offline): YAML well-formedness + invariant checks.

HONESTY: this does NOT contact a live Istio/k8s cluster. It asserts the manifests
parse and carry the security invariants we claim (STRICT mTLS, ISTIO_MUTUAL,
OTLP gRPC receiver, forwarding exporter). Full schema validation against the
Istio CRDs is done with kubeconform offline — see manifests/README.md for the
exact `kubeconform`/`kubectl --dry-run=client` commands.
"""
from __future__ import annotations

from pathlib import Path

import yaml

MANIFESTS = Path(__file__).resolve().parents[1] / "manifests"


def load_all(rel: str):
    docs = list(yaml.safe_load_all((MANIFESTS / rel).read_text()))
    return [d for d in docs if d]


def test_peer_authentication_all_strict():
    docs = load_all("istio/peer-authentication.yaml")
    assert len(docs) == 5, "one PeerAuthentication per organ"
    organs = set()
    for d in docs:
        assert d["kind"] == "PeerAuthentication"
        assert d["spec"]["mtls"]["mode"] == "STRICT", f"{d['metadata']['name']} not STRICT"
        organs.add(d["metadata"]["labels"]["szl.mesh/organ"])
    assert organs == {"a11oy", "sentra", "amaru", "killinchu", "rosie"}


def test_destination_rule_istio_mutual():
    docs = load_all("istio/destination-rule.yaml")
    assert docs, "destination rules present"
    for d in docs:
        assert d["kind"] == "DestinationRule"
        assert d["spec"]["trafficPolicy"]["tls"]["mode"] == "ISTIO_MUTUAL"


def test_collector_has_otlp_grpc_receiver_and_exporter_pipeline():
    docs = load_all("otel/collector.yaml")
    cms = [d for d in docs if d["kind"] == "ConfigMap"]
    assert cms, "collector ConfigMap present"
    cfg = yaml.safe_load(cms[0]["data"]["collector.yaml"])
    # gRPC receiver
    assert "grpc" in cfg["receivers"]["otlp"]["protocols"]
    assert cfg["receivers"]["otlp"]["protocols"]["grpc"]["endpoint"].endswith(":4317")
    # exporter pipeline forwards to vsp-otel
    assert any(k.startswith("otlphttp") for k in cfg["exporters"])
    pipe = cfg["service"]["pipelines"]["traces"]
    assert "otlp" in pipe["receivers"]
    assert any(e.startswith("otlphttp") for e in pipe["exporters"])


def test_collector_deployment_and_service_present():
    docs = load_all("otel/collector.yaml")
    kinds = {d["kind"] for d in docs}
    assert {"ConfigMap", "Deployment", "Service"} <= kinds


def _collector_container():
    docs = load_all("otel/collector.yaml")
    dep = next(d for d in docs if d["kind"] == "Deployment")
    return dep, dep["spec"]["template"]["spec"]["containers"][0]


def test_collector_image_pinned_by_digest():
    _dep, c = _collector_container()
    assert "@sha256:" in c["image"], "collector image must be pinned by digest"
    assert ":latest" not in c["image"]


def test_collector_has_liveness_and_readiness_probes():
    _dep, c = _collector_container()
    for probe in ("livenessProbe", "readinessProbe"):
        assert probe in c, f"collector missing {probe}"
        assert c[probe]["httpGet"]["port"] == "health"


def test_collector_securitycontext_hardened():
    dep, c = _collector_container()
    pod_sc = dep["spec"]["template"]["spec"]["securityContext"]
    assert pod_sc["runAsNonRoot"] is True
    csc = c["securityContext"]
    assert csc["allowPrivilegeEscalation"] is False
    assert csc["readOnlyRootFilesystem"] is True
    assert csc["capabilities"]["drop"] == ["ALL"]


def test_collector_resource_limits_and_requests():
    _dep, c = _collector_container()
    res = c["resources"]
    assert res["requests"]["cpu"] and res["requests"]["memory"]
    assert res["limits"]["cpu"] and res["limits"]["memory"]


def test_network_policies_default_deny_plus_allows():
    docs = load_all("netpol/network-policies.yaml")
    assert all(d["kind"] == "NetworkPolicy" for d in docs)
    names = {d["metadata"]["name"] for d in docs}
    assert "default-deny-all" in names
    deny = next(d for d in docs if d["metadata"]["name"] == "default-deny-all")
    # Empty podSelector + both policy types = namespace-wide default deny.
    assert deny["spec"]["podSelector"] == {}
    assert set(deny["spec"]["policyTypes"]) == {"Ingress", "Egress"}
    # Explicit allow-rules exist for collector ingress, vsp-otel egress, DNS.
    assert {
        "allow-otlp-ingress-to-collector",
        "allow-collector-egress-to-vsp-otel",
        "allow-dns-egress",
    } <= names


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
