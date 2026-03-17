import os, uuid
from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import DeviceId

def get_uuid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(name)))

def check():
    client = ContextClient()
    dc1_uuid = get_uuid('DC1')
    dc2_uuid = get_uuid('DC2')
    
    print(f"DC1 UUID: {dc1_uuid}")
    dev1 = client.GetDevice(DeviceId(device_uuid={'uuid': dc1_uuid}))
    for ep in dev1.device_endpoints:
        print(f"  DC1 Endpoint: {ep.endpoint_id.endpoint_uuid.uuid}")

    print(f"DC2 UUID: {dc2_uuid}")
    dev2 = client.GetDevice(DeviceId(device_uuid={'uuid': dc2_uuid}))
    for ep in dev2.device_endpoints:
        print(f"  DC2 Endpoint: {ep.endpoint_id.endpoint_uuid.uuid}")

if __name__ == '__main__':
    check()
