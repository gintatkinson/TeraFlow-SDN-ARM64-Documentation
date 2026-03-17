import json

def enrich():
    with open('SuperDescriptor_Final.json', 'r') as f:
        data = json.load(f)

    if 'devices' not in data: data['devices'] = []

    # 1. Map existing devices
    devices = {dev['device_id']['device_uuid']['uuid']: dev for dev in data['devices']}

    # 2. Collect all referenced endpoints
    referenced_endpoints = [] # List of (device_id_str, endpoint_uuid_str)

    def collect_all(obj):
        if isinstance(obj, list):
            for i in obj: collect_all(i)
            return
        if not isinstance(obj, dict): return
        
        # Check standard endpoint_id
        if 'endpoint_id' in obj:
            eid = obj['endpoint_id']
            if 'device_id' in eid and 'endpoint_uuid' in eid:
                referenced_endpoints.append((eid['device_id']['device_uuid']['uuid'], eid['endpoint_uuid']['uuid']))
        
        # Check link/service/slice endpoint lists
        for key in ['link_endpoint_ids', 'service_endpoint_ids', 'slice_endpoint_ids', 'endpoint_ids']:
            if key in obj and isinstance(obj[key], list):
                for eid in obj[key]:
                    if 'device_id' in eid and 'endpoint_uuid' in eid:
                        referenced_endpoints.append((eid['device_id']['device_uuid']['uuid'], eid['endpoint_uuid']['uuid']))
        
        # Recurse into all dict values
        for v in obj.values():
            if isinstance(v, (dict, list)):
                collect_all(v)

    print("Scanning topology for referenced endpoints and devices...")
    collect_all(data)
    
    unique_refs = set(referenced_endpoints)
    print(f"Found {len(unique_refs)} unique endpoint references.")

    # 3. Ensure they exist
    added_dev_count = 0
    added_ep_count = 0
    
    for d_id, e_id in unique_refs:
        # If device is missing, create it
        if d_id not in devices:
            new_dev = {
                'device_id': {'device_uuid': {'uuid': d_id}},
                'device_type': 'emu-packet-router',
                'device_config': {'config_rules': []},
                'device_operational_status': 1,
                'device_drivers': [0],
                'device_endpoints': []
            }
            data['devices'].append(new_dev)
            devices[d_id] = new_dev
            added_dev_count += 1
            print(f"Auto-created missing device: {d_id}")

        dev = devices[d_id]
        if 'device_endpoints' not in dev: dev['device_endpoints'] = []
        
        # Check if endpoint already exists
        exists = any(ep['endpoint_id']['endpoint_uuid']['uuid'] == e_id for ep in dev['device_endpoints'])
        if not exists:
            dev['device_endpoints'].append({
                'endpoint_id': {
                    'device_id': {'device_uuid': {'uuid': d_id}},
                    'endpoint_uuid': {'uuid': e_id}
                },
                'endpoint_type': 'copper',
                'kpi_sample_types': []
            })
            added_ep_count += 1

    print(f"Enrichment Summary: Added {added_dev_count} phantom devices and {added_ep_count} missing endpoints.")
    with open('SuperDescriptor_Enriched.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("SuperDescriptor_Enriched.json updated.")

if __name__ == "__main__":
    enrich()
