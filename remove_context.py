from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import ContextId, TopologyId

def remove_redundant_context():
    client = ContextClient()
    ctx_to_remove = '43813baf-195e-5da6-af20-b3d0922e71a7'
    
    print(f"Purging redundant context and its topologies: {ctx_to_remove}")
    try:
        # 1. List and remove topologies
        topos = client.ListTopologies(ContextId(context_uuid={'uuid': ctx_to_remove}))
        for t in topos.topologies:
            print(f"  Removing topology: {t.topology_id.topology_uuid.uuid}")
            client.RemoveTopology(t.topology_id)
        
        # 2. Remove context
        client.RemoveContext(ContextId(context_uuid={'uuid': ctx_to_remove}))
        print("Successfully purged redundant 'admin' context.")
    except Exception as e:
        print(f"Error during purge: {e}")

if __name__ == '__main__':
    remove_redundant_context()
