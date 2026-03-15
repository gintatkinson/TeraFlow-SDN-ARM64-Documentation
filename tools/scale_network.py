import json
import random
import time
from common.proto.context_pb2 import ContextId, Service, Slice, Empty, SERVICETYPE_L3NM, SERVICESTATUS_PLANNED, SliceId
from context.client.ContextClient import ContextClient
from service.client.ServiceClient import ServiceClient
from slice.client.SliceClient import SliceClient

def scale():
    cc = ContextClient()
    sc = ServiceClient()
    slc = SliceClient()

    ctx_id = ContextId()
    ctx_id.context_uuid.uuid = "admin"

    # 1. Cleanup old scaled services and slices to avoid conflicts
    print("Cleaning up old scaled services and slices...")
    try:
        services = cc.ListServices(ctx_id).services
        for s in services:
            if s.service_id.service_uuid.uuid.startswith("scale-svc-"):
                sc.DeleteService(s.service_id)
        
        slices = cc.ListSlices(ctx_id).slices
        for s in slices:
            if s.slice_id.slice_uuid.uuid.startswith("scale-slice-"):
                slc.DeleteSlice(s.slice_id)
    except Exception as e:
        print(f"Cleanup warning: {e}")

    # 2. Fetch valid inventory
    print("Fetching valid inventory...")
    devs = cc.ListDevices(Empty()).devices
    inventory = []
    for d in devs:
        if d.device_endpoints:
            eps = [e.endpoint_id.endpoint_uuid.uuid for e in d.device_endpoints]
            if eps:
                inventory.append({
                    "device_uuid": d.device_id.device_uuid.uuid,
                    "endpoints": eps
                })
    
    if len(inventory) < 2:
        print("Not enough devices with endpoints to scale.")
        return

    print(f"Inventory found: {len(inventory)} devices with endpoints.")

    # 3. Provision 30 services
    print("Provisioning 30 services...")
    for i in range(30):
        svc_uuid = f"scale-svc-{i+1:02d}"
        try:
            u1_data = random.choice(inventory)
            u2_data = random.choice(inventory)
            while u1_data == u2_data:
                u2_data = random.choice(inventory)
            
            # Step 1: Create
            s = Service()
            s.service_id.context_id.context_uuid.uuid = "admin"
            s.service_id.service_uuid.uuid = svc_uuid
            s.service_type = SERVICETYPE_L3NM
            s.service_status.service_status = SERVICESTATUS_PLANNED
            sc.CreateService(s)
            
            # Step 2: Update with endpoints
            s.service_endpoint_ids.add().CopyFrom(cc.GetDevice(cc.ListDevices(Empty()).devices[0].device_id).device_endpoints[0].endpoint_id) # Placeholder to ensure we get a real EndPointId object if needed, but we'll build it
            s.service_endpoint_ids.pop() # clear placeholder
            
            e1 = s.service_endpoint_ids.add()
            e1.topology_id.context_id.context_uuid.uuid = "admin"
            e1.topology_id.topology_uuid.uuid = "admin"
            e1.device_id.device_uuid.uuid = u1_data["device_uuid"]
            e1.endpoint_uuid.uuid = random.choice(u1_data["endpoints"])
            
            e2 = s.service_endpoint_ids.add()
            e2.topology_id.context_id.context_uuid.uuid = "admin"
            e2.topology_id.topology_uuid.uuid = "admin"
            e2.device_id.device_uuid.uuid = u2_data["device_uuid"]
            e2.endpoint_uuid.uuid = random.choice(u2_data["endpoints"])
            
            sc.UpdateService(s)
            print(f"Created Service: {svc_uuid}")
        except Exception as e:
            print(f"Failed to process service {svc_uuid}: {e}")

    # 4. Provision 10 slices
    print("Provisioning 10 slices...")
    for i in range(10):
        slc_uuid = f"scale-slice-{i+1:02d}"
        try:
            u1_data = random.choice(inventory)
            u2_data = random.choice(inventory)
            while u1_data == u2_data:
                u2_data = random.choice(inventory)
            
            # Step 1: Create
            sl = Slice()
            sl.slice_id.context_id.context_uuid.uuid = "admin"
            sl.slice_id.slice_uuid.uuid = slc_uuid
            sl.slice_status.slice_status = 1
            slc.CreateSlice(sl)
            
            # Step 2: Update with endpoints
            e1 = sl.slice_endpoint_ids.add()
            e1.topology_id.context_id.context_uuid.uuid = "admin"
            e1.topology_id.topology_uuid.uuid = "admin"
            e1.device_id.device_uuid.uuid = u1_data["device_uuid"]
            e1.endpoint_uuid.uuid = random.choice(u1_data["endpoints"])
            
            e2 = sl.slice_endpoint_ids.add()
            e2.topology_id.context_id.context_uuid.uuid = "admin"
            e2.topology_id.topology_uuid.uuid = "admin"
            e2.device_id.device_uuid.uuid = u2_data["device_uuid"]
            e2.endpoint_uuid.uuid = random.choice(u2_data["endpoints"])
            
            slc.UpdateSlice(sl)
            print(f"Created Slice: {slc_uuid}")
        except Exception as e:
            print(f"Failed to process slice {slc_uuid}: {e}")

if __name__ == '__main__':
    scale()
