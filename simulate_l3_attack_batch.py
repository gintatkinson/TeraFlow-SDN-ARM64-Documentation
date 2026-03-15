import sys
import os
import time

# Add TeraFlow root to path
sys.path.append('/var/teraflow')

import grpc
import logging
from common.proto.l3_centralizedattackdetector_pb2 import L3CentralizedattackdetectorMetrics, Feature, ConnectionMetadata
from l3_centralizedattackdetector.client.l3_centralizedattackdetectorClient import l3_centralizedattackdetectorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def simulate_attack_batch(batch_size=10):
    cad_client = l3_centralizedattackdetectorClient(address='l3-centralizedattackdetectorservice', port=10001)

    for i in range(batch_size):
        metrics = L3CentralizedattackdetectorMetrics()
        metrics.connection_metadata.ip_o = f"10.0.0.{i+1}"
        metrics.connection_metadata.ip_d = "192.168.1.100"
        metrics.connection_metadata.port_o = "443"
        metrics.connection_metadata.port_d = "80"
        metrics.connection_metadata.flow_id = f"attack-flow-{i:03d}"
        metrics.connection_metadata.protocol = "TCP"
        metrics.connection_metadata.time_start = float(i)
        metrics.connection_metadata.time_end = float(i + 1)

        # Features triggering "Crypto"
        for val in [100.0, 100.0, 5000.0, 5000.0, 50.0, 50.0, 1.0, 1.0]:
            f = metrics.features.add()
            f.feature = val

        LOGGER.info(f"Sending request {i+1}/{batch_size} to CAD...")
        try:
            response = cad_client.AnalyzeConnectionStatistics(metrics)
            LOGGER.info(f"Response: {response.message}")
        except Exception as e:
            LOGGER.error(f"Failed to communicate with CAD: {e}")
            break
    
    cad_client.close()

if __name__ == "__main__":
    simulate_attack_batch()
