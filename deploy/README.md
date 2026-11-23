# Kubernetes deployment

A Kustomize base for running the server in-cluster, optionally exposed through a [Gateway API](https://gateway-api.sigs.k8s.io/) Gateway.

```bash
kubectl apply -k deploy/
```

Requires Kubernetes 1.30+ (for the `sleep` preStop hook).

## Configure

| What | Where | Default |
|------|-------|---------|
| Namespace allowed to connect | `networkpolicy.yaml` → `ingress` | `gateway-system` |
| Image version | `kustomization.yaml` → `images` | `latest` |
| External access (optional) | uncomment `grpcroute.yaml` in `kustomization.yaml`, then set its `parentRefs` and `hostnames` | off |

The route needs the Gateway API CRDs (v1.1+, for `GRPCRoute`).

The image tracks `latest` and the pods use `imagePullPolicy: Always`, so a restart picks up a new release:

```bash
kubectl -n yfinance-grpc rollout restart deployment/yfinance-grpc
```

To pin a version instead, set `newTag` (and optionally `digest`) in `kustomization.yaml`.

## What's in it

| File | Purpose |
|------|---------|
| `namespace.yaml` | Namespace enforcing the `restricted` Pod Security Standard |
| `serviceaccount.yaml` | Dedicated identity; no API token mounted |
| `deployment.yaml` | 2 replicas, hardened pod (below), probes, graceful rollout |
| `service.yaml` | ClusterIP on 50059 with `appProtocol: kubernetes.io/h2c` so gateways speak HTTP/2 |
| `networkpolicy.yaml` | Ingress only from the Gateway's namespace; egress only to DNS and public HTTPS |
| `grpcroute.yaml` | Optional, off by default. Routes the four API services; reflection is not exposed |

## Security posture

- Distroless image (no shell, no package manager). Runs as uid 65532, non-root, no privilege escalation, all capabilities dropped, `RuntimeDefault` seccomp.
- Read-only root filesystem. Two size-limited `emptyDir` volumes are writable: `/tmp`, and `~/.cache` for yfinance's cookie and timezone caches (without that cache, every request logs in to Yahoo again).
- No Kubernetes API access: no RBAC, no token, service links disabled.
- Egress excludes private ranges and link-local addresses, including the cloud metadata endpoint.
- TLS terminates at the Gateway; pod-to-pod traffic is cleartext h2c inside the cluster. Add a mesh if you need mTLS there.

The NetworkPolicy only takes effect with a CNI that enforces it (Cilium, Calico, kindnet ≥ 0.24, ...).

## Probes and shutdown

The server has no `grpc.health.v1` service yet, so the probes check the TCP port. On SIGTERM, the preStop hook first keeps the pod serving for 5s while gateways remove it, then the server stops accepting RPCs and drains in-flight ones for up to 10s, well inside the 30s grace period.
