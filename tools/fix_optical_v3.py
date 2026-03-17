import json, uuid

def fix_optical_topology():
    with open('SuperDescriptor_Analysis.json', 'r') as f:
        data = json.load(f)

    # 1. Device Enrichment and Type Correction
    for d in data.get('devices', []):
        name = d.get('name', '')
        is_optical = False
        
        # Determine Optical Type
        if 'ROAD' in name or 'OLS' in name or 'HUB' in name:
            d['device_type'] = 'optical-roadm'
            is_optical = True
        elif 'SPLIT' in name:
            d['device_type'] = 'emu-optical-splitter'
            is_optical = True
        elif 'LEAF' in name or 'MGON' in name or 'TP' in name or 'OPT' in name:
            d['device_type'] = 'optical-transponder'
            is_optical = True
            
        if is_optical:
            if 'device_endpoints' not in d: d['device_endpoints'] = []
            
            # Force ALL endpoints to be optical type
            for ep in d['device_endpoints']:
                ep['endpoint_type'] = 'optical'
            
            # Ensure standard ports for ROADMs and the like
            existing_eps = {e['endpoint_id']['endpoint_uuid']['uuid'] for e in d.get('device_endpoints', [])}
            standard_ports = []
            if d['device_type'] == 'optical-roadm':
                standard_ports = ['SIG', 'LINE', '1', '2']
            elif d['device_type'] == 'emu-optical-splitter':
                standard_ports = ['common', 'leaf1', 'leaf2']
            else:
                standard_ports = ['1/1', 'LINE']
                
            for port in standard_ports:
                if port not in existing_eps:
                    d['device_endpoints'].append({
                        'endpoint_id': {'endpoint_uuid': {'uuid': port}, 'device_id': {'device_uuid': {'uuid': d['device_id']['device_uuid']['uuid']}}},
                        'name': port,
                        'endpoint_type': 'optical'
                    })

    # 2. Link Enrichment and Name Alignment
    for l in data.get('links', []):
        name = l.get('name', '')
        if '_OPT_LINK' in name or '_QKD_LINK' in name or '-' not in name:
            # Normalize names to SRC-DST for OpticalController
            clean_name = name.replace('_OPT_LINK', '').replace('_QKD_LINK', '')
            parts = clean_name.split('_')
            if len(parts) >= 2:
                src_name = parts[0]
                dst_name = parts[1]
                new_name = f"{src_name}-{dst_name}"
                l['name'] = new_name
                l['link_id']['link_uuid']['uuid'] = new_name
                
                # Link endpoints
                if 'link_endpoint_ids' not in l or len(l['link_endpoint_ids']) < 2:
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

    with open('SuperDescriptor_Ready_v3.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Enrichment complete: SuperDescriptor_Ready_v3.json created.")

if __name__ == "__main__":
    fix_optical_topology()
