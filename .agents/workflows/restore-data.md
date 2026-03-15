---
description: Restore network topology and scale services/slices after a system restart
---

1. Restore Core Topology (39 Devices, 89 Endpoints)
// turbo
2. multipass exec teraflow-vm -- bash -c "source /home/ubuntu/tfs_runtime_env_vars.sh && export PYTHONPATH=/home/ubuntu/tfs/src && python3 /home/ubuntu/tfs/tools/restore_topology.py"

3. Re-scale Network (Services and Slices)
// turbo
4. multipass exec teraflow-vm -- bash -c "source /home/ubuntu/tfs_runtime_env_vars.sh && export PYTHONPATH=/home/ubuntu/tfs/src && python3 /home/ubuntu/tfs/tools/scale_network.py"

5. Verify Data in Context
// turbo
6. multipass exec teraflow-vm -- bash -c "source /home/ubuntu/tfs_runtime_env_vars.sh && export PYTHONPATH=/home/ubuntu/tfs/src && python3 -c 'from common.proto.context_pb2 import ContextId; from context.client.ContextClient import ContextClient; c = ContextClient(); ctx_id = ContextId(context_uuid={\"uuid\": \"admin\"}); print(\"Services:\", len(c.ListServices(ctx_id).services)); print(\"Slices:\", len(c.ListSlices(ctx_id).slices))'"
