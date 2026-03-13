# TeraFlowSDN Distributed Ledger (DLT) & Auditing

TeraFlowSDN integrates a **Distributed Ledger Technology (DLT)** microservice to provide a tamper-proof, auditable record of critical network events and configurations.

## Architecture

The DLT component is split into two main parts:

### 1. DLT Gateway (Node.js/TypeScript)
- **Role**: Provides the interface for the DLT network.
- **Implementation**: A Express-based web server that interacts with **Hyperledger Fabric**.
- **Features**: 
  - Manages identities and certificates (Enrollment/Registration).
  - Submits transactions to the blockchain (Invoke).
  - Queries the current state or history of assets (Query).

### 2. DLT Connector (Python)
- **Role**: Integrates the blockchain logic with the rest of the TFS microservice ecosystem.
- **Implementation**: Provides a gRPC interface that other services (like `Service` or `Cybersecurity`) use to log events.
- **Flow**: When a service configuration is successfully applied, the `Service` component calls the DLT Connector to permanently record the `ServiceId` and `ConnectionId` on the ledger.

## Chaincode (Smart Contracts)

The "business logic" on the blockchain is implemented as chaincode (likely in Go or Java):
- **Service Management**: Records service creation, update, and deletion events.
- **Security Logs**: Stores immutable logs of detected attacks and mitigation actions taken by the Cybersecurity suite.
- **Service Level Agreements (SLAs)**: Can be used to record SLA violations for automated compliance and billing.

## Key Benefits
- **Accountability**: Every configuration change is signed and timestamped.
- **Non-Repudiation**: Network operators can prove that a specific configuration was requested and applied at a specific time.
- **Transparency**: Enabling trust in multi-domain scenarios where multiple providers share the same physical infrastructure.

## Component Paths
- `src/dlt/gateway/`: Node.js Hyperledger Fabric client.
- `src/dlt/connector/`: Python gRPC wrapper.
- `src/dlt/mock_blockchain/`: A mock implementation used for testing and local development without a full Fabric cluster.
