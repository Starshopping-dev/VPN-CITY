# Multi-Proxy NordVPN Setup

This project automates the creation of multiple proxy servers, each running through its own NordVPN connection. It uses Docker containers to create isolated pairs of NordVPN + Tinyproxy servers.

## Features

- Creates multiple proxy servers, each with a unique IP address
- Each proxy is secured with basic authentication
- Automatic UFW firewall rule configuration
- Isolated Docker networks for each proxy pair
- Easy configuration through YAML file

## Prerequisites

- Docker and Docker Compose
- Python 3.x
- NordVPN subscription
- UFW (Uncomplicated Firewall) - Optional
- PyYAML (`pip install pyyaml`)

## Installation

1. Clone this repository
2. Create a config.yaml file in the project root with your NordVPN credentials and desired settings:
   - NordVPN username and password
   - Number of proxies to create
   - Starting port number
   - UFW configuration preference

## Usage

1. Update country list and config:
   ```bash
   python update_countries.py
   ```
   This will:
   - Create/update config.yaml with latest country list
   - Preserve any existing country settings
   - Create a backup of your existing config
   - Note: This only updates the configuration files

2. Configure settings in config.yaml:
   - Add your NordVPN credentials
   - Set your whitelisted IP in network
   - Enable desired countries (set to true)
   - Set random: true to use all countries
   - Configure number of proxies and ports

3. Generate proxy setup:
   ```bash
   python generate.py
   ```
   This is REQUIRED after:
   - Running update_countries.py
   - Making any changes to config.yaml
   - Changing enabled countries
   
   It will:
   - Create new docker-compose.yml with your settings
   - Set up tinyproxy configuration
   - Configure UFW rules if enabled
   - Create fresh proxy list

4. Start the proxies:
   ```bash
   cd multi_proxy_setup
   docker-compose up -d
   ```

Your proxies will be listed in `multi_proxy_setup/proxies.txt`

## Proxy Format

Your proxies will be accessible at:
- Format: `http://badvibez:forever@<your-server-ip>:<port>`
- Ports start from your configured base_port
- Each proxy has its own unique IP through NordVPN

## Container Structure

Each proxy setup includes:
- A NordVPN container for VPN connection
- A Tinyproxy container for proxy service
- An isolated Docker network
- Automatic port forwarding

## Security Notes

- Basic authentication enabled by default
- UFW rules automatically configured
- Isolated Docker networks prevent cross-container traffic
- All traffic routed through NordVPN
- Credentials can be customized in the generator script

## Troubleshooting

1. Container Issues:
   - Verify NordVPN credentials
   - Check Docker permissions
   - Ensure ports aren't in use

2. Connection Issues:
   - Verify UFW rules
   - Check Docker network connectivity
   - Confirm NordVPN server status

## Contributing

Contributions welcome! Please:
- Fork the repository
- Create a feature branch
- Submit a pull request

## Special Thanks

Special thanks to [@azinchen](https://github.com/azinchen/nordvpn) for creating and maintaining the NordVPN Docker image that makes this project possible.

Special thanks to [@Flechaa](https://github.com/Flechaa/Flechaa) for his knowledge and guidance throughout this project.

## License

MIT License

## Disclaimer

This tool is for legitimate use only. Users are responsible for complying with all applicable laws and NordVPN's terms of service.

## Configuration Structure

The config.yaml file is structured with countries at the top for automatic updates:

```yaml
nordvpn:
  countries:
    random: false  # Override: if true, uses all countries
    Albania: false
    Algeria: false
    # ... [all countries listed alphabetically]
    Vietnam: false
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

### Important Notes:
- Countries must stay at the top of the config for auto-updates to work
- All countries are listed alphabetically
- Default to false is safer
- Random mode overrides individual country settings
- Country settings are preserved during updates
