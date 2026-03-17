import json, os, uuid, time, sys, grpc, requests
from common.proto.context_pb2 import Context, ContextId, Topology, TopologyId, Empty, Device, Link, Service, Slice, DeviceOperationalStatusEnum, OpticalLink, OpticalLinkDetails, DeviceId, LinkId
from context.client.ContextClient import ContextClient
from google.protobuf.json_format import ParseDict

# Required for QKD App registration
sys.path.append('/var/teraflow')
from common.proto.qkd_app_pb2 import App
from common.proto.qkd_app_pb2_grpc import AppServiceStub

NAMESPACE_TFS = uuid.UUID("200e3a1f-2223-534f-a100-758e29c37f40")

def fix_config_rules(obj):
    if not isinstance(obj, dict): return
    if 'config_rules' in obj:
        for rule in obj['config_rules']:
            if 'custom' in rule and 'resource_key' in rule['custom'] and 'resource_value' in rule['custom']:
                val = rule['custom']['resource_value']
                if not isinstance(val, (str, bytes)):
                    rule['custom']['resource_value'] = json.dumps(val)
    for k, v in obj.items():
        if isinstance(v, dict): fix_config_rules(v)
        elif isinstance(v, list):
            for item in v: fix_config_rules(item)

def ensure_slots(details):
    # Bug fix for bin_num="0b" in Slot.py
    for band in ['c_slots', 'l_slots', 's_slots']:
        if not details.get(band):
            details[band] = {str(i): 0 for i in range(1, 21)}

def restore():
    c = ContextClient()
    c.connect()
    
    ctx_uuid = '43813baf-195e-5da6-af20-b3d0922e71a7'
    topo_uuid = 'c76135e3-24a8-5e92-9bed-c3c9139359c8'
    ctx_id = ContextId(context_uuid={'uuid': ctx_uuid})

    print("--- STARTING ZERO-STATE WIPE ---")
    for attempt in range(2):
        for s in c.ListSlices(ctx_id).slices:
            try: c.RemoveSlice(s.slice_id); print(f"Removed Slice {s.slice_id.slice_uuid.uuid}")
            except: pass
        for s in c.ListServices(ctx_id).services:
            try: c.RemoveService(s.service_id); print(f"Removed Service {s.service_id.service_uuid.uuid}")
            except: pass
        for l in c.ListLinks(Empty()).links:
            try: c.RemoveLink(l.link_id); print(f"Removed Link {l.link_id.link_uuid.uuid}")
            except: pass
        for d in c.ListDevices(Empty()).devices:
            try: c.RemoveDevice(d.device_id); print(f"Removed Device {d.device_id.device_uuid.uuid}")
            except: pass
    
    print("--- RESTORING ENRICHED CLEAN TOPOLOGY ---")
    filename = '/tmp/SuperDescriptor_Ready_v4.json'
    if not os.path.exists(filename): filename = '/tmp/SuperDescriptor_Ready_v3.json'
    with open(filename, 'r') as f: data = json.load(f)

    # 1. Context & Topology
    c.SetContext(ParseDict({'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'name': 'admin'}, Context()))
    c.SetTopology(ParseDict({'topology_id': {'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'topology_uuid': {'uuid': topo_uuid}}, 'name': 'admin'}, Topology()))

    # 2. Devices
    all_dev_ids = []
    for dev in data.get('devices', []):
        name = dev.get('name', dev['device_id']['device_uuid']['uuid'])
        dev_uuid = str(uuid.uuid5(NAMESPACE_TFS, name))
        dev['device_id']['device_uuid']['uuid'] = dev_uuid
        dev['name'] = name
        fix_config_rules(dev)
        for ep in dev.get('device_endpoints', []):
            ep['endpoint_id']['device_id']['device_uuid']['uuid'] = dev_uuid
            ep_id = ep['endpoint_id']['endpoint_uuid']['uuid']
            # We use name if available, otherwise UUID
            ep['endpoint_id']['endpoint_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{dev_uuid}/{ep_id}"))

        dev['device_operational_status'] = 2
        c.SetDevice(ParseDict(dev, Device()))
        all_dev_ids.append(ParseDict(dev['device_id'], DeviceId()))
        print(f"Device {name} set.")

    # 3. Links
    all_link_ids = []
    for link in data.get('links', []):
        name = link.get('name', link['link_id']['link_uuid']['uuid'])
        link_uuid = str(uuid.uuid5(NAMESPACE_TFS, name))
        link['link_id']['link_uuid']['uuid'] = link_uuid
        link['name'] = name
        
        for ep_id in link.get('link_endpoint_ids', []):
            d_name = ep_id['device_id']['device_uuid']['uuid']
            d_hash = str(uuid.uuid5(NAMESPACE_TFS, d_name))
            ep_id['device_id']['device_uuid']['uuid'] = d_hash
            ep_id['endpoint_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{d_hash}/{ep_id['endpoint_uuid']['uuid']}"))
        
        if 'optical_details' in link:
            ensure_slots(link['optical_details'])
            try:
                c.SetOpticalLink(ParseDict(link, OpticalLink()))
                print(f"Optical Link {name} set.")
            except Exception as e:
                print(f"Failed SetOpticalLink {name}: {e}. Falling back to SetLink.")
                link.pop('optical_details')
                c.SetLink(ParseDict(link, Link()))
        else:
            c.SetLink(ParseDict(link, Link()))
            print(f"Link {name} set.")
        
        all_link_ids.append(ParseDict(link['link_id'], LinkId()))

    # 4. Topology Update
    final_topo = Topology()
    final_topo.topology_id.context_id.context_uuid.uuid = ctx_uuid
    final_topo.topology_id.topology_uuid.uuid = topo_uuid
    final_topo.name = 'admin'
    final_topo.device_ids.extend(all_dev_ids)
    final_topo.link_ids.extend(all_link_ids)
    c.SetTopology(final_topo)

    # 5. Services & Slices
    for svc in data.get('services', []):
        name = svc.get('name', svc['service_id']['service_uuid']['uuid'])
        svc['service_id']['service_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, name))
        svc['name'] = name
        svc['service_id']['context_id'] = {'context_uuid': {'uuid': ctx_uuid}}
        fix_config_rules(svc)
        for ep_id in svc.get('service_endpoint_ids', []):
             ep_id.pop('topology_id', None)
             d_hash = str(uuid.uuid5(NAMESPACE_TFS, ep_id['device_id']['device_uuid']['uuid']))
             ep_id['device_id']['device_uuid']['uuid'] = d_hash
             ep_id['endpoint_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{d_hash}/{ep_id['endpoint_uuid']['uuid']}"))
        c.SetService(ParseDict(svc, Service()))
        print(f"Service {name} set.")

    for slc in data.get('slices', []):
        name = slc.get('name', slc['slice_id']['slice_uuid']['uuid'])
        slc['slice_id']['slice_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, name))
        slc['name'] = name
        slc['slice_id']['context_id'] = {'context_uuid': {'uuid': ctx_uuid}}
        fix_config_rules(slc)
        for ep_id in slc.get('slice_endpoint_ids', []):
             ep_id.pop('topology_id', None)
             d_hash = str(uuid.uuid5(NAMESPACE_TFS, ep_id['device_id']['device_uuid']['uuid']))
             ep_id['device_id']['device_uuid']['uuid'] = d_hash
             ep_id['endpoint_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{d_hash}/{ep_id['endpoint_uuid']['uuid']}"))
        c.SetSlice(ParseDict(slc, Slice()))
        print(f"Slice {name} set.")

    # 6. QKD Apps Registration
    print("--- REGISTERING QKD APPS ---")
    app_channel = grpc.insecure_channel('127.0.0.1:10070')
    app_stub = AppServiceStub(app_channel)
    
    def reg_app(name, local_dev, remote_dev):
        a = App()
        a.app_id.context_id.context_uuid.uuid = ctx_uuid
        a.app_id.app_uuid.uuid = name
        a.app_status = 1 # ON
        a.app_type = 0   # QKDAPPTYPES_INTERNAL
        a.local_device_id.device_uuid.uuid = str(uuid.uuid5(NAMESPACE_TFS, local_dev))
        a.remote_device_id.device_uuid.uuid = str(uuid.uuid5(NAMESPACE_TFS, remote_dev))
        try: app_stub.RegisterApp(a); print(f"Registered QKD App {name}")
        except Exception as e: print(f"Failed to register QKD App {name}: {e}")

    reg_app('APP-QKD-01', 'GKE-QKD-NODE-01', 'GKE-QKD-NODE-02')
    reg_app('APP-QKD-02', 'GKE-QKD-NODE-02', 'GKE-QKD-NODE-01')

    print("--- REFRESHING OPTICAL CONTROLLER ---")
    try:
        url = f"http://127.0.0.1:10060/OpticalTFS/GetTopology/{ctx_uuid}/{topo_uuid}"
        requests.get(url)
        print("Optical Controller topology refreshed.")
    except Exception as e:
        print(f"Failed to refresh Optical Controller: {e}")

    print("Restoration complete.")
    c.close()

if __name__ == "__main__":
    restore()
