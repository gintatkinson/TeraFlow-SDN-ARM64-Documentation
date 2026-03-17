import json, uuid

# Standard TFS Namespace
NAMESPACE_TFS = uuid.UUID("200e3a1f-2223-534f-a100-758e29c37f40")

def get_semantic_name(old_id):
    if old_id.startswith('BB'): return f"GKE-BB-L3-{old_id[2:]:0>2}"
    if old_id.startswith('CE'): return f"GKE-CE-L3-{old_id[2:]:0>2}"
    if old_id.startswith('PE'): return f"GKE-PE-L3-{old_id[2:]:0>2}"
    if old_id.startswith('DC'): return f"GKE-DC-L3-{old_id[2:]:0>2}"
    if old_id.startswith('MGON'): return f"GKE-OPT-MGON-{old_id[4:]:0>2}"
    if old_id.startswith('OFC HUB'): return f"GKE-OPT-HUB-01"
    if old_id.startswith('OFC LEAF'): return f"GKE-OPT-LEAF-{old_id[9:]:0>2}"
    if old_id == 'OLS': return "GKE-OPT-OLS-01"
    if old_id == 'MW': return "GKE-MW-L3-01"
    if old_id == 'IPM': return "GKE-IP-MESH-01"
    if old_id == 'Optical-Splitter': return "GKE-OPT-SPLIT-01"
    if old_id == 'core-net': return "GKE-NET-CORE-01"
    if old_id == 'edge-net': return "GKE-NET-EDGE-01"
    if old_id.lower().startswith('r'):
        num = old_id[1:]
        if num.isdigit(): return f"GKE-RTR-L3-{num:0>3}"
    if old_id.startswith('T'): return f"GKE-TERM-L3-{old_id[1:].replace('.','-')}"
    if old_id.startswith('IP'): return f"GKE-IP-NODE-{old_id[2:]:0>2}"
    return f"GKE-DEV-{old_id}"

def transform():
    with open('SuperDescriptor_Enriched.json', 'r') as f:
        data = json.load(f)

    # 1. Map Device IDs
    id_map = {}
    for dev in data.get('devices', []):
        old_id = dev['device_id']['device_uuid']['uuid']
        new_name = get_semantic_name(old_id)
        id_map[old_id] = new_name
        dev['device_id']['device_uuid']['uuid'] = new_name
        dev['name'] = new_name
        # Update endpoints
        for ep in dev.get('device_endpoints', []):
            ep['endpoint_id']['device_id']['device_uuid']['uuid'] = new_name

    # 2. Map Links
    for link in data.get('links', []):
        link_uuid = link['link_id']['link_uuid']['uuid']
        # Link name usually source_dest
        parts = link_uuid.split('_')
        new_parts = [id_map.get(p, p) for p in parts]
        new_link_name = '_'.join(new_parts) + '_LINK'
        link['link_id']['link_uuid']['uuid'] = new_link_name
        link['name'] = new_link_name
        for ep_id in link.get('link_endpoint_ids', []):
            dev_id = ep_id['device_id']['device_uuid']['uuid']
            ep_id['device_id']['device_uuid']['uuid'] = id_map.get(dev_id, dev_id)

    # 3. Map Services
    for svc in data.get('services', []):
        svc_name = svc['service_id']['service_uuid']['uuid']
        new_svc_name = f"SVC-{svc_name}"
        svc['service_id']['service_uuid']['uuid'] = new_svc_name
        svc['name'] = new_svc_name
        for ep_id in svc.get('service_endpoint_ids', []):
            dev_id = ep_id['device_id']['device_uuid']['uuid']
            ep_id['device_id']['device_uuid']['uuid'] = id_map.get(dev_id, dev_id)

    # 4. Map Slices
    for slc in data.get('slices', []):
        slc_name = slc['slice_id']['slice_uuid']['uuid']
        new_slc_name = f"SLICE-{slc_name}"
        slc['slice_id']['slice_uuid']['uuid'] = new_slc_name
        slc['name'] = new_slc_name
        for ep_id in slc.get('slice_endpoint_ids', []):
            dev_id = ep_id['device_id']['device_uuid']['uuid']
            ep_id['device_id']['device_uuid']['uuid'] = id_map.get(dev_id, dev_id)

    with open('SuperDescriptor_Semantic.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("Transformation to SuperDescriptor_Semantic.json complete.")

if __name__ == "__main__":
    transform()
