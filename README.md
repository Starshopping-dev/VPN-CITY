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

1. Run `python generate.py` to create your proxy setup
2. Navigate to the generated `multi_proxy_setup` directory
3. Start your proxies with `docker-compose up -d`
4. Find your proxy list in `proxies.txt`

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

## License

MIT License

## Disclaimer

This tool is for legitimate use only. Users are responsible for complying with all applicable laws and NordVPN's terms of service.