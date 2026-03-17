from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import Context, ContextId

def swap_names():
    client = ContextClient()
    # 4381... currently 'stale-admin' (84 devs)
    # bace... currently 'admin' (41 devs, 2 svcs, 1 slc)
    
    ctx1_id = '43813baf-195e-5da6-af20-b3d0922e71a7'
    ctx2_id = 'bace0701-15e3-5144-97c5-47487d543032'
    
    print("Renaming bace... (current admin) to 'admin-backup'")
    c2 = Context()
    c2.context_id.context_uuid.uuid = ctx2_id
    c2.name = 'admin-backup'
    client.SetContext(c2)
    
    print("Renaming 4381... (current stale-admin) to 'admin'")
    c1 = Context()
    c1.context_id.context_uuid.uuid = ctx1_id
    c1.name = 'admin'
    client.SetContext(c1)
    
    print("Names swapped successfully.")

if __name__ == '__main__':
    swap_names()
