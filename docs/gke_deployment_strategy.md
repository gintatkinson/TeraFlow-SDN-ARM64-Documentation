# Google Cloud (GKE) Deployment Strategy - xG-AI Cognitive Controller

This strategy outlines the transition of the xG-AI Cognitive Controller from the local ARM64 Multipass environment to a production-grade Google Kubernetes Engine (GKE) cluster.

## 1. Compute Architecture
- **Option A: Native ARM64 (Tau T2A)**: Continue using the current ARM64-optimized images (dev10). This minimizes change risks and leverages high-performance ARM nodes.
- **Option B: Standard x86 (N2/N2D)**: Revert binary patches (like `grpc_health_probe`) to use standard x86 images. GKE offers greater machine type variety in this category.

## 2. Storage & Persistence
> [!IMPORTANT]
> The ephemeral storage issue (MicroK8s restart data loss) is resolved by moving to Google Cloud persistent storage.

- **Context Database**: Deploy PostgreSQL using HA configurations with **GCE Persistent Disks (SSD)**.
- **Backups**: Implement automated snapshots via GKE Backup for GKE or standard Velero integration.

## 3. Network & Access Control
- **Cloud Load Balancer**: Replace `socat` bridges with a **GKE Ingress** or a `LoadBalancer` service type. 
- **Domain Mapping**: Map `xg-ai.controller.cloud` to the resulting Google CLB IP.
- **Security**: Utilize Google Cloud Armor for DDoS protection and IAP (Identity-Aware Proxy) for authenticated WebUI access.

## 4. Container Life Cycle
- **Registry**: Migrate from the local registry to **Google Artifact Registry (GAR)**.
- **CI/CD**: Integrate GitHub Actions (using the `documentation` repo) to automatically build and push to GAR on every merge to `master`.

## 5. Deployment Workflow
1. **Provision GKE**: Create a 3-node cluster in `us-central1`.
2. **Setup GAR**: Create a private repository for `tfs/webui` and other services.
3. **Apply Secrets**: Inject database credentials and GitHub secrets.
4. **Deploy Manifests**: Run `kubectl apply` using the standardized manifests in the repository.
5. **DNS cutover**: Update the public endpoint once the health checks are green.

---
**Status**: Ready for GKE pilot deployment.
