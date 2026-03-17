from common.proto.context_pb2 import Empty, ContextId
from context.client.ContextClient import ContextClient

def super_wipe():
    print("Executing SUPER WIPE...")
    c = ContextClient()
    
    # 1. Services & Slices
    contexts = c.ListContexts(Empty()).contexts
    for ctx in contexts:
        cid = ctx.context_id
        print(f"Cleaning context: {cid.context_uuid.uuid}")
        
        slices = c.ListSlices(cid).slices
        for s in slices:
            try: c.RemoveSlice(s.slice_id)
            except: pass
            
        services = c.ListServices(cid).services
        for s in services:
            try: c.RemoveService(s.service_id)
            except: pass

    # 2. Links
    links = c.ListLinks(Empty()).links
    print(f"Removing {len(links)} links...")
    for l in links:
        try: c.RemoveLink(l.link_id)
        except: pass

    # 3. Devices
    devices = c.ListDevices(Empty()).devices
    print(f"Removing {len(devices)} devices...")
    for d in devices:
        try: c.RemoveDevice(d.device_id)
        except: pass

    # 4. Topologies & Contexts
    contexts = c.ListContexts(Empty()).contexts
    for ctx in contexts:
        cid = ctx.context_id
        topos = c.ListTopologies(cid).topologies
        for t in topos:
            print(f"Removing topology: {t.topology_id.topology_uuid.uuid}")
            try: c.RemoveTopology(t.topology_id)
            except: pass
        
        print(f"Removing context: {cid.context_uuid.uuid}")
        try: c.RemoveContext(cid)
        except: pass

    print("SUPER WIPE complete.")

if __name__ == '__main__':
    super_wipe()
