# Multi-Proxy NordVPN Setup

Creates multiple proxy servers using NordVPN and Tinyproxy.

## Prerequisites
- Docker and Docker Compose
- Python 3.x
- NordVPN subscription
- PyYAML (`pip install pyyaml`)

## Usage

1. Edit config.yaml with your settings:
   ```yaml
   nordvpn:
     countries:
       random: true
     user: "your_nordvpn_user"
     pass: "your_nordvpn_pass"
     network: "your_ip/32"

   proxies:
     count: 20
     base_port: 8880
     username: "badvibez"
     password: "forever"

   ufw:
     enable: true
   ```

2. Generate and start proxies:
   ```bash
   python generate.py
   cd multi_proxy_setup
   docker-compose up -d
   ```

Your proxies will be listed in `multi_proxy_setup/proxies.txt`
