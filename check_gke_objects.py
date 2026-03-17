import os, uuid
from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import ContextId, TopologyId

def get_uuid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(name)))

def check_gke():
    client = ContextClient()
    ctx_uuid = get_uuid('admin')
    topo_uuid = get_uuid('admin')
    
    ctx_id = ContextId(context_uuid={'uuid': ctx_uuid})
    topo_id = TopologyId(context_id=ctx_id, topology_uuid={'uuid': topo_uuid})
    
    print(f"Context UUID: {ctx_uuid}")
    print(f"Topology UUID: {topo_uuid}")
    
    try:
        services = client.ListServices(ctx_id)
        print(f"Found {len(services.services)} services in context {ctx_uuid}")
        for s in services.services:
            print(f"  Service: {s.service_id.service_uuid.uuid}")
            
        slices = client.ListSlices(ctx_id)
        print(f"Found {len(slices.slices)} slices in context {ctx_uuid}")
        for sl in slices.slices:
            print(f"  Slice: {sl.slice_id.slice_uuid.uuid}")
            
        topologies = client.ListTopologies(ctx_id)
        print(f"Found {len(topologies.topologies)} topologies in context {ctx_uuid}")
        for t in topologies.topologies:
            print(f"  Topology: {t.topology_id.topology_uuid.uuid}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_gke()
