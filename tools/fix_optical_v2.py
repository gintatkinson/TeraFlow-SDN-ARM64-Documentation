import json, uuid

def fix_optical_topology():
    with open('SuperDescriptor_Analysis.json', 'r') as f:
        data = json.load(f)

    # 1. Device Enrichment and Type Correction
    for d in data.get('devices', []):
        name = d.get('name', '')
        # ROADMs
        if 'ROAD' in name or 'OLS' in name or 'HUB' in name:
            d['device_type'] = 'optical-roadm'
            if 'device_endpoints' not in d: d['device_endpoints'] = []
            # Ensure at least SIG and LINE ports
            existing_eps = {e['endpoint_id']['endpoint_uuid']['uuid'] for e in d.get('device_endpoints', [])}
            for port in ['SIG', 'LINE', '1', '2']:
                if port not in existing_eps:
                    d['device_endpoints'].append({
                        'endpoint_id': {'endpoint_uuid': {'uuid': port}, 'device_id': {'device_uuid': {'uuid': d['device_id']['device_uuid']['uuid']}}},
                        'name': port,
                        'endpoint_type': 'optical'
                    })
        # Transponders / Leaf / MGON
        elif 'LEAF' in name or 'MGON' in name or 'TP' in name:
            d['device_type'] = 'optical-transponder'
            if 'device_endpoints' not in d: d['device_endpoints'] = []
            existing_eps = {e['endpoint_id']['endpoint_uuid']['uuid'] for e in d.get('device_endpoints', [])}
            for port in ['1/1', 'LINE']:
                if port not in existing_eps:
                    d['device_endpoints'].append({
                        'endpoint_id': {'endpoint_uuid': {'uuid': port}, 'device_id': {'device_uuid': {'uuid': d['device_id']['device_uuid']['uuid']}}},
                        'name': port,
                        'endpoint_type': 'optical'
                    })

    # 2. Link Enrichment and Name Alignment
    # OpticalController expects "SRC_NAME-DST_NAME"
    for l in data.get('links', []):
        name = l.get('name', '')
        if '_OPT_LINK' in name or '_QKD_LINK' in name:
            # Try to identify src/dst from name
            parts = name.replace('_OPT_LINK', '').replace('_QKD_LINK', '').split('_')
            if len(parts) >= 2:
                src_name = parts[0]
                dst_name = parts[1]
                new_name = f"{src_name}-{dst_name}"
                l['name'] = new_name
                l['link_id']['link_uuid']['uuid'] = new_name
                
                # Check endpoints
                if len(l.get('link_endpoint_ids', [])) < 2:
                    # Manually add endpoints if missing
                    l['link_endpoint_ids'] = [
                        {'device_id': {'device_uuid': {'uuid': src_name}}, 'endpoint_uuid': {'uuid': 'LINE'}},
                        {'device_id': {'device_uuid': {'uuid': dst_name}}, 'endpoint_uuid': {'uuid': 'LINE'}}
                    ]
            
            # Ensure optical_details
            if 'optical_details' not in l:
                l['optical_details'] = {
                    'length': 100,
                    'src_port': 'LINE',
                    'dst_port': 'LINE',
                    'local_peer_port': 'LINE',
                    'remote_peer_port': 'LINE',
                    'used': False,
                    'c_slots': {str(i): 0 for i in range(1, 21)},
                    'l_slots': {str(i): 0 for i in range(1, 21)},
                    's_slots': {str(i): 0 for i in range(1, 21)}
                }

    with open('SuperDescriptor_Ready_v2.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Enrichment complete: SuperDescriptor_Ready_v2.json created.")

if __name__ == "__main__":
    fix_optical_topology()
