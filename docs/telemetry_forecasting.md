# TeraFlowSDN Telemetry & Forecasting Stack

TeraFlowSDN (TFS) implements a modern, high-throughput telemetry pipeline to monitor network performance and proactively predict issues.

## Telemetry Pipeline

The telemetry stack is responsible for the collection, storage, and exposure of Key Performance Indicators (KPIs).

### 1. KPI Management
- **KPI Manager**: Defines and tracks the lifecycle of performance metrics. It allows services to "subscribe" to certain types of data (e.g., packet loss, power levels).
- **KPI Value API & Writer**: Provides the ingestion layer for time-series data, ensuring it is correctly formatted and stored in the backend database.

### 2. High-Performance Processing
- **Telemetry Service**: Aggregates data from multiple sources (Devices, Services).
- **Analytics (Spark)**: Real-time stream processing of monitoring data. It can perform complex aggregations and trigger alerts when thresholds are breached.
- **Monitoring (QuestDB/InfluxDB)**: Efficient storage for historical analysis and visualization.

## Forecaster (ML-Driven Intelligence)

The **Forecaster** microservice adds a predictive layer to the telemetry stack.

### Mechanisms
- **Historical Analysis**: It pulls long-term KPI data from the `Monitoring` service.
- **Trend Prediction**: Uses Machine Learning models to forecast future values of critical metrics (e.g., bandwidth utilization).
- **Proactive Scaling**: The `Forecaster` can notify the `Automation` or `Slice` components to scale resources *before* congestion actually occurs.

## Key Components
- `src/telemetry/`: Core collection and backend integration.
- `src/kpi_manager/`: Metadata management for performance metrics.
- `src/forecaster/`: Predictive analytics engine.
- `src/analytics/`: Real-time streaming platform.
