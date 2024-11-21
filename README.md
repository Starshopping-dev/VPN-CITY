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
   This creates:
   - Docker compose configuration
   - Tinyproxy settings
   - UFW rules if enabled

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

## Configuration

### Basic Setup
Create a `config.yaml` file with your settings:

## Country Configuration

### Basic Configuration
The config.yaml file supports two modes for country selection:

1. Random Mode:
```yaml
nordvpn:
  countries:
    random: true    # Will use all available countries
    # Other country settings are ignored when random is true
```

2. Specific Countries Mode:
```yaml
nordvpn:
  countries:
    random: false   # Must be false to use specific countries
    United States: true   # Will use US servers
    Vietnam: true        # Will use Vietnam servers
    France: false       # Won't use French servers
    # etc...
```

### Available Countries
All available countries are listed in config.yaml. To enable a country:
1. Set `random: false`
2. Set desired countries to `true`
3. Leave unwanted countries as `false`

### Updating Country List
To get the latest country list:
```bash
python update_countries.py
```
This will:
- Update config.yaml with the latest available countries
- Preserve your existing country selections
- Create a backup of your current config

### Example Configuration
```yaml
nordvpn:
  user: "your_nordvpn_user"
  pass: "your_nordvpn_pass"
  network: "your_ip/32"
  countries:
    random: false
    United States: true
    United Kingdom: true
    Japan: true
    # Other countries set to false...

proxies:
  count: 20
  base_port: 8880
  username: "badvibez"
  password: "forever"
```
