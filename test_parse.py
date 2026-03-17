import json
from common.proto.context_pb2 import Device
from google.protobuf.json_format import ParseDict, MessageToDict

dev_dict = {
    "device_id": {"device_uuid": {"uuid": "test-dev"}},
    "device_endpoints": [
        {
            "endpoint_id": {
                "device_id": {"device_uuid": {"uuid": "test-dev"}},
                "endpoint_uuid": {"uuid": "test-ep"}
            },
            "endpoint_type": "copper"
        }
    ]
}

dev_proto = Device()
ParseDict(dev_dict, dev_proto)
print("Proto device_endpoints len:", len(dev_proto.device_endpoints))
if len(dev_proto.device_endpoints) > 0:
    print("Endpoint UUID:", dev_proto.device_endpoints[0].endpoint_id.endpoint_uuid.uuid)
else:
    print("FAILED to parse endpoints")

msg_dict = MessageToDict(dev_proto)
print("MessageToDict output keys:", msg_dict.keys())
