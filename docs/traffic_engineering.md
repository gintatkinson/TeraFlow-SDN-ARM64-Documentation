# TeraFlowSDN Traffic Engineering (TE)

The **Traffic Engineering (TE)** component in TeraFlowSDN (TFS) provides advanced path optimization for carrier-grade networks.

## Implementation Details

Uniquely within the TFS ecosystem, the TE component is implemented in **Erlang**. This choice leverages Erlang's strengths in massive concurrency and fault tolerance, making it ideal for the highly complex, multi-objective optimizations required for Traffic Engineering.

### Core Responsibilities
- **Path Optimization**: Beyond simple shortest-path, the TE engine considers multiple constraints:
  - **Bandwidth Availability**: Ensuring links are not oversubscribed.
  - **Latency Constraints**: Supporting real-time applications.
  - **Path Diversity**: Computing disjoint primary and backup paths for high availability.
- **Resource Admission Control**: Validates whether a new service can be admitted without degrading existing services.

## Architecture

- **Erlang VM**: The core engine runs as a separate, highly efficient process.
- **gRPC Interface**: Despite its Erlang core, it exposes standard gRPC interfaces to the rest of the TFS microservices.
- **Integration**: Works closely with the `PathComp` and `Service` microservices to refine path calculations for mission-critical services.

## Component Path
- `src/te/`: Contains the Erlang source code (`apps/`), build configurations (`rebar.config`), and integration logic.
