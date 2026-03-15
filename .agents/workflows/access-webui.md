---
description: Restore persistent WebUI access bridges (Port 80 and 8004)
---

1. Kill stale socat processes if any
// turbo
2. multipass exec teraflow-vm -- pkill socat || true

3. Restore Port 80 Bridge (Main WebUI)
// turbo
4. multipass exec teraflow-vm -- screen -dmS webui-bridge bash -c "while true; do socat TCP-LISTEN:80,fork,reuseaddr TCP:10.152.183.154:80; sleep 1; done"

5. Restore Port 8004 Bridge (Legacy Access)
// turbo
6. multipass exec teraflow-vm -- screen -dmS legacy-bridge bash -c "while true; do socat TCP-LISTEN:8004,fork,reuseaddr TCP:10.152.183.154:80; sleep 1; done"

7. Verify Access Paths
// turbo
8. curl -I http://192.168.2.3/ && curl -I http://192.168.2.3:8004/
