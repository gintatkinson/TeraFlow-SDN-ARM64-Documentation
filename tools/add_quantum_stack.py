import json

def add_quantum():
    with open('SuperDescriptor_Semantic.json', 'r') as f:
        data = json.load(f)

    # 1. Add Optical Nodes (ROADM)
    opt1 = {
        "device_id": {"device_uuid": {"uuid": "GKE-OPT-ROAD-01"}},
        "name": "GKE-OPT-ROAD-01",
        "device_type": "optical-roadm",
        "device_config": {"config_rules": [{"action": 1, "custom": {"resource_key": "_connect/address", "resource_value": "127.0.0.1"}}]},
        "device_operational_status": 2,
        "device_endpoints": [{"endpoint_id": {"device_id": {"device_uuid": {"uuid": "GKE-OPT-ROAD-01"}}, "endpoint_uuid": {"uuid": "LINE"}}, "name": "LINE", "endpoint_type": "optical"}]
    }
    opt2 = {
        "device_id": {"device_uuid": {"uuid": "GKE-OPT-ROAD-02"}},
        "name": "GKE-OPT-ROAD-02",
        "device_type": "optical-roadm",
        "device_config": {"config_rules": [{"action": 1, "custom": {"resource_key": "_connect/address", "resource_value": "127.0.0.1"}}]},
        "device_operational_status": 2,
        "device_endpoints": [{"endpoint_id": {"device_id": {"device_uuid": {"uuid": "GKE-OPT-ROAD-02"}}, "endpoint_uuid": {"uuid": "LINE"}}, "name": "LINE", "endpoint_type": "optical"}]
    }
    
    # 2. Add QKD Nodes
    qkd1 = {
        "device_id": {"device_uuid": {"uuid": "GKE-QKD-NODE-01"}},
        "name": "GKE-QKD-NODE-01",
        "device_type": "qkd-node",
        "device_config": {"config_rules": [{"action": 1, "custom": {"resource_key": "_connect/address", "resource_value": "127.0.0.1"}}]},
        "device_operational_status": 2,
        "device_endpoints": [{"endpoint_id": {"device_id": {"device_uuid": {"uuid": "GKE-QKD-NODE-01"}}, "endpoint_uuid": {"uuid": "QKD-INTF"}}, "name": "QKD-INTF", "endpoint_type": "qkd"}]
    }
    qkd2 = {
        "device_id": {"device_uuid": {"uuid": "GKE-QKD-NODE-02"}},
        "name": "GKE-QKD-NODE-02",
        "device_type": "qkd-node",
        "device_config": {"config_rules": [{"action": 1, "custom": {"resource_key": "_connect/address", "resource_value": "127.0.0.1"}}]},
        "device_operational_status": 2,
        "device_endpoints": [{"endpoint_id": {"device_id": {"device_uuid": {"uuid": "GKE-QKD-NODE-02"}}, "endpoint_uuid": {"uuid": "QKD-INTF"}}, "name": "QKD-INTF", "endpoint_type": "qkd"}]
    }

    data['devices'].extend([opt1, opt2, qkd1, qkd2])

    # 3. Add Links
    opt_link = {
        "link_id": {"link_uuid": {"uuid": "GKE-OPT-ROAD-01_GKE-OPT-ROAD-02_OPT_LINK"}},
        "name": "GKE-OPT-ROAD-01_GKE-OPT-ROAD-02_OPT_LINK",
        "link_endpoint_ids": [
            {"device_id": {"device_uuid": {"uuid": "GKE-OPT-ROAD-01"}}, "endpoint_uuid": {"uuid": "LINE"}},
            {"device_id": {"device_uuid": {"uuid": "GKE-OPT-ROAD-02"}}, "endpoint_uuid": {"uuid": "LINE"}}
        ]
    }
    qkd_link = {
        "link_id": {"link_uuid": {"uuid": "GKE-QKD-NODE-01_GKE-QKD-NODE-02_QKD_LINK"}},
        "name": "GKE-QKD-NODE-01_GKE-QKD-NODE-02_QKD_LINK",
        "link_endpoint_ids": [
            {"device_id": {"device_uuid": {"uuid": "GKE-QKD-NODE-01"}}, "endpoint_uuid": {"uuid": "QKD-INTF"}},
            {"device_id": {"device_uuid": {"uuid": "GKE-QKD-NODE-02"}}, "endpoint_uuid": {"uuid": "QKD-INTF"}}
        ]
    }
    data['links'].extend([opt_link, qkd_link])

    # 4. Add QKD Service
    qkd_svc = {
        "service_id": {
            "context_id": {"context_uuid": {"uuid": "admin"}},
            "service_uuid": {"uuid": "SVC-QKD-SECURE-01"}
        },
        "name": "SVC-QKD-SECURE-01",
        "service_type": "SERVICETYPE_QKD",
        "service_status": {"service_status": 2},
        "service_endpoint_ids": [
            {"device_id": {"device_uuid": {"uuid": "GKE-QKD-NODE-01"}}, "endpoint_uuid": {"uuid": "QKD-INTF"}},
            {"device_id": {"device_uuid": {"uuid": "GKE-QKD-NODE-02"}}, "endpoint_uuid": {"uuid": "QKD-INTF"}}
        ]
    }
    data['services'].append(qkd_svc)

    with open('SuperDescriptor_Quantum.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("Quantum Stack added to SuperDescriptor_Quantum.json")

if __name__ == "__main__":
    add_quantum()
