import json, os, uuid
from common.proto.context_pb2 import Context, ContextId, Topology, TopologyId, Empty, Device, Link, Service, Slice, DeviceOperationalStatusEnum, OpticalLink, OpticalLinkDetails, DeviceId, LinkId
from context.client.ContextClient import ContextClient
from google.protobuf.json_format import ParseDict

NAMESPACE_TFS = uuid.UUID("200e3a1f-2223-534f-a100-758e29c37f40")

def fix_config_rules(obj):
    if not isinstance(obj, dict): return
    if 'config_rules' in obj:
        for rule in obj['config_rules']:
            if 'custom' in rule and 'resource_value' in rule['custom']:
                val = rule['custom']['resource_value']
                if not isinstance(val, (str, bytes)):
                    rule['custom']['resource_value'] = json.dumps(val)
    # Recurse for nested configs
    for k, v in obj.items():
        if isinstance(v, dict): fix_config_rules(v)
        elif isinstance(v, list):
            for item in v: fix_config_rules(item)

def restore():
    c = ContextClient()
    c.connect()
    
    ctx_uuid = '43813baf-195e-5da6-af20-b3d0922e71a7'
    topo_uuid = 'c76135e3-24a8-5e92-9bed-c3c9139359c8'

    print("--- SUPER WIPE ---")
    # Slices
    for s in c.ListSlices(ContextId(context_uuid={'uuid': ctx_uuid})).slices:
        try: c.RemoveSlice(s.slice_id); print(f"Removed Slice {s.slice_id.slice_uuid.uuid}")
        except: pass
    # Services
    for s in c.ListServices(ContextId(context_uuid={'uuid': ctx_uuid})).services:
        try: c.RemoveService(s.service_id); print(f"Removed Service {s.service_id.service_uuid.uuid}")
        except: pass
    # Links
    for l in c.ListLinks(Empty()).links:
        try: c.RemoveLink(l.link_id); print(f"Removed Link {l.link_id.link_uuid.uuid}")
        except: pass
    # Devices (Multi-pass wipe)
    for _ in range(2):
        for d in c.ListDevices(Empty()).devices:
            try: c.RemoveDevice(d.device_id); print(f"Removed Device {d.device_id.device_uuid.uuid}")
            except: pass

    print("--- RESTORE ---")
    filename = '/tmp/SuperDescriptor_Final.json'
    if not os.path.exists(filename): filename = '/tmp/SuperDescriptor_Final_Semantic_Enriched.json'
    with open(filename, 'r') as f: data = json.load(f)

    # 1. Context & Topology
    c.SetContext(ParseDict({'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'name': 'admin'}, Context()))
    c.SetTopology(ParseDict({'topology_id': {'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'topology_uuid': {'uuid': topo_uuid}}, 'name': 'admin'}, Topology()))

    # 2. Devices
    all_dev_ids = []
    for dev in data.get('devices', []):
        name = dev.get('name', dev['device_id']['device_uuid']['uuid'])
        dev['device_id']['device_uuid']['uuid'] = name
        dev['name'] = name
        fix_config_rules(dev)
        for ep in dev.get('device_endpoints', []):
            ep['endpoint_id']['device_id']['device_uuid']['uuid'] = name
            ep_id = ep['endpoint_id']['endpoint_uuid']['uuid']
            ep['endpoint_id']['endpoint_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{name}/{ep_id}"))

        dev['device_operational_status'] = 2
        c.SetDevice(ParseDict(dev, Device()))
        all_dev_ids.append(ParseDict(dev['device_id'], DeviceId()))
        print(f"Device {name} set.")

    # 3. Links
    all_link_ids = []
    for link in data.get('links', []):
        for ep_id in link.get('link_endpoint_ids', []):
            d_id = ep_id['device_id']['device_uuid']['uuid']
            ep_name = ep_id['endpoint_uuid']['uuid']
            ep_id['endpoint_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{d_id}/{ep_name}"))
        
        name = link.get('name', link['link_id']['link_uuid']['uuid'])
        link['link_id']['link_uuid']['uuid'] = name
        link['name'] = name
        if 'optical_details' in link: link.pop('optical_details')
        
        c.SetLink(ParseDict(link, Link()))
        all_link_ids.append(ParseDict(link['link_id'], LinkId()))
        print(f"Link {name} set.")

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
        svc['service_id']['service_uuid']['uuid'] = name
        svc['name'] = name
        svc['service_id']['context_id'] = {'context_uuid': {'uuid': ctx_uuid}}
        fix_config_rules(svc)
        for ep_id in svc.get('service_endpoint_ids', []):
             ep_id.pop('topology_id', None)
             d_uuid = ep_id['device_id']['device_uuid']['uuid']
             ep_uuid = ep_id['endpoint_uuid']['uuid']
             ep_id['endpoint_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{d_uuid}/{ep_uuid}"))
        c.SetService(ParseDict(svc, Service()))
        print(f"Service {name} set.")

    for slc in data.get('slices', []):
        name = slc.get('name', slc['slice_id']['slice_uuid']['uuid'])
        slc['slice_id']['slice_uuid']['uuid'] = name
        slc['name'] = name
        slc['slice_id']['context_id'] = {'context_uuid': {'uuid': ctx_uuid}}
        fix_config_rules(slc)
        for ep_id in slc.get('slice_endpoint_ids', []):
             ep_id.pop('topology_id', None)
             d_uuid = ep_id['device_id']['device_uuid']['uuid']
             ep_uuid = ep_id['endpoint_uuid']['uuid']
             ep_id['endpoint_uuid']['uuid'] = str(uuid.uuid5(NAMESPACE_TFS, f"{topo_uuid}/{d_uuid}/{ep_uuid}"))
        c.SetSlice(ParseDict(slc, Slice()))
        print(f"Slice {name} set.")

    print("Restoration complete.")
    c.close()

if __name__ == "__main__":
    restore()
