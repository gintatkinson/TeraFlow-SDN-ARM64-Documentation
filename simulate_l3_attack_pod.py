import sys
import os

# Add TeraFlow root to path
sys.path.append('/var/teraflow')

import grpc
import logging
from common.proto.l3_centralizedattackdetector_pb2 import ModelInput
from l3_centralizedattackdetector.client.l3_centralizedattackdetectorClient import l3_centralizedattackdetectorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def simulate_attack():
    # Centralized Attack Detector Address (internal service name)
    cad_client = l3_centralizedattackdetectorClient(address='l3-centralizedattackdetectorservice', port=10001)

    # Simulated features for a Cryptomining attack
    attack_features = {
        "n_packets_server_seconds": 100.0,
        "n_packets_client_seconds": 100.0,
        "n_bits_server_seconds": 5000.0,
        "n_bits_client_seconds": 5000.0,
        "n_bits_server_n_packets_server": 50.0,
        "n_bits_client_n_packets_client": 50.0,
        "n_packets_server_n_packets_client": 1.0,
        "n_bits_server_n_bits_client": 1.0,
        "ip_o": "10.0.0.1",
        "port_o": "443",
        "ip_d": "192.168.1.100",
        "port_d": "80",
        "flow_id": "attack-flow-001",
        "protocol": "TCP",
        "time_start": 0.0,
        "time_end": 10.0,
    }

    LOGGER.info("Sending attack simulation input to Centralized Attack Detector...")
    try:
        # Note: AnalyzeConnectionStatistics might be the RPC to call
        # Let's check the PB2 or use a generic send
        from common.proto.l3_centralizedattackdetector_pb2 import L3CentralizedattackdetectorMetrics, AutoFeatures, ConnectionMetadata
        
        metrics = L3CentralizedattackdetectorMetrics()
        metrics.connection_metadata.ip_o = "10.0.0.1"
        metrics.connection_metadata.ip_d = "192.168.1.100"
        metrics.connection_metadata.port_o = "443"
        metrics.connection_metadata.port_d = "80"
        metrics.connection_metadata.flow_id = "attack-flow-001"
        metrics.connection_metadata.protocol = "TCP"
        
        # Add features (centralized attack detector expects a list of features)
        # Based on l3_centralizedattackdetectorServiceServicerImpl.py
        for val in [100.0, 100.0, 5000.0, 5000.0, 50.0, 50.0, 1.0, 1.0]:
            f = metrics.features.add()
            f.feature = val

        response = cad_client.AnalyzeConnectionStatistics(metrics)
        LOGGER.info(f"Response from CAD: {response.message}")
    except Exception as e:
        LOGGER.error(f"Failed to communicate with CAD: {e}")
    finally:
        cad_client.close()

if __name__ == "__main__":
    simulate_attack()
