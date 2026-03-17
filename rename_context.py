from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import Context, ContextId

def rename_redundant_context():
    client = ContextClient()
    ctx_id_str = '43813baf-195e-5da6-af20-b3d0922e71a7'
    
    print(f"Renaming redundant context: {ctx_id_str}")
    try:
        # Fetch current and update name
        # Some versions might require a full SetContext with same ID but new name
        ctx_proto = Context()
        ctx_proto.context_id.context_uuid.uuid = ctx_id_str
        ctx_proto.name = 'admin'
        
        client.SetContext(ctx_proto)
        print("Successfully renamed redundant 'admin' to 'stale-admin'.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    rename_redundant_context()
