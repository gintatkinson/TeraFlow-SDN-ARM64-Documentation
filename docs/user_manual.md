# TeraFlowSDN User Manual

This manual provides instructions on how to interact with the TeraFlowSDN (TFS) controller via its Web User Interface (WebUI) and Northbound Interface (NBI) REST APIs.

## 1. Accessing the WebUI

The WebUI is the primary graphical interface for managing the controller. Once deployed, it is typically accessible via:

- **URL**: `http://<controller-ip>:<port>/` (Default port is often 80 or mapped via Kubernetes ingress).
- **Default Credentials**: Check your deployment configuration (often no authentication is required for local dev environments).

### System Architecture & Capabilities
- **[High-Level Architecture](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/design_architecture.md)**: Overview of the microservice ecosystem.
- **[Service Lifecycle](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/service_lifecycle.md)**: How to create and manage services and slices.
- **[Traffic Engineering](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/traffic_engineering.md)**: Path computation and TE policies.
- **[Optical Control & VNT](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/optical_control.md)**: Managing physical and virtual optical links.
- **[QKD Capability](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/qkd_capability.md)**: Orchestrating Quantum Key Distribution apps.
- **[E2E Orchestration](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/e2e_orchestration.md)**: Multi-domain service coordination.
- **[ZTP & Inventory](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/ztp_inventory.md)**: Automated device onboarding.
- **[Policy Management](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/policy_management.md)**: Enforcing SLAs and remediation rules.
- **[Monitoring & Analytics](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/monitoring_analytics.md)**: Telemetry and data analysis.
- **[Northbound Interfaces](file:///Users/perkunas/.gemini/antigravity/scratch/teraflow-code/docs/nbi_interfaces.md)**: TAPI, IETF-NS, and RESTCONF access.

### Main Sections
- **Topology**: Visualize the network graph, including devices and links.
- **Device**: Onboard, configure, and monitor network devices (Switches, Routers, Transponders).
- **Service**: Create and manage connectivity services (L2VPN, L3VPN, Optical).
- **Slice**: Manage end-to-end network slices.
- **Context/Topology Selector**: Use the top-right dropdowns to switch between different contexts and topologies.

## 2. Onboarding a Device

To bring a device under TFS management:

1. Navigate to the **Device** section in the WebUI.
2. Click **Add Device**.
3. Fill in the device details:
   - **Device ID**: A unique name for the device.
   - **Device Type**: (e.g., `ip-swich`, `optical-transponder`).
   - **Driver**: Select the appropriate driver (e.g., `OpenConfig`, `Netconf`, `P4`).
   - **Address/Port**: The management IP and port of the device.
4. Click **Connect**. The controller will attempt to reach the device and retrieve its initial configuration.

## 3. Creating a Service

To provision connectivity between two endpoints:

1. Navigate to the **Service** section.
2. Click **Create Service**.
3. Select the **Service Type** (e.g., `L3NM`, `L2NM`, `Optical Connection`).
4. Select the **Endpoints**: Choose the source and destination device/interfaces.
5. Define **Constraints**: (Optional) Add constraints like bandwidth, latency, or disjoint paths.
6. Click **Create**. TFS will compute the path and configure the involved devices automatically.

## 4. Northbound Interface (NBI) REST API

The NBI allows external systems (e.g., Orchestrators, OSS/BSS) to programmatically interact with TFS.

### API Entry Points
- **Standard IETF APIs**:
  - `/restconf/data/ietf-l2vpn-svc:l2vpn-svc`
  - `/restconf/data/ietf-l3vpn-svc:l3vpn-svc`
  - `/restconf/data/ietf-network-slice-service:network-slice-services`
- **TFS Native API**:
  - `/tfs-api/context`: Manage contexts, topologies, and devices.
  - `/tfs-api/service`: Manage services.

### Example: Listing Contexts
```bash
curl -X GET http://<nbi-ip>:<port>/tfs-api/context
```

### Example: Creating an L3VPN Service (IETF)
```bash
curl -X POST http://<nbi-ip>:<port>/restconf/data/ietf-l3vpn-svc:l3vpn-svc/vpn-services \
     -H "Content-Type: application/json" \
     -d @service_request.json
```

## 5. Security & Cybersecurity

The TFS controller provides real-time security monitoring:

### Monitoring Attacks
- The **WebUI** includes dashboards to visualize security KPIs such as "Security Status" and "ML Confidence".
- Active attacks are logged in the `Context` and can be audited via the DLT (Distributed Ledger) if deployed.

### Automated Mitigation
- When an attack is detected, TFS automatically attempts to apply an ACL rule to block the source.
- You can view these rules in the **Service** configuration within the WebUI.

## 6. Advanced Features

### Zero-Touch Provisioning (ZTP)
Devices can be configured to auto-onboard. When a new device is detected on the network, ZTP pulls its initial configuration from the **Policy** service and pushes it via the **Device** component.

### Real-Time Analytics
The **Analytics** component processes telemetry streams using Spark. This is used for predictive maintenance and automated scaling of network slices.

## 7. Multi-Domain & Cross-Layer Orchestration

### E2E Orchestrator
For services spanning multiple network layers (e.g., IP over Optical) or multiple administrative domains, use the **E2E Orchestrator**. It automatically decomposes complex requests into sub-service requests for the relevant underlying components.

### Inter-Domain Connectivity
TFS can federate with other controller instances. The **Inter-Domain** component abstracts local topology and shares it with peers to enable seamless cross-controller path computation.

## 8. Simulation & Benchmarking

You can run network-scale simulations using the **Load Generator**:
1. Access the **Load Gen** section in the WebUI.
2. Select a pre-defined test scenario or configure the arrival rate and service type.
3. Click **Start**. The controller will begin orchestrating thousands of simulated services.
4. Monitor performance (latency, success rate) via the integrated Grafana dashboards.

## 9. Auditing (DLT)

If **DLT** is enabled, every service modification is recorded on a private Hyperledger Fabric blockchain.
- This provides an immutable audit trail of "who did what and when".
- This is particularly useful for verifying SLA compliance in multi-provider environments.

## 10. Service Availability Note

The features documented in sections 5-9 (Cybersecurity, DLT, Forecaster, etc.) require additional components to be enabled in the `TFS_COMPONENTS` deployment variable. 

- **Core Deployment**: Includes Context, Device, Service, PathComp, NBI, WebUI. (Active in this VM)
- **Advanced Deployment**: Requires enabling specialized services (e.g., `l3_centralizedattackdetector`, `dlt-gateway`, `forecaster`) in the deployment scripts.

## 11. Troubleshooting

- **Check Pod Status**: Use `kubectl get pods -n tfs` to ensure all microservices are running.
- **E2E Failures**: Check `e2eorchestratorservice` logs if a cross-domain service fails to provision.
- **Security Logs**: If an attack is suspected, check logs for `l3-centralizedattackdetector` to see ML inference results.
- **DLT Status**: Ensure the `dltgateway` is connected to a running blockchain peer before logging events.
