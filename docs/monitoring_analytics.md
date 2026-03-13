# Monitoring and Analytics Suite

TeraFlowSDN (TFS) features a robust monitoring and analytics suite designed to provide real-time visibility into network performance and enable data-driven automation. This suite consists of the `monitoring` and `analytics` microservices.

## 1. Monitoring Service

The Monitoring Service is responsible for collecting, storing, and retrieving telemetry data from network devices and services.

### Core Features
- **Telemetry Collection**: Supports multiple protocols (gRPC, gNMI, SNMP) via device drivers.
- **KPI Management**: Defines and manages Key Performance Indicators (KPIs) such as packet loss, delay, and throughput.
- **Alarm Management**: Allows users to set thresholds on KPIs to trigger alarms.
- **Persistent Storage**: Integrates with InfluxDB for time-series data storage.

### Integration
- **Grafana**: Telemetry data can be visualized in Grafana dashboards.
- **Automation Service**: Alarms can trigger automated remediation workflows.

## 2. Analytics Service

The Analytics Service provides advanced data processing capabilities, including real-time stream analysis and forecasting.

### Core Features
- **Real-time Stream Processing**: Leverages Apache Spark Streaming for high-throughput data analysis.
- **Analyzer Framework**: Allows users to define custom "Analyzers" to process specific KPI streams.
- **Frontend/Backend Split**:
    - **Frontend**: Provides gRPC API for managing Analyzer lifecycle (`ListAnalyzers`, `GetAnalyzer`, `DeleteAnalyzer`).
    - **Backend**: Executes the stream processing logic and interacts with the monitoring database.
- **Machine Learning**: (In development) Support for integrating ML models for predictive maintenance and forecasting.

## Common Workflows

### Setting up a Dashboard
1.  **Onboarding**: Device is added with specific KPI targets.
2.  **Sampling**: Monitoring Service starts collecting telemetry samples.
3.  **Storage**: Samples are pushed to InfluxDB.
4.  **Visualization**: Grafana queries InfluxDB to display real-time graphs.

### Creating an Analyzer
1.  **Request**: User creates an Analyzer via the Analytics Frontend.
2.  **Selection**: The Backend selects the relevant KPI stream from Monitoring.
3.  **Processing**: Spark Streaming applies the requested logic (e.g., averaging, anomaly detection).
4.  **Reporting**: Results are written back to the database or used to trigger alarms.

## Usage (gRPC)

Key RPC methods provided by `AnalyticsFrontendService`:
- `CreateAnalyzer(Analyzer)`: Initializes a new analytics job.
- `GetAnalyzer(AnalyzerId)`: Retrieves the status and results of an analyzer.
- `ListAnalyzers(Empty)`: Lists all active and historical analyzers.
