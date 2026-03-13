# Quantum Key Distribution (QKD) Capability

The TeraFlowSDN (TFS) controller includes a dedicated `qkd_app` service to manage and orchestrate Quantum Key Distribution (QKD) applications. This service enables the management of quantum keys and the association of QKD applications with network services.

## Core Features

- **App Registration**: Register QKD applications with specific attributes (e.g., source and destination endpoints, priority, required key rate).
- **App Lifecycle Management**: Create, list, retrieve, and delete QKD applications via gRPC.
- **Status Monitoring**: Track the operational status of QKD applications (e.g., `INITIALIZED`, `RUNNING`, `TERMINATED`).
- **Database Integration**: PERSISTENT storage of QKD application metadata and status.

## Architecture

The QKD capability consists of:

1.  **QKDApp Service**: The main gRPC service providing the management API.
2.  **Database**: SQL-based storage (using SQLAlchemy) for application models.
3.  **Mock QKD Node**: (For testing) A mock component that simulates QKD hardware signatures and key exchange.

## Integration

The QKD capability is typically integrated with:
- **Context Service**: For resolving device and link identifiers.
- **Service/Slice Service**: When QKD-secured connectivity is requested.

## Usage (gRPC)

Key RPC methods provided by `QKDAppService`:

- `RegisterApp(QKDApp)`: Registers a new QKD application.
- `ListApps(ContextId)`: Lists all QKD apps in a specific context.
- `GetApp(QKDAppId)`: Retrieves details for a specific application.
- `DeleteApp(QKDAppId)`: Removes a QKD application.
