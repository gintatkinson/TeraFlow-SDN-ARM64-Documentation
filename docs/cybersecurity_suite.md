# TeraFlowSDN Cybersecurity Suite

TeraFlowSDN (TFS) includes a comprehensive cybersecurity framework designed to detect and mitigate attacks at both the L3 (IP) and Optical (Physical) layers.

## L3 Cybersecurity Flow

The L3 security suite is designed to detect sophisticated attacks like cryptomining and DDoS using Machine Learning.

### 1. L3 Distributed Attack Detector (DAD)
- **Role**: Edge monitoring and feature extraction.
- **Mechanism**: DAD instances monitor traffic logs (e.g., Tstat) near the network edge. They extract connection-level features (IPs, ports, flow timing, packet sizes).
- **Output**: Sends `L3CentralizedattackdetectorMetrics` to the CAD.

### 2. L3 Centralized Attack Detector (CAD)
- **Role**: AI-driven analysis.
- **Mechanism**: Receives metrics from multiple DADs. It uses an **ML model (ONNX format)** to classify traffic as "Normal" or "Crypto".
- **Monitoring Integration**: CAD generates KPIs (e.g., security status, ML confidence) and pushes them to the `Monitoring` service.
- **Trigger**: When an attack is detected, it calls the `PerformMitigation` RPC on the Attack Mitigator.

### 3. L3 Attack Mitigator (AM)
- **Role**: Automated response.
- **Mechanism**: Receives the attack details (source/destination IPs and ports). It maps the attack to a specific network service and device.
- **Enforcement**: Communicates with the `Service` microservice to inject an **ACL Rule (DROP)** into the running configuration of the affected service.

## Optical Cybersecurity

Focused on anomalies and attacks targeting the optical transport layer (e.g., power fluctuations, unauthorized tapping).

- **Optical Attack Detector**: Uses unsupervised learning (**DBSCAN**) via the `DbscanServing` component to identify anomalies in optical performance metrics (OPM).
- **Optical Attack Manager**: Coordinates security policies for optical channels and manages detection states.
- **Optical Attack Mitigator**: Facilitates restoration or rerouting of optical services in response to physical-layer attacks.

## Key Components & Files
- `src/l3_distributedattackdetector/`: Traffic ingestion and feature extraction.
- `src/l3_centralizedattackdetector/`: ML inference (Cryptomining detector).
- `src/l3_attackmitigator/`: ACL-based mitigation logic.
- `src/opticalattackdetector/`: Optical anomaly detection.
- `src/dbscanserving/`: Shared anomaly detection service.
