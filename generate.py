import os
import yaml
import socket

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
    Generate a docker-compose.yml for Tinyproxy + NordVPN pairs using configurations from a YAML file.
    """
    # Load configurations
    nordvpn_user = config["nordvpn"]["user"]
    nordvpn_pass = config["nordvpn"]["pass"]
    network = config["nordvpn"]["network"]
    num_proxies = config["proxies"]["count"]
    base_port = config["proxies"]["base_port"]
    proxy_user = config["proxies"]["username"]
    proxy_pass = config["proxies"]["password"]

    # Get server IP
    server_ip = get_server_ip()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Docker Compose header
    docker_compose_content = """
version: '3.9'

services:
"""

    # Template for Tinyproxy + NordVPN pair
    service_template = """
  vpn{index}:
    image: azinchen/nordvpn:latest
    container_name: vpn{index}
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun
    environment:
      - USER={nordvpn_user}
      - PASS={nordvpn_pass}
      - NETWORK={network}
    networks:
      - vpn_net_{index}

  tinyproxy{index}:
    image: vimagick/tinyproxy
    container_name: tinyproxy{index}
    networks:
      - vpn_net_{index}
    ports:
      - "{port}:8888"
    environment:
      - BasicAuth={proxy_user}:{proxy_pass}
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
    for i in range(1, num_proxies + 1):
        port = base_port + i - 1
        vpn_services += service_template.format(
            index=i, port=port, nordvpn_user=nordvpn_user, nordvpn_pass=nordvpn_pass, network=network,
            proxy_user=proxy_user, proxy_pass=proxy_pass
        )
        networks += f"  vpn_net_{i}:\n    driver: bridge\n"
        proxy_list.append(f"Proxy {i}: http://{proxy_user}:{proxy_pass}@{server_ip}:{port}")

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

# Example usage
if __name__ == "__main__":
    # Load configuration from config.yaml
    config = load_config()

    # Generate proxies
    generate_proxies_with_config(config)
