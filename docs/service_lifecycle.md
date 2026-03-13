# TeraFlowSDN Service Lifecycle & Orchestration

This document details the internal lifecycle of a network service within TeraFlowSDN, focusing on how the `Service` microservice orchestrates fulfillment via the `TasksScheduler`.

## Service States

The `ServiceStatusEnum` defines the following states for a service:

1. **`SERVICESTATUS_PLANNED`**: Initial state after creation. The service is being analyzed and paths are being computed.
2. **`SERVICESTATUS_ACTIVE`**: The service has been successfully provisioned on the network hardware.
3. **`SERVICESTATUS_UPDATING`**: An existing service is being modified (e.g., path recomputation, constraint updates).
4. **`SERVICESTATUS_PENDING_REMOVAL`**: The service is slated for deletion; hardware configuration removal is in progress.
5. **`SERVICESTATUS_SLA_VIOLATED`**: Deployment was successful, but real-time monitoring indicates SLA constraints (e.g., latency) are not being met.

## The Orchestration Flow

When a service is created or updated, the following internal sequence occurs:

### 1. Request Handling
The `ServiceServiceServicerImpl` receives the gRPC request. This can be triggered by:
- **NBI/WebUI**: Direct manual requests.
- **ZTP (Zero-Touch Provisioning)**: Automatically when a new device is discovered.
- **Automation Service**: Based on event-driven logic or higher-level orchestration.
- **L3/Optical Mitigators**: In response to security threats.

The servicer first validates the request and ensures no conflicting service IDs exist.

### 2. Path Computation
If the request requires path orchestration, `Service` calls the `PathComp` microservice. `PathComp` uses the topology data from `Context` to return a list of path hops (links and devices) and the necessary configurations.

### 3. Task DAG Composition
This is the core of the orchestration logic handled by `TasksScheduler`. It builds a **Directed Acyclic Graph (DAG)** of tasks to ensure correct ordering:

- **Service Set Status (PLANNED)**: Marks the start of the operation.
- **Connection Configuration**: For each hop in the path, a task is created to configure the respective devices.
- **Sub-Service Configuration**: If the service spans multiple domains, sub-tasks are created for lower-level controllers.
- **Service Set Status (ACTIVE)**: Marks the final success.

### 4. Task Execution
The `TaskExecutor` iterates through the DAG in topological order. For each task:
- It selects the appropriate **Service Handler** based on the device type and driver.
- The Service Handler translates abstract connection requirements into device-specific configuration rules.
- The `Device` microservice is called to apply these rules via southbound drivers (OpenConfig, P4, etc.).

## Error Handling & Rollback

- **Task Failure**: If a task fails, the `TasksScheduler` halts execution. 
- **State Persistence**: Every state change and task result is logged in the `Context` service to allow for recovery or manual intervention.
- **Rollback**: (Implementation varies) Generally, if a critical failure occurs during configuration, the system attempts to revert previously applied settings to prevent partial/inconsistent network states.

## Key Classes
- `ServiceServiceServicerImpl.py`: The gRPC entry point.
- `TasksScheduler.py`: Logic for building the task graph.
- `TaskExecutor.py`: Logic for running tasks and managing cache.
- `ServiceHandlerFactory.py`: Logic for selecting the correct driver-specific handler.
