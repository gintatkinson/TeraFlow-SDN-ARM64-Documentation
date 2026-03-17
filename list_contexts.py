from context.client.ContextClient import ContextClient
from common.proto.context_pb2 import Empty

def list_all_contexts():
    client = ContextClient()
    contexts = client.ListContexts(Empty())
    print(f"Total Contexts: {len(contexts.contexts)}")
    for ctx in contexts.contexts:
        print(f"  Context ID: {ctx.context_id.context_uuid.uuid}, Name: {ctx.name}")

if __name__ == '__main__':
    list_all_contexts()
