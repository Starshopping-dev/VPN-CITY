import os
import yaml
import socket
import subprocess
import logging
import random

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
    'Albania': 'AL', 'Algeria': 'DZ', 'Andorra': 'AD', 'Argentina': 'AR', 'Armenia': 'AM',
    'Australia': 'AU', 'Austria': 'AT', 'Azerbaijan': 'AZ', 'Bahamas': 'BS',
    'Bangladesh': 'BD', 'Belgium': 'BE', 'Belize': 'BZ', 'Bermuda': 'BM', 'Bhutan': 'BT',
    'Bolivia': 'BO', 'Bosnia and Herzegovina': 'BA', 'Brazil': 'BR',
    'Brunei Darussalam': 'BN', 'Bulgaria': 'BG', 'Cambodia': 'KH', 'Canada': 'CA',
    'Cayman Islands': 'KY', 'Chile': 'CL', 'Colombia': 'CO', 'Costa Rica': 'CR',
    'Croatia': 'HR', 'Cyprus': 'CY', 'Czech Republic': 'CZ', 'Denmark': 'DK',
    'Dominican Republic': 'DO', 'Ecuador': 'EC', 'Egypt': 'EG', 'El Salvador': 'SV',
    'Estonia': 'EE', 'Finland': 'FI', 'France': 'FR', 'Georgia': 'GE', 'Germany': 'DE',
    'Ghana': 'GH', 'Greece': 'GR', 'Greenland': 'GL', 'Guam': 'GU', 'Guatemala': 'GT',
    'Honduras': 'HN', 'Hong Kong': 'HK', 'Hungary': 'HU', 'Iceland': 'IS', 'India': 'IN',
    'Indonesia': 'ID', 'Ireland': 'IE', 'Isle of Man': 'IM', 'Israel': 'IL',
    'Italy': 'IT', 'Jamaica': 'JM', 'Japan': 'JP', 'Jersey': 'JE', 'Kazakhstan': 'KZ',
    'Kenya': 'KE', 'Latvia': 'LV', 'Lebanon': 'LB', 'Liechtenstein': 'LI',
    'Lithuania': 'LT', 'Luxembourg': 'LU', 'Malaysia': 'MY', 'Malta': 'MT',
    'Mexico': 'MX', 'Moldova': 'MD', 'Monaco': 'MC', 'Mongolia': 'MN',
    'Montenegro': 'ME', 'Morocco': 'MA', 'Myanmar': 'MM', 'Nepal': 'NP',
    'Netherlands': 'NL', 'New Zealand': 'NZ', 'Nigeria': 'NG', 'North Macedonia': 'MK',
    'Norway': 'NO', 'Pakistan': 'PK', 'Panama': 'PA', 'Papua New Guinea': 'PG',
    'Paraguay': 'PY', 'Peru': 'PE', 'Philippines': 'PH', 'Poland': 'PL',
    'Portugal': 'PT', 'Puerto Rico': 'PR', 'Romania': 'RO', 'Serbia': 'RS',
    'Singapore': 'SG', 'Slovakia': 'SK', 'Slovenia': 'SI', 'South Africa': 'ZA',
    'South Korea': 'KR', 'Spain': 'ES', 'Sri Lanka': 'LK', 'Sweden': 'SE',
    'Switzerland': 'CH', 'Taiwan': 'TW', 'Thailand': 'TH', 'Trinidad and Tobago': 'TT',
    'Turkey': 'TR', 'Ukraine': 'UA', 'United Arab Emirates': 'AE',
    'United Kingdom': 'GB', 'United States': 'US', 'Uruguay': 'UY',
    'Uzbekistan': 'UZ', 'Venezuela': 'VE', 'Vietnam': 'VN'
}

# Docker Compose header
docker_compose_content = """version: '3.8'

services:
"""

# Template for each service pair
service_template = """
  vpn_{index}:
    image: azinchen/nordvpn:latest
    privileged: true
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun
    environment:
      - USER={nordvpn_user}
      - PASS={nordvpn_pass}
      - COUNTRY={countries}
      - RANDOM_TOP=1000
      - RECREATE_VPN_CRON=*/3 * * * *
      - NETWORK={network}
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
    network_mode: service:vpn_{index}
    volumes:
      - ./data:/etc/tinyproxy
    depends_on:
      - vpn_{index}
    restart: unless-stopped
"""

# Network template
network_template = """
networks:
  vpn_net_{index}:
    driver: bridge
"""

# Tinyproxy config
tinyproxy_config = """User nobody
Group nobody
Port 8888
Timeout 600
LogFile "/etc/tinyproxy/tinyproxy.log"
LogLevel Info
MaxClients 100
StatFile "/etc/tinyproxy/stats.html"
DefaultErrorFile "/etc/tinyproxy/default.html"
ViaProxyName "tinyproxy"
BasicAuth badvibez forever
Allow 127.0.0.1/32
Allow 0.0.0.0/0
Listen 0.0.0.0
"""


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


def get_selected_countries(config):
    """Get country IDs based on selected countries in the config."""
    MAX_COUNTRIES = 5  # Maximum number of countries per container
    
    # Get list of working countries
    WORKING_COUNTRIES = {
        'Vietnam': '234',
        'Luxembourg': '126',
        'Germany': '81',
        'France': '74',
        'UK': '227',
        'US': '228',
        'Netherlands': '153',
        'Sweden': '208',
        'Switzerland': '209',
        'Spain': '202'
    }
    
    # If random is true, pick 5 random working countries
    if config['nordvpn']['countries'].get('random', False):
        selected_ids = random.sample(list(WORKING_COUNTRIES.values()), MAX_COUNTRIES)
        logging.info(f"Using random countries: {';'.join(selected_ids)}")
        return ';'.join(selected_ids)
    
    # Otherwise, get enabled countries from config
    enabled_countries = []
    for country, enabled in config['nordvpn']['countries'].items():
        if enabled and country in WORKING_COUNTRIES:
            enabled_countries.append(WORKING_COUNTRIES[country])
            if len(enabled_countries) >= MAX_COUNTRIES:
                break
    
    if not enabled_countries:
        # Fallback to 5 random working countries
        selected_ids = random.sample(list(WORKING_COUNTRIES.values()), MAX_COUNTRIES)
        return ';'.join(selected_ids)
    
    return ';'.join(enabled_countries)


def is_port_available(port):
    """Check if a port is available"""
    if port < 1 or port > 65535:
        logging.error(f"Invalid port number: {port}")
        return False
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', port))
        available = True
    except:
        logging.warning(f"Port {port} is already in use")
        available = False
    finally:
        sock.close()
    return available


def generate_proxies_with_config(config, output_dir="multi_proxy_setup"):
    try:
        # Load configurations
        nordvpn_user = config["nordvpn"]["user"]
        nordvpn_pass = config["nordvpn"]["pass"]
        network = config["nordvpn"]["network"]
        num_proxies = config["proxies"]["count"]
        base_port = config["proxies"]["base_port"]
        proxy_user = config["proxies"]["username"]
        proxy_pass = config["proxies"]["password"]

        # Create tinyproxy config with credentials from config
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
Allow 127.0.0.1/32
Allow 0.0.0.0/0
Listen 0.0.0.0
"""

        # Validate port range
        if base_port + num_proxies > 65535:
            raise ValueError("Port range exceeds maximum (65535)")

        # Check UFW if enabled
        if config["ufw"]["enable"]:
            try:
                # Try with sudo
                subprocess.run(["sudo", "ufw", "status"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                try:
                    # Try without sudo as fallback
                    subprocess.run(["ufw", "status"], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    logging.warning("UFW not available or not active. Skipping UFW rules.")
                    config["ufw"]["enable"] = False

        # Create directories with proper permissions
        try:
            os.makedirs(output_dir, exist_ok=True)
            data_dir = os.path.join(output_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            logs_dir = os.path.join(data_dir, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            # Set full permissions for data and logs directories
            os.chmod(data_dir, 0o777)
            os.chmod(logs_dir, 0o777)
            
            # Create and set permissions for tinyproxy log file
            log_file = os.path.join(logs_dir, "tinyproxy.log")
            open(log_file, 'a').close()  # Create if not exists
            os.chmod(log_file, 0o666)
        except Exception as e:
            logging.error(f"Failed to create directories: {e}")
            raise

        # Get countries with validation
        try:
            countries = get_selected_countries(config)
            if not countries:
                raise ValueError("No valid countries selected")
        except Exception as e:
            logging.error(f"Failed to get country IDs: {e}")
            raise

        # Check ports before proceeding
        available_ports = []
        for i in range(num_proxies):
            port = base_port + i
            if is_port_available(port):
                available_ports.append(port)
            else:
                logging.warning(f"Port {port} unavailable, skipping...")
        
        if not available_ports:
            raise ValueError(f"No available ports found starting from {base_port}")

        # Generate services with delays
        vpn_services = ""
        proxy_list = []
        
        for i, port in enumerate(available_ports, 1):
            # Add delay for each container except the first one
            delay = f"""
    depends_on:
      vpn_{i-1}:
        condition: service_healthy""" if i > 1 else ""

            current_service = service_template.format(
                index=i,
                port=port,
                nordvpn_user=nordvpn_user,
                nordvpn_pass=nordvpn_pass,
                network=network,
                countries=countries,
                delay=delay  # Add delay to template
            )
            
            vpn_services += current_service
            proxy_list.append(f"Proxy {i}: http://{proxy_user}:{proxy_pass}@{get_server_ip()}:{port}")

        # Write tinyproxy config
        os.makedirs(os.path.join(output_dir, "data"), exist_ok=True)
        with open(os.path.join(output_dir, "data", "tinyproxy.conf"), "w") as f:
            f.write(tinyproxy_config)

        # Write files with error handling
        try:
            with open(os.path.join(output_dir, "docker-compose.yml"), "w") as f:
                f.write(docker_compose_content + vpn_services + network_template)
            
            with open(os.path.join(output_dir, "proxies.txt"), "w") as f:
                f.write("\n".join(proxy_list))
        except Exception as e:
            logging.error(f"Failed to write configuration files: {e}")
            raise

        logging.info(f"Successfully generated {len(available_ports)} proxies")
        if len(available_ports) < num_proxies:
            logging.warning(f"Only {len(available_ports)} of {num_proxies} requested proxies could be created")

        # Set up UFW rules if enabled
        if config["ufw"]["enable"]:
            setup_ufw_rules(available_ports)

    except Exception as e:
        logging.error(f"Failed to generate proxy setup: {e}")
        raise


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
    """Validates the config structure."""
    if "nordvpn" not in config:
        raise ValueError("Missing nordvpn section in config")
    if "proxies" not in config:
        raise ValueError("Missing proxies section in config")
    if "ufw" not in config:
        raise ValueError("Missing ufw section in config")
    
    # Check nordvpn section
    required_nordvpn = ["user", "pass", "network", "countries"]
    for key in required_nordvpn:
        if key not in config["nordvpn"]:
            raise ValueError(f"Missing {key} in nordvpn section")
    
    return True


if __name__ == "__main__":
    # Load configuration from config.yaml
    config = load_config()

    # Generate proxies and UFW rules
    generate_proxies_with_config(config)
