import json, uuid

def get_uuid(name):
    if not name: return None
    try:
        uuid.UUID(str(name))
        return str(name)
    except:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(name)))

def verify():
    with open('SuperDescriptor_Enriched.json', 'r') as f:
        data = json.load(f)

    # 1. Collect all endpoints defined in devices
    device_endpoints = {} # (dev_uuid, ep_name) -> ep_uuid
    hashed_endpoints = set()
    
    for dev in data.get('devices', []):
        dev_id = dev['device_id']['device_uuid']['uuid']
        dev_uuid = get_uuid(dev_id)
        
        for ep in dev.get('device_endpoints', []):
            ep_name = ep['endpoint_id']['endpoint_uuid']['uuid']
            ep_uuid = get_uuid(f"{dev_uuid}:{ep_name}")
            device_endpoints[(dev_uuid, ep_name)] = ep_uuid
            hashed_endpoints.add(ep_uuid)

    print(f"Total endpoints defined in devices: {len(hashed_endpoints)}")

    # 2. Check links
    missing_links = 0
    total_links = 0
    for link in data.get('links', []):
        total_links += 1
        link_id = link['link_id']['link_uuid']['uuid']
        link_uuid = get_uuid(link_id)
        
        for ep_id in link.get('link_endpoint_ids', []):
            d_id = ep_id['device_id']['device_uuid']['uuid']
            e_id = ep_id['endpoint_uuid']['uuid']
            
            d_uuid = get_uuid(d_id)
            e_uuid = get_uuid(f"{d_uuid}:{e_id}")
            
            if e_uuid not in hashed_endpoints:
                print(f"MISSING: Link {link_id} ({link_uuid}) references unknown endpoint {e_id} on device {d_id} ({d_uuid}). Target Hash: {e_uuid}")
                missing_links += 1
    
    print(f"Total links checked: {total_links}")
    print(f"Total link-endpoint references missing: {missing_links}")

if __name__ == "__main__":
    verify()
