# Policy Management Service

The Policy Management Service in TeraFlowSDN (TFS) provides a framework for defining and enforcing network policies based on real-time event monitoring and predefined conditions. It enables automated remediation, traffic steering, and SLA enforcement.

## Core Features

- **Policy Definition**: Create complex rules based on gRPC-defined conditions (`PolicyRuleCondition`) and actions (`PolicyRuleAction`).
- **Reactive Enforcement**: Monitors gRPC and Kafka event streams (e.g., from Monitoring Service) to trigger policy actions.
- **Service/Device Policies**: Supports policies targeted at specific services (e.g., SLA enforcement) or devices (e.g., security hardening).
- **SLA Integration**: Automatically enforces Service Level Agreements (SLAs) by monitoring KPIs and taking corrective actions when thresholds are violated.

## Architecture

The Policy Service is a Java/Quarkus microservice that interacts with multiple components:

1.  **Policy Core**: Manages the lifecycle of policy rules.
2.  **Monitoring Gateway**: Subscribes to alarms and KPI metrics to evaluate policy conditions.
3.  **Service/Device Gateways**: Executes policy actions by interacting with the `ServiceService` and `DeviceService`.
4.  **Kafka Integration**: Listens for high-frequency alarm events for low-latency policy evaluation.

## Policy Structure

A `PolicyRule` consists of:
- **Conditions**: A set of logical checks (Numerical/Boolean operators) on KPI values.
- **Actions**: A list of tasks to execute if conditions are met (e.g., `SET_DEVICE_CONFIG`, `RECOMPUTE_PATH`).
- **State**: Tracks whether the policy is `ACTIVE`, `ENFORCED`, or `VALiDATED`.

## Usage (gRPC)

Key RPC methods provided by `PolicyService`:

- `PolicyAddService(PolicyRuleService)`: Adds a policy rule associated with a specific service.
- `PolicyAddDevice(PolicyRuleDevice)`: Adds a policy rule associated with a specific device.
- `GetPolicyService(PolicyRuleId)`: Retrieves a service policy.
- `UpdatePolicyService(PolicyRuleService)`: Modifies an existing service policy.
