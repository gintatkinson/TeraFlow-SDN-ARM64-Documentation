---
description: Check the overall health of the xG-AI Cognitive Controller system
---

1. Check Kubernetes Pod Status
// turbo
2. multipass exec teraflow-vm -- kubectl get pods -n tfs

3. Check VM Resource Utilization (Load, RAM, Disk)
// turbo
4. multipass exec teraflow-vm -- bash -c "uptime && free -m && df -h /"

5. Verify WebUI Accessibility (Dual Paths)
// turbo
6. curl -I http://192.168.2.3/ && curl -I http://192.168.2.3:8004/

7. Check Active Screen Sessions (Background Bridges)
// turbo
8. multipass exec teraflow-vm -- screen -ls
