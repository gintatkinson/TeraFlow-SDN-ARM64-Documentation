# Northbound Interfaces (NBI)

The TeraFlowSDN (TFS) Northbound Interface (NBI) service provides a set of standardized and programmable interfaces for higher-layer systems (OSS/BSS, Orchestrators like OSM) to interact with the network controller. It abstracts the underlying gRPC microservices into standard protocols.

## Supported Protocols and Frameworks

The NBI service is a multi-protocol gateway that currently supports:

### 1. IETF Network Slice (IETF-NS)
- **Purpose**: Enables the creation and management of network slices using the IETF YANG model.
- **Interface**: RESTConf / HTTP.
- **Key Operations**: Provisioning transport network slices, setting SLOs/SLEs.

### 2. TAPI (Transport API)
- **Purpose**: Standardized interface for transport network topology and connectivity management.
- **Interface**: REST / HTTP.
- **Key Operations**: Topology retrieval (Nodes, Edges), Connectivity Service creation.

### 3. ETSI BWM (Bandwidth Management)
- **Purpose**: Specific to edge computing or application-triggered bandwidth adjustments.
- **Interface**: REST / HTTP.
- **Key Operations**: Dynamic bandwidth reservation and release.

### 4. RESTCONF (Generic)
- **Purpose**: General-purpose data model access via RESTCONF.
- **Documentation**: Includes support for standard IETF and OpenConfig YANG models.

## Integration Architecture

1.  **NBI Gateway**: Acts as an HTTP/REST server that translates incoming requests to internal gRPC calls.
2.  **Model Mapping**: Uses specialized bindings (e.g., Pyangbind) to translate between YANG/JSON and internal protobuf messages.
3.  **Authentication**: (Optional) Can be integrated with OAuth2/JWT for secure access.

## Accessing the NBI

By default, the NBI service is exposed on a specific port in the Kubernetes cluster (see `manifests/nbiservice.yaml`).

| Protocol | Typical Path |
| :--- | :--- |
| IETF Network Slice | `/restconf/data/ietf-network-slice:network-slices` |
| TAPI | `/tapi-common:context/` |
| ETSI BWM | `/etsi-bwm/` |

## Usage Examples

Example cURL for TAPI Topology:
```bash
curl -X GET http://<NBI_IP>:<PORT>/tapi-common:context/tapi-topology:topology-context/
```
