# Zero-Touch Provisioning (ZTP) and Inventory

The TeraFlowSDN (TFS) Zero-Touch Provisioning (ZTP) service automates the onboarding and initial configuration of network devices. Developed using Java and the Quarkus framework, it provides a highly efficient and reactive management plane for device lifecycle.

## Core Features

- **Automated Onboarding**: Detects new devices and triggers initial configuration based on predefined roles.
- **Inventory Management**: Maintains a real-time view of device models, driver versions, and operational statuses.
- **Role-Based Configuration**: Assigns specific configurations to devices based on their `DeviceRole` (e.g., Core Router, Edge Switch).
- **KPI Monitoring Setup**: Automatically configures monitoring parameters (KPI sample types) during device discovery.

## Architecture

The ZTP service is structured as follows:

1.  **ZTP Core Service**: Java/Quarkus service handling the business logic.
2.  **Context Consumer**: Subscribes to context events to detect new or modified devices.
3.  **Device Gateway**: Interacts with the `DeviceService` to apply configurations via drivers.
4.  **Monitoring Gateway**: Interacts with the `MonitoringService` to enable telemetry collection.

## Workflow

1.  **Detection**: ZTP receives a `DeviceEvent` from the Context Service.
2.  **Validation**: ZTP checks if the device is already onboarded or requires a role.
3.  **Bootstrap**: If required, ZTP applies a baseline configuration to the device.
4.  **Finalization**: The device status is updated in the Context Service to `OPERATIONAL`.

## Usage (gRPC)

Key RPC methods provided by `ZtpService`:

- `AddDevice(DeviceId)`: Explicitly triggers ZTP onboarding for a device.
- `GetDeviceRole(DeviceId)`: Retrieves the currently assigned role for a device.
- `ConfigureDevice(DeviceId, ConfigRule)`: Manual override for ZTP-managed configuration.
