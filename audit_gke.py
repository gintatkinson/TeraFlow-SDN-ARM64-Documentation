import os, uuid
from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import ContextId, Empty

def audit():
    client = ContextClient()
    ctxs = client.ListContexts(Empty()).contexts
    
    print(f"Total Contexts: {len(ctxs)}")
    for ctx in ctxs:
        c_id = ctx.context_id
        c_uuid = c_id.context_uuid.uuid
        print(f"\nContext: {c_uuid} (Name: {ctx.name})")
        
        topos = client.ListTopologies(c_id).topologies
        print(f"  Topologies: {len(topos)}")
        for t in topos:
            t_id = t.topology_id
            print(f"    Topology: {t_id.topology_uuid.uuid}")
            details = client.GetTopologyDetails(t_id)
            print(f"      Devices: {len(details.devices)}")
            print(f"      Links: {len(details.links)}")
            
        svcs = client.ListServices(c_id).services
        print(f"  Services: {len(svcs)}")
        
        slcs = client.ListSlices(c_id).slices
        print(f"  Slices: {len(slcs)}")

if __name__ == '__main__':
    audit()
