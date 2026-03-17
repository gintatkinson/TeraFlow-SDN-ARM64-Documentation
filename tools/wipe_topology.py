from common.proto.context_pb2 import Empty, ContextId, DeviceId, LinkId, ServiceId, SliceId
from context.client.ContextClient import ContextClient

def wipe():
    print("Starting topology wipe for fresh restoration...")
    c = ContextClient()
    
    contexts = c.ListContexts(Empty()).contexts
    print(f"Found {len(contexts)} contexts.")

    for ctx in contexts:
        cid = ctx.context_id
        # 1. Delete Slices
        slices = c.ListSlices(cid).slices
        print(f"Deleting {len(slices)} slices in context {cid.context_uuid.uuid}...")
        for slc in slices:
            try:
                c.RemoveSlice(slc.slice_id)
            except:
                pass

        # 2. Delete Services
        services = c.ListServices(cid).services
        print(f"Deleting {len(services)} services in context {cid.context_uuid.uuid}...")
        for svc in services:
            try:
                c.RemoveService(svc.service_id)
            except:
                pass

    # 3. Delete Links
    links = c.ListLinks(Empty()).links
    print(f"Deleting {len(links)} links...")
    for l in links:
        try:
            c.RemoveLink(l.link_id)
        except:
            pass

    # 4. Delete Devices
    devices = c.ListDevices(Empty()).devices
    print(f"Deleting {len(devices)} devices...")
    for d in devices:
        try:
            c.RemoveDevice(d.device_id)
        except:
            pass

    print("Wipe complete.")

if __name__ == "__main__":
    wipe()
