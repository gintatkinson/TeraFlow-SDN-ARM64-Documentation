#!/bin/bash
set -e

echo "Updating apt..."
sudo apt-get update -y

echo "Installing prerequisites..."
sudo apt-get install -y python3-pip python3-venv build-essential gettext curl jq

echo "Installing MicroK8s..."
sudo snap install microk8s --classic --channel=1.28/stable

echo "Setting permissions..."
sudo usermod -a -G microk8s ubuntu
sudo mkdir -p /home/ubuntu/.kube
sudo chown -f -R ubuntu /home/ubuntu/.kube

echo "Enabling MicroK8s addons (DNS, Storage, Registry)..."
# Using sg to run microk8s commands with the microk8s group
sudo -H -u ubuntu bash -c 'sg microk8s -c "microk8s enable dns hostpath-storage registry ingress"'

echo "Creating python alias..."
sudo ln -sf /usr/bin/python3 /usr/bin/python

echo "Provisioning complete!"
