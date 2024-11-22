# Multi-Proxy NordVPN Setup

Creates multiple proxy servers using NordVPN and Tinyproxy.

## Prerequisites
- Docker and Docker Compose
- Python 3.x
- NordVPN service credentials
- PyYAML (`pip install pyyaml`)
- UFW firewall (optional)

## Quick Start

1. Edit config.yaml with your details:
```yaml
nordvpn:
  countries:
    random: true  # Will pick 5 random countries from working list
    Vietnam: true
    Luxembourg: true
    Germany: true
    France: true
    UK: true
    US: true
    Netherlands: true
    Sweden: true
    Switzerland: true
    Spain: true
  user: "your_service_token"  # NordVPN service credentials
  pass: "your_service_password"
  network: "your_ip/32"

proxies:
  count: 6  # Will be capped at 6 if set higher
  base_port: 8880
  username: "proxy_user"
  password: "proxy_pass"

ufw:
  enable: true  # Set to false to skip UFW rules
```

2. Run:
```bash
python generate.py
cd multi_proxy_setup
docker-compose up -d
```

3. Your proxies will be in `multi_proxy_setup/proxies.txt` in format:
```
ip:port:username:password
```

## Notes
- Maximum 6 proxies (NordVPN connection limit)
- Each proxy rotates between 2 countries (reduced from 5 for stability)
- Uses NordVPN service credentials (not regular account login)
- Ports start at base_port (default 8880)
