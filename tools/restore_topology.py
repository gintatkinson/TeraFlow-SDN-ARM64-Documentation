import json, os, uuid
from common.proto.context_pb2 import Context, ContextId, Topology, TopologyId, Empty, Device, Link, Service, Slice, DeviceOperationalStatusEnum, OpticalLink, OpticalLinkDetails, DeviceId, LinkId
from context.client.ContextClient import ContextClient
from google.protobuf.json_format import ParseDict

# Standard TFS Namespace for name-to-UUID hashing
NAMESPACE_TFS = uuid.UUID("200e3a1f-2223-534f-a100-758e29c37f40")

# Deterministic UUID generation helper
# Direct semantic ID mapping (no hashing for GKE/SVC/SLICE/NODE)
def get_uuid(name):
    if not name: return str(uuid.uuid4())
    # If it is already a UUID or is a semantic name, return it directly
    name_str = str(name)
    if name_str.startswith(('GKE-', 'SVC-', 'SLICE-', 'NODE-')):
        return name_str
    try:
        uuid.UUID(name_str)
        return name_str
    except:
        return str(uuid.uuid5(NAMESPACE_TFS, name_str))

def restore():
    print("Starting high-speed Context-Direct topology restoration...")
    ctx_client = ContextClient()
    
    # Hardcoded GKE-native UUIDs (Server-side constraints)
    ctx_uuid = '43813baf-195e-5da6-af20-b3d0922e71a7'  # TFS NAMESPACE hash of 'admin'
    topo_uuid = 'c76135e3-24a8-5e92-9bed-c3c9139359c8' # Hardcoded in GKE test logic
    print(f"Using GKE-Native Context UUID: {ctx_uuid}, Topology UUID: {topo_uuid}")

    filename = 'SuperDescriptor_Final.json'
    if not os.path.exists(filename):
        filename = 'SuperDescriptor_Enriched.json'

    with open(filename, 'r') as f:
        data = json.load(f)

    def map_endpoint_id(eid):
        if not eid: return
        eid['topology_id'] = {
            'context_id': {'context_uuid': {'uuid': ctx_uuid}},
            'topology_uuid': {'uuid': topo_uuid}
        }
        raw_dev_id = eid['device_id']['device_uuid']['uuid']
        eid['device_id']['device_uuid']['uuid'] = get_uuid(raw_dev_id)
        dev_uuid = eid['device_id']['device_uuid']['uuid']
        ep_name = eid['endpoint_uuid']['uuid']
        try:
            uuid.UUID(ep_name)
        except:
            eid['endpoint_uuid']['uuid'] = get_uuid(f"{topo_uuid}/{dev_uuid}/{ep_name}")

    def prepare_object(obj):
        if not isinstance(obj, dict): return
        if 'context_id' in obj:
            obj['context_id'] = {'context_uuid': {'uuid': ctx_uuid}}
        if 'topology_ids' in obj:
            obj['topology_ids'] = [{'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'topology_uuid': {'uuid': topo_uuid}}]
        if 'topology_id' in obj:
            obj['topology_id'] = {'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'topology_uuid': {'uuid': topo_uuid}}
        if 'device_id' in obj and 'device_uuid' in obj['device_id']:
            obj['device_id']['device_uuid']['uuid'] = get_uuid(obj['device_id']['device_uuid']['uuid'])
        if 'endpoint_id' in obj:
            map_endpoint_id(obj['endpoint_id'])
        if 'link_id' in obj:
            obj['link_id']['link_uuid']['uuid'] = get_uuid(obj['link_id']['link_uuid']['uuid'])
        if 'service_id' in obj:
            obj['service_id']['service_uuid']['uuid'] = get_uuid(obj['service_id']['service_uuid']['uuid'])
        if 'slice_id' in obj:
            obj['slice_id']['slice_uuid']['uuid'] = get_uuid(obj['slice_id']['slice_uuid']['uuid'])

        if 'config_rules' in obj:
            for rule in obj['config_rules']:
                if 'custom' in rule:
                    prepare_object(rule['custom'])
                    if 'resource_value' in rule['custom']:
                        val = rule['custom']['resource_value']
                        if not isinstance(val, (str, bytes)):
                            rule['custom']['resource_value'] = json.dumps(val)

        for k, v in obj.items():
            if k in ['endpoint_ids', 'link_endpoint_ids', 'service_endpoint_ids', 'slice_endpoint_ids', 'device_endpoints'] and isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        if 'endpoint_id' in item: map_endpoint_id(item['endpoint_id'])
                        else: map_endpoint_id(item)
            elif isinstance(v, (dict, list)):
                if isinstance(v, list):
                    for i in v: prepare_object(i)
                else: prepare_object(v)

    # 1. Context & Topology
    try:
        ctx_client.SetContext(ParseDict({'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'name': 'admin'}, Context()))
        ctx_client.SetTopology(ParseDict({'topology_id': {'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'topology_uuid': {'uuid': topo_uuid}}, 'name': 'admin'}, Topology()))
    except Exception as e: print(f"Warning setting context/topology: {e}")

    # 2. Devices
    print("Injecting devices...")
    all_dev_ids = []
    for dev in data.get('devices', []):
        orig_id = dev['device_id']['device_uuid']['uuid']
        try:
            prepare_object(dev)
            dev['device_operational_status'] = 2
            dev_proto = ParseDict(dev, Device())
            ctx_client.SetDevice(dev_proto)
            all_dev_ids.append(dev_proto.device_id)
            print(f"Device {orig_id} -> {dev['device_id']['device_uuid']['uuid']} set.")
        except Exception as e: print(f"Error device {orig_id}: {e}")

    # 3. Links
    print("Injecting links...")
    all_link_ids = []
    for link in data.get('links', []):
        try:
            prepare_object(link)
            if not link.get('name'): link['name'] = link['link_id']['link_uuid']['uuid']
            if 'optical_details' in link:
                ctx_client.SetOpticalLink(ParseDict(link, OpticalLink()))
            else:
                ctx_client.SetLink(ParseDict(link, Link()))
            all_link_ids.append(ParseDict(link['link_id'], LinkId()))
            print(f"Link {link['link_id']['link_uuid']['uuid']} set.")
        except Exception as e: print(f"Error link: {e}")

    # 4. Topology Details Update
    print(f"Assigning {len(all_dev_ids)} devices and {len(all_link_ids)} links to Topology {topo_uuid}...")
    final_topo = Topology()
    final_topo.topology_id.context_id.context_uuid.uuid = ctx_uuid
    final_topo.topology_id.topology_uuid.uuid = topo_uuid
    final_topo.name = 'admin'
    final_topo.device_ids.extend(all_dev_ids)
    final_topo.link_ids.extend(all_link_ids)
    ctx_client.SetTopology(final_topo)

    # 5. Services & Slices
    print("Injecting services & slices...")
    for svc in data.get('services', []):
        try:
            prepare_object(svc)
            if not svc.get('name'): svc['name'] = svc['service_id']['service_uuid']['uuid']
            ctx_client.SetService(ParseDict(svc, Service()))
        except Exception as e: print(f"Error service: {e}")
    for slc in data.get('slices', []):
        try:
            prepare_object(slc)
            ctx_client.SetSlice(ParseDict(slc, Slice()))
        except Exception as e: print(f"Error slice: {e}")

    print("Restoration complete.")
    
    # Sync Optical Controller
    import requests
    try:
        url = f"http://opticalcontrollerservice:10060/OpticalTFS/GetTopology/{ctx_uuid}/{topo_uuid}"
        resp = requests.get(url)
        print(f"Optical Sync: {resp.status_code}, {resp.text}")
    except Exception as e: print(f"Warning: Could not sync Optical Controller: {e}")

if __name__ == "__main__":
    restore()
