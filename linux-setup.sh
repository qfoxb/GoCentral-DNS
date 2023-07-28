#!/bin/bash
git clone https://github.com/qfoxb/GoCentral-DNS.git
cd GoCentral-DNS
sudo apt install python3-pip python3 --yes
pip3 install -r requirements.txt
python3 GoCentral-DNS-Server.py
