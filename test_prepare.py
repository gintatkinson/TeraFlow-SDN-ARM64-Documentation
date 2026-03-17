import json, uuid
# copy relevant parts of restore_topology.py
def get_uuid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(name)))

ctx_uuid = get_uuid('admin')
topo_uuid = get_uuid('admin')

def map_endpoint_id(eid):
    eid['topology_id'] = {'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'topology_uuid': {'uuid': topo_uuid}}
    raw_dev_id = eid['device_id']['device_uuid']['uuid']
    eid['device_id']['device_uuid']['uuid'] = get_uuid(raw_dev_id)
    dev_uuid = eid['device_id']['device_uuid']['uuid']
    ep_name = eid['endpoint_uuid']['uuid']
    eid['endpoint_uuid']['uuid'] = get_uuid(f"{dev_uuid}:{ep_name}")

def prepare_object(obj):
    if not isinstance(obj, dict): return
    if 'context_id' in obj: obj['context_id'] = {'context_uuid': {'uuid': ctx_uuid}}
    if 'topology_ids' in obj:
        obj['topology_ids'] = [{'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'topology_uuid': {'uuid': topo_uuid}}]
    if 'topology_id' in obj:
        obj['topology_id'] = {'context_id': {'context_uuid': {'uuid': ctx_uuid}}, 'topology_uuid': {'uuid': topo_uuid}}
    if 'device_id' in obj and 'device_uuid' in obj['device_id']:
        obj['device_id']['device_uuid']['uuid'] = get_uuid(obj['device_id']['device_uuid']['uuid'])
    if 'endpoint_id' in obj: map_endpoint_id(obj['endpoint_id'])
    for k, v in obj.items():
        if isinstance(v, (dict, list)):
            if isinstance(v, list):
                for i in v: prepare_object(i)
            else:
                prepare_object(v)

def test():
    data = json.load(open('SuperDescriptor_Enriched.json'))
    dev = data['devices'][0]
    print(f"Before: {dev['device_id']}")
    prepare_object(dev)
    print(f"After IDs: {dev['device_id']}")
    print(f"After Topos: {dev.get('topology_ids')}")
    # Search for the bad UUID in the result
    res_str = json.dumps(dev)
    if 'c76135e3-24a8-5e92-9bed-c3c9139359c8' in res_str:
        print("BAD UUID FOUND IN RESULT!")
    else:
        print("Bad UUID clean.")

test()
