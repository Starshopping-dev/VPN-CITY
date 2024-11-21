import os
import yaml
import socket
import subprocess


def load_config(config_path="config.yaml"):
    """
    Load configuration from config.yaml.
    """
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def get_server_ip():
    """
    Get the IP address of the server running the script.
    """
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def generate_proxies_with_config(config, output_dir="multi_proxy_setup"):
    """
    Generate a docker-compose.yml for Tinyproxy + NordVPN pairs using configurations from a YAML file,
    and set up UFW rules if enabled.
    """
    # Load configurations
    nordvpn_user = config["nordvpn"]["user"]
    nordvpn_pass = config["nordvpn"]["pass"]
    network = config["nordvpn"]["network"]
    num_proxies = config["proxies"]["count"]
    base_port = config["proxies"]["base_port"]
    proxy_user = config["proxies"]["username"]
    proxy_pass = config["proxies"]["password"]
    enable_ufw = config["ufw"]["enable"]

    # Get server IP
    server_ip = get_server_ip()

    # Create output directory and tinyproxy config directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "data"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "data", "logs"), exist_ok=True)

    # Create tinyproxy config FIRST
    tinyproxy_config = f"""User nobody
Group nobody
Port 8888
Timeout 600
LogFile "/etc/tinyproxy/logs/tinyproxy.log"
LogLevel Info
MaxClients 100
StatFile "/etc/tinyproxy/stats.html"
DefaultErrorFile "/etc/tinyproxy/default.html"
ViaProxyName "tinyproxy"
BasicAuth {proxy_user} {proxy_pass}

# Allow connections from the local machine
Allow 127.0.0.1/32

# Allow all external connections
Allow 0.0.0.0/0

# Listen on all interfaces
Listen 0.0.0.0
"""

    # Write tinyproxy config
    config_path = os.path.join(output_dir, "data", "tinyproxy.conf")
    with open(config_path, "w") as f:
        f.write(tinyproxy_config)

    # Docker Compose header
    docker_compose_content = """
version: '3.9'

services:
"""

    # Template for Tinyproxy + NordVPN pair
    service_template = """
  nordvpn_{index}:
    image: azinchen/nordvpn:latest
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun
    environment:
      - USER={nordvpn_user}
      - PASS={nordvpn_pass}
      - COUNTRY=234;126
      - NETWORK={network}
      - RANDOM_TOP=1000
      - RECREATE_VPN_CRON=*/3 * * * *
      - OPENVPN_OPTS=--mute-replay-warnings
    ports:
      - "{port}:8888"
    restart: unless-stopped
    networks:
      - vpn_net_{index}
    logging:
      driver: "json-file"
      options:
        max-size: "1m"

  tinyproxy_{index}:
    image: vimagick/tinyproxy
    container_name: tinyproxy_{index}
    network_mode: service:nordvpn_{index}
    volumes:
      - ./data:/etc/tinyproxy
    depends_on:
      - nordvpn_{index}
    restart: unless-stopped
"""

    # Network template
    network_template = """
networks:
{networks}
"""

    # Generate services and networks
    vpn_services = ""
    networks = ""
    proxy_list = []
    port_list = []
    for i in range(1, num_proxies + 1):
        port = base_port + i - 1
        vpn_services += service_template.format(
            index=i,
            port=port,
            nordvpn_user=nordvpn_user,
            nordvpn_pass=nordvpn_pass,
            network=network,
            proxy_user=proxy_user,
            proxy_pass=proxy_pass,
        )
        networks += f"  vpn_net_{i}:\n    driver: bridge\n"
        proxy_list.append(f"Proxy {i}: http://{proxy_user}:{proxy_pass}@{server_ip}:{port}")
        port_list.append(port)

    docker_compose_content += vpn_services
    docker_compose_content += network_template.format(networks=networks)

    # Write to docker-compose.yml
    docker_compose_path = os.path.join(output_dir, "docker-compose.yml")
    with open(docker_compose_path, "w") as f:
        f.write(docker_compose_content)

    print(f"Docker Compose file generated at: {docker_compose_path}")

    # Write proxies to a file
    proxies_file_path = os.path.join(output_dir, "proxies.txt")
    with open(proxies_file_path, "w") as f:
        f.write("\n".join(proxy_list))

    print(f"Proxy list generated at: {proxies_file_path}")

    # Set up UFW rules if enabled
    if enable_ufw:
        setup_ufw_rules(port_list)

    # Create tinyproxy config
    tinyproxy_config = f"""User nobody
Group nobody
Port 8888
Timeout 600
LogFile "/etc/tinyproxy/tinyproxy.log"
LogLevel Info
MaxClients 100
StatFile "/etc/tinyproxy/stats.html"
DefaultErrorFile "/etc/tinyproxy/default.html"
ViaProxyName "tinyproxy"
BasicAuth {proxy_user} {proxy_pass}

# Allow connections from the local machine
Allow 127.0.0.1/32

# Allow all external connections
Allow 0.0.0.0/0

# Listen on all interfaces
Listen 0.0.0.0
"""

    # Write tinyproxy config
    config_path = os.path.join(output_dir, "data", "tinyproxy.conf")
    with open(config_path, "w") as f:
        f.write(tinyproxy_config)


def setup_ufw_rules(port_list):
    """
    Set up UFW rules for the given list of ports.
    """
    print("Setting up UFW rules...")
    try:
        for port in port_list:
            # Allow each port in UFW
            subprocess.run(["sudo", "ufw", "allow", f"{port}/tcp"], check=True)
        # Reload UFW to apply changes
        subprocess.run(["sudo", "ufw", "reload"], check=True)
        print("UFW rules set up successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up UFW rules: {e}")


if __name__ == "__main__":
    # Load configuration from config.yaml
    config = load_config()

    # Generate proxies and UFW rules
    generate_proxies_with_config(config)
