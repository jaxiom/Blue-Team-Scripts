#!/usr/bin/env python3
import os
import subprocess
import getpass

def print_banner():
    print("""
          
██╗   ██╗██████╗ ███████╗███████╗███████╗███╗   ██╗██████╗ ███████╗██████╗ 
██║   ██║██╔══██╗██╔════╝██╔════╝██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗
██║   ██║██║  ██║█████╗  █████╗  █████╗  ██╔██╗ ██║██║  ██║█████╗  ██████╔╝
██║   ██║██║  ██║██╔══╝  ██╔══╝  ██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
╚██████╔╝██████╔╝███████╗██║     ███████╗██║ ╚████║██████╔╝███████╗██║  ██║
 ╚═════╝ ╚═════╝ ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝
                                                                           
    """)
    print("WARNING: This script needs to be run by an admin to work properly.\n")

def menu():
    print("Please select an option:")
    print("  1 - Run Initial Access Script")
    print("  2 - Install Monitor Software")
    print("  3 - Monitor System")
    choice = input("Enter your choice (1-3): ")
    return choice

def run_initial_access():
    print("Running Initial Access Script...")
    # Remove non-essential services
    services_to_keep = input("Enter essential services to keep (comma-separated, e.g., 'dns,mail,ssh'): ")
    keep_list = services_to_keep.split(',')
    print("Stopping non-essential services...")
    essential_services = ['systemd-resolve', 'postfix', 'ssh'] + keep_list
    services = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager']).decode('utf-8')
    for service in services.split('\n'):
        if not any(essential in service for essential in essential_services):
            service_name = service.split()[0]
            subprocess.call(['systemctl', 'stop', service_name])
            subprocess.call(['systemctl', 'disable', service_name])

    # Remove non-essential users
    current_user = getpass.getuser()
    print("Removing non-essential users...")
    users = subprocess.check_output('cut -d: -f1 /etc/passwd', shell=True).decode().split()
    for user in users:
        if user not in ['root', 'daemon', 'bin', 'sys', current_user] + essential_services:
            subprocess.call(['userdel', '-r', user])

    # Set up firewall
    allowed_services = input("Enter services to allow through the firewall (e.g., 'http,https,ssh'): ")
    subprocess.call(['ufw', 'reset'])
    for service in allowed_services.split(','):
        subprocess.call(['ufw', 'allow', service])
    subprocess.call(['ufw', 'enable'])

    # Remove all ssh keys
    print("Removing all SSH keys...")
    subprocess.call(['rm', '-rf', '/home/*/.ssh'])
    subprocess.call(['rm', '-rf', '/root/.ssh'])

    print("Initial access configuration is complete.")

def install_monitor_software():
    print("Installing monitor software...")

def monitor_system():
    print("Monitoring system...")

def main():
    print_banner()
    while True:
        choice = menu()
        if choice == '1':
            run_initial_access()
        elif choice == '2':
            install_monitor_software()
        elif choice == '3':
            monitor_system()
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
