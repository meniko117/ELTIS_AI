import os
import subprocess
import requests

# Path to your OpenVPN installation
openvpn_path = "C:\\Program Files\\OpenVPN\\bin\\openvpn.exe"  # Update this path for your system

# Path where .ovpn files are stored
config_path = "path_to_your_vpn_configs"  # Update this path

# List of countries and corresponding config file names
servers = {
    "US": "us_server.ovpn",
    "UK": "uk_server.ovpn",
    "Germany": "germany_server.ovpn",
    "France": "france_server.ovpn",
    "Japan": "japan_server.ovpn"
}

def connect_to_vpn(country):
    if country not in servers:
        print(f"Country {country} is not in the list.")
        return

    vpn_file = os.path.join(config_path, servers[country])
    
    if not os.path.exists(vpn_file):
        print(f"VPN configuration file for {country} not found!")
        return

    print(f"Connecting to {country} server...")
    
    # Build the command
    command = [openvpn_path, "--config", vpn_file]
    
    # Connect to VPN
    subprocess.run(command, shell=True)

def disconnect_vpn():
    print("Disconnecting VPN...")
    subprocess.run("taskkill /F /IM openvpn.exe", shell=True)

if __name__ == "__main__":
    print("Available countries:")
    for country in servers:
        print(country)

    chosen_country = input("Enter the country code to connect: ").upper()
    
    connect_to_vpn(chosen_country)

    # To disconnect the VPN, you can call the disconnect_vpn function.
    # Uncomment the line below to disconnect after connecting.
    # disconnect_vpn()
