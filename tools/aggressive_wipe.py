import json, uuid
from common.proto.context_pb2 import Empty, ContextId, TopologyId
from context.client.ContextClient import ContextClient

def aggressive_wipe():
    print("Starting Aggressive GKE Wipe...")
    ctx_client = ContextClient()
    ctx_client.connect()
    
    # 1. Slices
    try:
        slices = ctx_client.ListSlices(Empty())
        for s in slices.slices:
            print(f"Deleting Slice: {s.slice_id.slice_uuid.uuid}")
            ctx_client.RemoveSlice(s.slice_id)
    except: pass

    # 2. Services
    try:
        contexts = ctx_client.ListContextIds(Empty())
        for ctx_id in contexts.context_ids:
            services = ctx_client.ListServices(ctx_id)
            for s in services.services:
                print(f"Deleting Service: {s.service_id.service_uuid.uuid}")
                ctx_client.RemoveService(s.service_id)
    except: pass

    # 3. Links
    try:
        links = ctx_client.ListLinks(Empty())
        for l in links.links:
            print(f"Deleting Link: {l.link_id.link_uuid.uuid}")
            ctx_client.RemoveLink(l.link_id)
    except: pass

    # 4. Devices
    try:
        devices = ctx_client.ListDevices(Empty())
        for d in devices.devices:
            print(f"Deleting Device: {d.device_id.device_uuid.uuid}")
            ctx_client.RemoveDevice(d.device_id)
    except: pass

    # 5. Topologies (except admin)
    try:
        for ctx_id in contexts.context_ids:
            topos = ctx_client.ListTopologies(ctx_id)
            for t in topos.topologies:
                if t.topology_id.topology_uuid.uuid != 'c76135e3-24a8-5e92-9bed-c3c9139359c8':
                    print(f"Deleting Topology: {t.topology_id.topology_uuid.uuid}")
                    ctx_client.RemoveTopology(t.topology_id)
    except: pass

    print("Aggressive Wipe Complete.")
    ctx_client.close()

if __name__ == "__main__":
    aggressive_wipe()
