# Multi-Proxy NordVPN Setup

Creates multiple proxy servers using NordVPN and Tinyproxy. Each proxy uses a different VPN connection for better anonymity.

## Prerequisites
- Docker and Docker Compose
- Python 3.x
- Active NordVPN subscription
- PyYAML (`pip install pyyaml`)
- UFW firewall (optional, Linux only)

## Quick Start

1. Copy `config_template.yaml` to `config.yaml` and edit with your details:
```yaml
nordvpn:
  user: "your_nordvpn_email"
  pass: "your_nordvpn_password"
  network: "your_ip/32"  # Example: "192.168.1.100/32"
  countries:
    random: true  # Set to true to use random countries
    # Or enable specific countries (true/false):
    Vietnam: false
    Luxembourg: true
    Germany: true
    # etc...

proxies:
  count: 5  # Number of proxies you want to create
  base_port: 8880  # Starting port number
  username: "proxy_user"  # Username for proxy authentication
  password: "proxy_pass"  # Password for proxy authentication

ufw:
  enable: false  # Set to true only if using UFW on Linux
```

2. Run the generator:
```bash
python generate.py
```

3. Start the proxies:
```bash
cd multi_proxy_setup
docker-compose up -d
```

4. Find your proxy list in `multi_proxy_setup/proxies.txt`

## Proxy Format
Your proxies will be available in this format:
```
username:password@your_ip:port
```

## Important Notes
- Each proxy uses 5 different countries for IP rotation
- Containers start sequentially to avoid NordVPN connection issues
- Default ports start at 8880 and increment (8880, 8881, 8882, etc.)
- All proxies use authentication for security
- The script checks for port availability before assigning them

## Troubleshooting
- If containers fail to start, check your NordVPN credentials
- Make sure the specified ports are not in use
- Verify your IP address in the network setting
- Check Docker logs if any issues occur: `docker-compose logs`
