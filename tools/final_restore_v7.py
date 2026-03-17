import json, os, uuid, time, sys, grpc, requests
from common.proto.context_pb2 import Context, ContextId, Topology, TopologyId, Empty, Device, Link, Service, Slice, DeviceOperationalStatusEnum, OpticalLink, OpticalLinkDetails, DeviceId, LinkId, ServiceTypeEnum, ServiceId, SliceId, OpticalConfig
from context.client.ContextClient import ContextClient
from google.protobuf.json_format import ParseDict

# Required for QKD App registration
sys.path.append('/var/teraflow')
from common.proto.qkd_app_pb2 import App
from common.proto.qkd_app_pb2_grpc import AppServiceStub

NAMESPACE_TFS = uuid.UUID("200e3a1f-2223-534f-a100-758e29c37f40")

# Device types for OpticalConfig
OPTICAL_ROADM_TYPES = {"optical-roadm", "emu-optical-roadm", "EMULATED_OPEN_ROADM"}
OPTICAL_TRANSPONDER_TYPES = {"optical-transponder", "emu-optical-transponder"}

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
    # Multiple attempts to handle dependencies
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
    
    # Also wipe OpticalConfigs
    try:
        cfgs = c.GetOpticalConfig(Empty())
        for cfg in cfgs.opticalconfigs:
            try: c.DeleteOpticalConfig(cfg.opticalconfig_id); print(f"Removed OpticalConfig {cfg.opticalconfig_id.opticalconfig_uuid}")
            except: pass
    except: pass

    print("--- RESTORING ENRICHED CLEAN TOPOLOGY ---")
    filename = '/tmp/SuperDescriptor_Ready_v4.json'
    with open(filename, 'r') as f: data = json.load(f)

    # Deduplicate devices by name (favoring non-empty ones)
    unique_devices = {}
    for dev in data.get('devices', []):
        name = dev.get('name', dev['device_id']['device_uuid']['uuid'])
        if name not in unique_devices or len(dev.get('device_endpoints', [])) > len(unique_devices[name].get('device_endpoints', [])):
            unique_devices[name] = dev
    processed_devices = list(unique_devices.values())

    # 1. Context & Topology
    c.SetContext(ParseDict({'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'name': 'admin'}, Context()))
    c.SetTopology(ParseDict({'topology_id': {'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'topology_uuid': {'uuid': topo_uuid}}, 'name': 'admin'}, Topology()))

    # 2. Devices & OpticalConfigs
    all_dev_ids = []
    for dev in processed_devices:
        name = dev.get('name', dev['device_id']['device_uuid']['uuid'])
        dev_uuid = str(uuid.uuid5(NAMESPACE_TFS, name))
        dev['device_id']['device_uuid']['uuid'] = dev_uuid
        dev['name'] = name
        fix_config_rules(dev)
        for ep in dev.get('device_endpoints', []):
            ep['endpoint_id']['device_id']['device_uuid']['uuid'] = dev_uuid
            ep_id = ep['endpoint_id']['endpoint_uuid']['uuid']
            ep['endpoint_id']['endpoint_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{dev_uuid}/{ep_id}"))

        dev['device_operational_status'] = 2
        c.SetDevice(ParseDict(dev, Device()))
        all_dev_ids.append(ParseDict(dev['device_id'], DeviceId()))

        # Generate OpticalConfig for optical nodes
        d_type = dev.get('device_type', '')
        if d_type in OPTICAL_ROADM_TYPES or d_type in OPTICAL_TRANSPONDER_TYPES:
            print(f"Generating OpticalConfig for {name}")
            oc = OpticalConfig()
            oc.opticalconfig_id.opticalconfig_uuid = dev_uuid # Use device UUID for simple mapping
            oc.device_id.device_uuid.uuid = dev_uuid
            
            # Simple mock config JSON for WebUI
            cfg_dict = {
                "device_name": name,
                "type": "optical-roadm" if d_type in OPTICAL_ROADM_TYPES else "optical-transponder",
                "channels": [
                    {
                        "name": {"index": "channel-1"},
                        "frequency": 193100,
                        "target-output-power": "-5.0",
                        "operational-mode": 1,
                        "status": "ENABLED",
                        "band_name": "C-band"
                    }
                ],
                "transceivers": {"transceiver": ["t1", "t2"]}
            }
            oc.config = json.dumps(cfg_dict)
            c.SetOpticalConfig(oc)

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
            except Exception as e:
                print(f"Failed SetOpticalLink {name}: {e}. Falling back to SetLink.")
                link.pop('optical_details')
                c.SetLink(ParseDict(link, Link()))
        else:
            c.SetLink(ParseDict(link, Link()))
        
        all_link_ids.append(ParseDict(link['link_id'], LinkId()))

    # 4. Topology Update
    final_topo = Topology()
    final_topo.topology_id.context_id.context_uuid.uuid = ctx_uuid
    final_topo.topology_id.topology_uuid.uuid = topo_uuid
    final_topo.name = 'admin'
    final_topo.device_ids.extend(all_dev_ids)
    final_topo.link_ids.extend(all_link_ids)
    c.SetTopology(final_topo)

    # 5. Multilayer Semantic Services
    all_svc_ids = []
    
    def create_svc(name, svc_type, endpoints):
        svc_uuid = str(uuid.uuid5(NAMESPACE_TFS, name))
        svc_dict = {
            'service_id': {
                'context_id': {'context_uuid': {'uuid': ctx_uuid}},
                'service_uuid': {'uuid': svc_uuid}
            },
            'name': name,
            'service_type': svc_type,
            'service_endpoint_ids': [],
            'service_config': {'config_rules': []}
        }
        for dev_name, ep_name in endpoints:
            d_hash = str(uuid.uuid5(NAMESPACE_TFS, dev_name))
            svc_dict['service_endpoint_ids'].append({
                'device_id': {'device_uuid': {'uuid': d_hash}},
                'endpoint_uuid': {'uuid': str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{d_hash}/{ep_name}"))}
            })
        
        # Add a placeholder QKD security constraint
        if "SECURED" in name:
            svc_dict['service_config']['config_rules'].append({
                'action': 1, # SET
                'custom': {
                    'resource_key': '/settings/security',
                    'resource_value': 'QKD-quantum-hardened'
                }
            })

        c.SetService(ParseDict(svc_dict, Service()))
        print(f"Service {name} set.")
        return ParseDict(svc_dict['service_id'], ServiceId())

    # L2 Secured over QKD
    svc_l2 = create_svc("SVC-QKD-SECURED-L2", ServiceTypeEnum.SERVICETYPE_L2NM, [("GKE-PE-L3-01", "1/1"), ("GKE-PE-L3-02", "1/1")])
    # L3 Secured over QKD
    svc_l3 = create_svc("SVC-QKD-SECURED-L3", ServiceTypeEnum.SERVICETYPE_L3NM, [("GKE-RTR-L3-001", "Ethernet10"), ("GKE-RTR-L3-149", "eth-1/0/9")])
    # Core QKD Service
    svc_qkd = create_svc("SVC-QKD-CORE-01", ServiceTypeEnum.SERVICETYPE_QKD, [("GKE-QKD-NODE-01", "LINE"), ("GKE-QKD-NODE-02", "LINE")])
    
    all_svc_ids = [svc_l2, svc_l3, svc_qkd]

    # 6. Master Network Slice
    slice_name = "SLICE-QUANTUM-MULTILAYER"
    slc = Slice()
    slc.slice_id.context_id.context_uuid.uuid = ctx_uuid
    slc.slice_id.slice_uuid.uuid = str(uuid.uuid5(NAMESPACE_TFS, slice_name))
    slc.name = slice_name
    slc.slice_service_ids.extend(all_svc_ids)
    for sid in all_svc_ids:
        svc = c.GetService(sid)
        slc.slice_endpoint_ids.extend(svc.service_endpoint_ids)
    
    c.SetSlice(slc)
    print(f"Slice {slice_name} set.")

    # 7. QKD Apps Registration
    print("--- REGISTERING QKD APPS ---")
    app_channel = grpc.insecure_channel('127.0.0.1:10070')
    app_stub = AppServiceStub(app_channel)
    def reg_app(name, local_dev, remote_dev):
        a = App()
        a.app_id.context_id.context_uuid.uuid = ctx_uuid
        a.app_id.app_uuid.uuid = name
        a.app_status = 1 
        a.app_type = 0   
        a.local_device_id.device_uuid.uuid = str(uuid.uuid5(NAMESPACE_TFS, local_dev))
        a.remote_device_id.device_uuid.uuid = str(uuid.uuid5(NAMESPACE_TFS, remote_dev))
        try: app_stub.RegisterApp(a); print(f"Registered QKD App {name}")
        except: pass
    reg_app('APP-QKD-01', 'GKE-QKD-NODE-01', 'GKE-QKD-NODE-02')
    reg_app('APP-QKD-02', 'GKE-QKD-NODE-02', 'GKE-QKD-NODE-01')

    print("--- REFRESHING OPTICAL CONTROLLER & ADDING LIGHTPATHS ---")
    base_url = "http://127.0.0.1:10060/OpticalTFS"
    try:
        requests.get(f"{base_url}/GetTopology/{ctx_uuid}/{topo_uuid}")
        print("Optical Controller topology refreshed.")
        
        # Trigger sample lightpaths to populate Light Paths and Bands
        # Format: /AddLightpath/<src>/<dst>/<bitrate>/<bidir>
        print("Adding sample lightpaths...")
        lp1 = requests.put(f"{base_url}/AddLightpath/GKE-OPT-ROAD-01/GKE-OPT-ROAD-02/100/1")
        print(f"LP1: {lp1.status_code}")
        lp2 = requests.put(f"{base_url}/AddFlexLightpath/GKE-OPT-LEAF-01/GKE-OPT-LEAF-02/40/1")
        print(f"LP2: {lp2.status_code}")
    except Exception as e:
        print(f"Failed to populate OpticalController: {e}")

    print("Restoration v7 complete.")
    c.close()

if __name__ == "__main__":
    restore()
