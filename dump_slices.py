from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import ContextId
from google.protobuf.json_format import MessageToDict

def dump_slices():
    client = ContextClient()
    ctx_uuid = '43813baf-195e-5da6-af20-b3d0922e71a7'
    ctx_id = ContextId(context_uuid={'uuid': ctx_uuid})
    
    slices = client.ListSlices(ctx_id)
    print(f"Found {len(slices.slices)} slices.")
    for slc in slices.slices:
        print(json.dumps(MessageToDict(slc), indent=2))

if __name__ == '__main__':
    import json
    dump_slices()
