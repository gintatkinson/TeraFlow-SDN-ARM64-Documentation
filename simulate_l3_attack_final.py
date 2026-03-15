import sys
import os

# Add TeraFlow root to path
sys.path.append('/var/teraflow')

import grpc
import logging
from common.proto.l3_centralizedattackdetector_pb2 import L3CentralizedattackdetectorMetrics, Feature, ConnectionMetadata
from l3_centralizedattackdetector.client.l3_centralizedattackdetectorClient import l3_centralizedattackdetectorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def simulate_attack():
    cad_client = l3_centralizedattackdetectorClient(address='l3-centralizedattackdetectorservice', port=10001)

    metrics = L3CentralizedattackdetectorMetrics()
    metrics.connection_metadata.ip_o = "10.0.0.1"
    metrics.connection_metadata.ip_d = "192.168.1.100"
    metrics.connection_metadata.port_o = "443"
    metrics.connection_metadata.port_d = "80"
    metrics.connection_metadata.flow_id = "attack-flow-001"
    metrics.connection_metadata.protocol = "TCP"
    metrics.connection_metadata.time_start = 0.0
    metrics.connection_metadata.time_end = 10.0

    # These features are based on the ONNX model expectations in the CAD component
    # n_packets_server_seconds, n_packets_client_seconds, n_bits_server_seconds, n_bits_client_seconds, ...
    for val in [100.0, 100.0, 5000.0, 5000.0, 50.0, 50.0, 1.0, 1.0]:
        f = metrics.features.add()
        f.feature = val

    LOGGER.info("Sending attack simulation metrics to Centralized Attack Detector...")
    try:
        response = cad_client.AnalyzeConnectionStatistics(metrics)
        LOGGER.info(f"Response from CAD: {response.message}")
    except Exception as e:
        LOGGER.error(f"Failed to communicate with CAD: {e}")
    finally:
        cad_client.close()

if __name__ == "__main__":
    simulate_attack()
