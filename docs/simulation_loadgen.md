# TeraFlowSDN Simulation & Load Generation

The **Load Generator** component is an integrated tool within TeraFlowSDN (TFS) designed for high-scale simulation and performance benchmarking of the controller.

## Features

- **Automated Service Orchestration**: Programmatically creates, updates, and deletes services at a specified rate.
- **Variable Load Patterns**: Configurable arrival rates (e.g., Poisson distribution) and service durations.
- **Scaling Analysis**: Used to measure the controller's latency and throughput under heavy provisioning loads.
- **WebUI Integration**: Simulations can be initiated and monitored directly from the "Load Gen" section of the WebUI.

## Simulation Flow

1. **Initialization**: The Load Generator is configured with a list of devices and endpoints from the `Context`.
2. **Service Request**: It generates a `Service` request (e.g., L2VPN) with random or pre-defined source/destination points.
3. **Fulfillment Tracking**: It tracks the time taken for the `Service` microservice to move the service from `PLANNED` to `ACTIVE`.
4. **Cleanup**: After a simulated duration, it deletes the service to free up resources.

## Usage Scenarios

- **Stress Testing**: Identifying the maximum number of concurrent services the controller can handle.
- **Feature Validation**: Testing the impact of new path computation algorithms or device drivers on overall system latency.
- **Developer Sandbox**: Quickly populating a development environment with sample services and topology data.

## Key Components
- `src/load_generator/`: Core simulation logic and gRPC service.
- `src/webui/service/load_gen/`: Web interface for controlling simulations.
