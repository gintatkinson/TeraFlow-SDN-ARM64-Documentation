# Optical Control and Virtual Network Topology (VNT)

TeraFlowSDN (TFS) provides a specialized framework for managing optical networks and mapping them into a virtual network topology (VNT). This ensures that higher-layer services can seamlessly leverage optical capacity without managing the underlying physics (WDM, RSA, etc.).

## Core Components

### 1. Optical Controller (`opticalcontroller`)
The Optical Controller provides a RESTful interface for managing physical and logical optical resources. It abstracts the complexities of optical path computation and device configuration.
- **REST API**: Provides endpoints such as `/AddLightpath` and `/DeleteLightpath`.
- **RSA Engine**: Implements the Routing and Spectrum Allocation (RSA) algorithm to find optimal paths and frequency slots in the WDM grid.
- **Resource Management**: Tracks available frequency slots, transponders, and amplifiers.

### 2. VNT Manager (`vnt_manager`)
The VNT Manager acts as the bridge between the multi-layer controller (TeraFlowSDN) and the optical domain.
- **VLink Creation**: Requests the creation of optical lightpaths from the Optical Controller to serve as "virtual links" in the higher-layer topology.
- **Topology Augmentation**: Once an optical lightpath is established, the VNT Manager adds it as a link in the `ContextService` topology.
- **Orchestration**: Manages the lifecycle of virtual links based on dynamic traffic demands.

## Common Workflows

### Lightpath Provisioning
1.  **Request**: A higher-layer service (e.g., L3VPN) requires more capacity between two locations.
2.  **Trigger**: The VNT Manager detects the demand and requests an optical lightpath from the Optical Controller.
3.  **Computation**: The Optical Controller's RSA engine computes a valid path and spectrum.
4.  **Deployment**: The Optical Controller configures the optical devices (ROADM, Transponders).
5.  **Exposure**: The lightpath is exposed as a high-capacity Virtual Link in the TFS topology.

## Integration

- **Monitoring**: Collects performance metrics (e.g., SNR, power levels) from optical devices.
- **L3-L0 Mapping**: Maps IP/Packet flows to underlying optical wavelengths.

## Usage (REST)

Example Optical Controller API call:
```http
POST /AddLightpath/<src>/<dst>/<bitrate>/<bidir>
```
- `<src>/<dst>`: Device names or UUIDs.
- `<bitrate>`: Requested capacity in Gbps.
- `<bidir>`: Bidirectional flag (0 or 1).
