from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import ContextId, Empty

def check_both():
    client = ContextClient()
    ctxs = ['43813baf-195e-5da6-af20-b3d0922e71a7', 'bace0701-15e3-5144-97c5-47487d543032']
    
    for c_id_str in ctxs:
        c_id = ContextId(context_uuid={'uuid': c_id_str})
        print(f"Context {c_id_str}:")
        try:
            devs = client.ListDevices(Empty()) # Devices are global in many versions, but check ListDevices
            # Wait, ListDevices doesn't take context_id in some versions. 
            # Let's check ListTopologies
            topos = client.ListTopologies(c_id)
            print(f"  Topologies: {len(topos.topologies)}")
            
            svcs = client.ListServices(c_id)
            print(f"  Services: {len(svcs.services)}")
            
            slcs = client.ListSlices(c_id)
            print(f"  Slices: {len(slcs.slices)}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == '__main__':
    check_both()
