#!/bin/bash
echo "Change folder"
cd yeelightEdge/
echo "Stop service"
systemctl stop yeelightEdge.service
echo "Install virtual python environment"
python3 -m venv venv
source venv/bin/activate
echo "Install python requirements"
python3 -m pip install -r ./requirements.txt
echo "Copy service"
cp yeelightEdge.service /etc/systemd/system/
echo "Enable service"
systemctl enable yeelightEdge.service
echo "Start service"
systemctl start yeelightEdge.service
echo "Status of service"
systemctl status yeelightEdge.service