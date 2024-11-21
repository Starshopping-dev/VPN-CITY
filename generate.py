import os
import yaml
import socket
import subprocess

# Built-in country data
BUILTIN_COUNTRIES = {
    'Albania': 2, 'Algeria': 3, 'Andorra': 5, 'Argentina': 10, 'Armenia': 11,
    'Australia': 13, 'Austria': 14, 'Azerbaijan': 15, 'Bahamas': 16,
    'Bangladesh': 18, 'Belgium': 21, 'Belize': 22, 'Bermuda': 24, 'Bhutan': 25,
    'Bolivia': 26, 'Bosnia and Herzegovina': 27, 'Brazil': 30,
    'Brunei Darussalam': 32, 'Bulgaria': 33, 'Cambodia': 36, 'Canada': 38,
    'Cayman Islands': 40, 'Chile': 43, 'Colombia': 47, 'Costa Rica': 52,
    'Croatia': 54, 'Cyprus': 56, 'Czech Republic': 57, 'Denmark': 58,
    'Dominican Republic': 61, 'Ecuador': 63, 'Egypt': 64, 'El Salvador': 65,
    'Estonia': 68, 'Finland': 73, 'France': 74, 'Georgia': 80, 'Germany': 81,
    'Ghana': 82, 'Greece': 84, 'Greenland': 85, 'Guam': 88, 'Guatemala': 89,
    'Honduras': 96, 'Hong Kong': 97, 'Hungary': 98, 'Iceland': 99, 'India': 100,
    'Indonesia': 101, 'Ireland': 104, 'Isle of Man': 243, 'Israel': 105,
    'Italy': 106, 'Jamaica': 107, 'Japan': 108, 'Jersey': 244, 'Kazakhstan': 110,
    'Kenya': 111, 'Latvia': 119, 'Lebanon': 120, 'Liechtenstein': 124,
    'Lithuania': 125, 'Luxembourg': 126, 'Malaysia': 131, 'Malta': 134,
    'Mexico': 140, 'Moldova': 142, 'Monaco': 143, 'Mongolia': 144,
    'Montenegro': 146, 'Morocco': 147, 'Myanmar': 149, 'Nepal': 152,
    'Netherlands': 153, 'New Zealand': 156, 'Nigeria': 159, 'North Macedonia': 128,
    'Norway': 163, 'Pakistan': 165, 'Panama': 168, 'Papua New Guinea': 169,
    'Paraguay': 170, 'Peru': 171, 'Philippines': 172, 'Poland': 174,
    'Portugal': 175, 'Puerto Rico': 176, 'Romania': 179, 'Serbia': 192,
    'Singapore': 195, 'Slovakia': 196, 'Slovenia': 197, 'South Africa': 200,
    'South Korea': 114, 'Spain': 202, 'Sri Lanka': 203, 'Sweden': 208,
    'Switzerland': 209, 'Taiwan': 211, 'Thailand': 214, 'Trinidad and Tobago': 218,
    'Turkey': 220, 'Ukraine': 225, 'United Arab Emirates': 226,
    'United Kingdom': 227, 'United States': 228, 'Uruguay': 230,
    'Uzbekistan': 231, 'Venezuela': 233, 'Vietnam': 234
}

# Country codes mapping
COUNTRY_CODES = {
    'Albania': 'AL', 'Algeria': 'DZ', 'Andorra': 'AD', 'Argentina': 'AR',
    # ... add all country codes ...
    'Vietnam': 'VN'
}


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
    try:
        # Try to get the actual server IP rather than localhost
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # Fallback to hostname method
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)


def get_random_countries(config):
    """
    Get random country IDs based on configuration.
    """
    if config["nordvpn"]["countries"].get("random", False):
        return ';'.join(map(str, BUILTIN_COUNTRIES.values()))
    
    available_ids = [
        BUILTIN_COUNTRIES[country] 
        for country, enabled in config["nordvpn"]["countries"].items() 
        if enabled and country in BUILTIN_COUNTRIES and country != "random"
    ]
    
    return ';'.join(map(str, available_ids))


def is_port_available(port):
    """
    Check if a port is available on localhost.
    Returns True if port is available, False if in use.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


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
      - COUNTRY={countries}
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
    
    # Check port availability before proceeding
    for i in range(num_proxies):
        port = base_port + i
        if not is_port_available(port):
            raise ValueError(f"Port {port} is already in use. Please choose a different base_port.")
    
    # Get countries string ONCE before the loop
    countries = get_random_countries(config)
    
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
            countries=countries,  # Use the same countries string
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


def validate_config(config):
    """
    Validates the config structure.
    """
    required_keys = ["nordvpn", "proxies", "ufw"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key in config.yaml: {key}")
    return True


def get_country_ids(config):
    """
    Returns a semicolon-separated string of country IDs
    based on the 'random' setting and enabled countries in the config.
    """
    if config["nordvpn"]["countries"].get("random", False):
        return ';'.join(map(str, BUILTIN_COUNTRIES.values()))

    enabled_ids = [
        BUILTIN_COUNTRIES[country]
        for country, enabled in config["nordvpn"]["countries"].items()
        if enabled and country in BUILTIN_COUNTRIES and country != "random"
    ]

    return ';'.join(map(str, enabled_ids))


if __name__ == "__main__":
    # Load configuration from config.yaml
    config = load_config()

    # Generate proxies and UFW rules
    generate_proxies_with_config(config)
