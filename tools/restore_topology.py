import json, time, os
from common.proto.context_pb2 import Context, ContextId, Topology, TopologyId, Empty, Device, Link
from context.client.ContextClient import ContextClient
from device.client.DeviceClient import DeviceClient
from google.protobuf.json_format import ParseDict

def restore():
    print("Starting direct topology restoration with ResourceValue Fix...")
    ctx_client = ContextClient()
    dev_client = DeviceClient()
    
    with open('/home/ubuntu/SuperDescriptor.json', 'r') as f:
        data = json.load(f)

    # 1. Ensure Context
    for ctx in data.get('contexts', []):
        try:
            ctx_client.SetContext(ParseDict(ctx, Context()))
            print(f"Context {ctx['context_id']['context_uuid']['uuid']} set.")
        except Exception as e:
            print(f"Error setting context: {e}")

    # 2. Ensure Topologies
    for topo in data.get('topologies', []):
        try:
            ctx_client.SetTopology(ParseDict(topo, Topology()))
            print(f"Topology {topo['topology_id']['topology_uuid']['uuid']} set.")
        except Exception as e:
            print(f"Error setting topology: {e}")

    # 3. Add Devices
    for dev in data.get('devices', []):
        uuid = dev['device_id']['device_uuid']['uuid']
        try:
            # Fix resource_value if it's a dict/list (must be string for gRPC)
            if 'device_config' in dev and 'config_rules' in dev['device_config']:
                for rule in dev['device_config']['config_rules']:
                    if 'custom' in rule and 'resource_value' in rule['custom']:
                        val = rule['custom']['resource_value']
                        if isinstance(val, (dict, list)):
                            rule['custom']['resource_value'] = json.dumps(val)
            
            dev_client.AddDevice(ParseDict(dev, Device()))
            print(f"Device {uuid} added.")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"Device {uuid} already exists.")
            else:
                print(f"Error adding device {uuid}: {e}")

    # 4. Add Links
    for link in data.get('links', []):
        try:
            ctx_client.SetLink(ParseDict(link, Link()))
            print(f"Link {link['link_id']['link_uuid']['uuid']} set.")
        except Exception as e:
            print(f"Error setting link: {e}")

    print("Restoration complete.")

if __name__ == "__main__":
    restore()
