import json, uuid

OPT_PATTERNS = ['ROAD', 'OLS', 'HUB', 'SPLIT', 'LEAF', 'MGON', 'TP', 'OPT', 'QKD']

def fix_optical_topology():
    with open('SuperDescriptor_Analysis.json', 'r') as f:
        data = json.load(f)

    # First pass: map nodes and enforce types
    opt_nodes = set()
    for d in data.get('devices', []):
        name = d.get('name', '')
        is_optical = False
        
        if any(p in name for p in OPT_PATTERNS):
            is_optical = True
            opt_nodes.add(name)
            # Apply specific types for OpticalController visibility
            if 'SPLIT' in name: d['device_type'] = 'emu-optical-splitter'
            elif 'ROAD' in name or 'OLS' in name or 'HUB' in name: d['device_type'] = 'optical-roadm'
            elif 'QKD' in name: d['device_type'] = 'qkd-node'
            else: d['device_type'] = 'optical-transponder'
            
            # Force all endpoints to be optical
            if 'device_endpoints' not in d: d['device_endpoints'] = []
            for ep in d['device_endpoints']:
                ep['endpoint_type'] = 'optical'
            
            # Ensure standard ports for connectivity
            existing_eps = {e['endpoint_id']['endpoint_uuid']['uuid'] for e in d['device_endpoints']}
            for port in ['LINE', 'SIG', '1', '2', '1/1', 'common', 'leaf1', 'leaf2']:
                if port not in existing_eps:
                    d['device_endpoints'].append({
                        'endpoint_id': {'endpoint_uuid': {'uuid': port}, 'device_id': {'device_uuid': {'uuid': d['device_id']['device_uuid']['uuid']}}},
                        'name': port,
                        'endpoint_type': 'optical'
                    })

    # Second pass: links between optical nodes or matched by pattern
    for l in data.get('links', []):
        eps = l.get('link_endpoint_ids', [])
        if len(eps) < 2: continue
        
        src_node = eps[0]['device_id']['device_uuid']['uuid']
        dst_node = eps[1]['device_id']['device_uuid']['uuid']
        
        name = l.get('name', '')
        if src_node in opt_nodes or dst_node in opt_nodes or any(p in name for p in OPT_PATTERNS):
            # Force SRC-DST format for OpticalController
            new_name = f"{src_node}-{dst_node}"
            l['name'] = new_name
            l['link_id']['link_uuid']['uuid'] = new_name
            
            # Ensure optical_details with 20-slot initialization (fixes 0b crash)
            if 'optical_details' not in l:
                l['optical_details'] = {
                    'length': 100,
                    'src_port': eps[0]['endpoint_uuid']['uuid'],
                    'dst_port': eps[1]['endpoint_uuid']['uuid'],
                    'local_peer_port': eps[0]['endpoint_uuid']['uuid'],
                    'remote_peer_port': eps[1]['endpoint_uuid']['uuid'],
                    'used': False,
                    'c_slots': {str(i): 0 for i in range(1, 21)},
                    'l_slots': {str(i): 0 for i in range(1, 21)},
                    's_slots': {str(i): 0 for i in range(1, 21)}
                }

    with open('SuperDescriptor_Ready_v4.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Enrichment complete: SuperDescriptor_Ready_v4.json created.")

if __name__ == "__main__":
    fix_optical_topology()
