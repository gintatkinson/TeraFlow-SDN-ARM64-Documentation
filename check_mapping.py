from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import DeviceId, Empty

def check_mapping():
    client = ContextClient()
    devices = client.ListDevices(Empty()).devices
    print(f"Total devices in system: {len(devices)}")
    for d in devices:
        print(f"  Device: {d.name} (UUID: {d.device_id.device_uuid.uuid})")

if __name__ == '__main__':
    check_mapping()
