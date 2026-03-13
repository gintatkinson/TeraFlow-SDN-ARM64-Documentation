# End-to-End (E2E) Orchestration

The End-to-End (E2E) Orchestrator in TeraFlowSDN is responsible for coordinating network services across multiple administrative or technology domains. It acts as a "super-controller" that leverages lower-level domain controllers to establish end-to-end connectivity.

## Core Features

- **Multi-Controller Coordination**: Discovers and interacts with other TFS controllers or external SDN controllers.
- **Path Computation**: Computes end-to-end paths across multiple domains using abstract topology information.
- **Service Provisioning**: Triggers service creation in each involved domain to fulfill an E2E request.
- **Inter-Domain Link Management**: Tracks and manages links connecting different domains.

## Architecture

The E2E Orchestrator consists of:

1.  **E2EOrchestrator Service**: The primary gRPC service interface.
2.  **Subscription Manager**: Manages subscriptions to remote controllers for topology updates.
3.  **Controller Discoverer**: Automatically discovers remote controllers based on configuration or environment variables.

## Comparison: E2E vs. Inter-Domain

| Feature | E2E Orchestrator | Inter-Domain Service |
| :--- | :--- | :--- |
| **Focus** | Multi-domain coordination | Direct peer-to-peer peering |
| **Logic** | Hierarchical / Centralized | Distributed / Peering |
| **Interaction** | Talks to multiple domain controllers | Talks to peering TFS instances |

## Usage (gRPC)

Key RPC methods provided by `E2EOrchestratorService`:

- `ComputePath(Service)`: Computes an E2E path for a given service request.
- `ProvisionService(Service)`: Fully provisions an E2E service across domains.
- `DeactivateService(Service)`: Tears down an E2E service and releases resources in all domains.
