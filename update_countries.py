#!/usr/bin/env python3
import sys
import yaml
import shutil
from datetime import datetime
import os
from generate import BUILTIN_COUNTRIES  # Import the country list
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_latest_countries():
    """
    Get the latest country list.
    """
    return BUILTIN_COUNTRIES  # Use the same list as generate.py

def backup_config():
    """
    Create a backup of existing config
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copy2('config.yaml', f'config.yaml.backup_{timestamp}')
        print(f"Created backup: config.yaml.backup_{timestamp}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")

def update_config_file(countries):
    """
    Update config.yaml with latest country list while preserving existing settings
    """
    try:
        if not os.path.exists('config.yaml'):
            print("No existing config.yaml found, creating new one...")
            config = {'nordvpn': {'countries': {}}, 'proxies': {}, 'ufw': {}}
        else:
            backup_config()
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
        
        # Get existing country settings
        existing_config = config.get('nordvpn', {}).get('countries', {})
        
        # Create new countries dict with existing settings preserved
        new_countries = {
            'random': existing_config.get('random', False),
        }
        
        # Add all countries, preserving existing settings if they exist
        for country in countries.keys():
            new_countries[country] = existing_config.get(country, False)
        
        # Update config
        config['nordvpn']['countries'] = new_countries
        
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("Successfully updated config.yaml with latest country list")
        print("Preserved existing country settings")
        print("\nNext steps:")
        print("1. Edit config.yaml to enable desired countries")
        print("2. cd multi_proxy_setup")
        print("3. docker-compose up -d")
        return config  # Return the config for use in update_docker_compose
    except Exception as e:
        print(f"Error updating config: {e}")
        print("Your original config.yaml is preserved in the backup")
        return None  # Return None on error

def update_docker_compose(countries, config):
    """Update docker-compose.yml with latest country IDs"""
    try:
        docker_compose_path = "multi_proxy_setup/docker-compose.yml"
        if os.path.exists(docker_compose_path):
            logging.info("Updating docker-compose.yml with latest country IDs...")
            
            # Get enabled countries
            enabled_ids = [
                str(id) for country, id in countries.items() 
                if config["nordvpn"]["countries"].get(country, False)
            ]
            
            if not enabled_ids:
                logging.warning("No countries are enabled in config.yaml. Skipping docker-compose update.")
                return
            
            country_string = ';'.join(enabled_ids)
            
            # Read file
            with open(docker_compose_path, 'r') as f:
                content = f.read()
            
            # Check if COUNTRY variable exists
            if "COUNTRY=" not in content:
                raise ValueError("COUNTRY environment variable not found in docker-compose.yml")
            
            # Update COUNTRY environment variable
            import re
            new_content = re.sub(
                r'COUNTRY=.*\n',
                f'COUNTRY={country_string}\n',
                content
            )
            
            # Write updated content
            with open(docker_compose_path, 'w') as f:
                f.write(new_content)
            
            logging.info("Docker compose file updated with latest country IDs")
    except Exception as e:
        logging.error(f"Could not update docker-compose.yml: {e}")

if __name__ == "__main__":
    countries = get_latest_countries()
    config = update_config_file(countries)  # Store the returned config
    if config:  # Only update docker if we have a valid config
        update_docker_compose(countries, config) 