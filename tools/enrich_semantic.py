import json, os

def get_slots():
    return {str(i): 1 for i in range(1, 21)}

def enrich_descriptor():
    filename = 'SuperDescriptor_Final_Semantic.json'
    with open(filename, 'r') as f:
        data = json.load(f)

    # 1. Enrich Optical Links with optical_details
    for link in data.get('links', []):
        if 'OPT_LINK' in link['name'] or 'ROAD' in link['name']:
            link['optical_details'] = {
                'length': 100,
                'src_port': 'LINE',
                'dst_port': 'LINE',
                'local_peer_port': 'LINE',
                'remote_peer_port': 'LINE',
                'used': False,
                'c_slots': get_slots(),
                'l_slots': {},
                's_slots': {}
            }
            print(f"Enriched Optical Link: {link['name']}")

    # 2. Enrich QKD Nodes with QKD metadata
    for dev in data.get('devices', []):
        if 'QKD' in dev['name']:
            # QKD nodes need specific config rules for discovery
            dev['device_config']['config_rules'].append({
                'action': 1,
                'custom': {
                    'resource_key': '_info',
                    'resource_value': json.dumps({
                        'type': 'qkd-node',
                        'model': 'GENERIC',
                        'version': '1.0'
                    })
                }
            })
            print(f"Enriched QKD Node: {dev['name']}")
        
        # Ensure name is ALWAYS set
        if 'name' not in dev or not dev['name']:
            dev['name'] = dev['device_id']['device_uuid']['uuid']

    # 3. Enrich Services with names
    for svc in data.get('services', []):
        if 'name' not in svc or not svc['name']:
            svc['name'] = svc['service_id']['service_uuid']['uuid']
            print(f"Fixed Service Name: {svc['name']}")

    with open('SuperDescriptor_Final_Semantic_Enriched.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("Enrichment complete: SuperDescriptor_Final_Semantic_Enriched.json")

if __name__ == "__main__":
    enrich_descriptor()
