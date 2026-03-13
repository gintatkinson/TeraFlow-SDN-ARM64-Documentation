# TeraFlowSDN Inter-Domain & E2E Orchestration

TeraFlowSDN (TFS) is designed to operate in multi-layer and multi-domain environments, where a single service might traverse multiple administrative domains or different networking technologies (e.g., Packet over Optical).

## Inter-Domain Federation

The **Inter-Domain** microservice allows multiple TFS controller instances to discover each other and exchange topology information.

### Key Features
- **Remote Domain Discovery**: Configuration of peer controller endpoints and authentication.
- **Topology Abstraction**: Each domain can export a simplified version of its local topology to peers, hiding internal complexity while still allowing for path computation.
- **Cross-Domain Path Request**: When a service request spans domains, the local Inter-Domain component communicates with remote peers to negotiate cross-border links.

## E2E Orchestrator

The **E2E Orchestrator** acts as a higher-level "controller of controllers" (Child-Parent relationship) or a cross-layer coordinator.

### Orchestration Tiers
1. **Vertical (Cross-Layer)**: Orchestrating an IP service that requires an underlying Optical channel. It coordinates the `Service` microservice and the `OpticalController`.
2. **Horizontal (Multi-Domain)**: Decomposing an end-to-end service request into multiple segments, each managed by a different TFS domain or a lower-level controller.

### Path Computation Logic
The E2E Orchestrator uses a global (or abstracted) view of the multi-domain graph (often computed via `networkx` or delegated to specialized TE engines) to find the sequence of domains and border nodes required to fulfill the request.

## Component Interaction
- `src/interdomain/`: Handles gRPC communication with peer TFS instances.
- `src/e2e_orchestrator/`: Logic for decomposing and monitoring end-to-end services.
- `src/vnt_manager/`: Maintains the virtualized, consolidated view of multi-domain resources.
