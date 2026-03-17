import json, uuid
from common.proto.context_pb2 import ContextId, Empty
from context.client.ContextClient import ContextClient

def super_wipe():
    print("Performing GKE Super Wipe...")
    ctx_client = ContextClient()
    
    # Contexts to clear
    try:
        contexts = ctx_client.ListContextIds(Empty())
        for ctx_id in contexts.context_ids:
            print(f"Clearing context: {ctx_id.context_uuid.uuid}")
            # We don't delete 'admin' if it has critical server-side constraints, 
            # but we can clear its contents.
            # Actually, standard TFS allows deleting contexts.
            ctx_client.RemoveContext(ctx_id)
    except Exception as e:
        print(f"Wipe error: {e}")
    print("Wipe complete.")

if __name__ == "__main__":
    super_wipe()
