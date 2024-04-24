#!/usr/bin/env python3
import os
import subprocess
import getpass
import sys

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

def confirm_installation(software_name):
    response = input(f"Do you want to install and configure {software_name}? (y/n): ")
    return response.lower() == 'y'

def install_monitor_software():
    print("Installing monitor software...")
    subprocess.call(['sudo', 'apt-get', 'update'])

    if confirm_installation("ClamAV"):
        subprocess.call(['sudo', 'apt-get', 'install', '-y', 'clamav', 'clamav-daemon'])
        print("Setting up ClamAV...")
        subprocess.call(['sudo', 'systemctl', 'stop', 'clamav-freshclam'])
        subprocess.call(['sudo', 'freshclam'])
        subprocess.call(['sudo', 'systemctl', 'start', 'clamav-freshclam'])

    if confirm_installation("Fail2Ban"):
        subprocess.call(['sudo', 'apt-get', 'install', '-y', 'fail2ban'])
        print("Setting up Fail2Ban...")
        subprocess.call(['sudo', 'cp', '/etc/fail2ban/jail.conf', '/etc/fail2ban/jail.local'])
        with open('/etc/fail2ban/jail.local', 'a') as f:
            f.write("\n[sshd]\nenabled = true\n")
        subprocess.call(['sudo', 'systemctl', 'restart', 'fail2ban'])

    if confirm_installation("Lynis"):
        subprocess.call(['sudo', 'apt-get', 'install', '-y', 'lynis'])

    if confirm_installation("AIDE"):
        subprocess.call(['sudo', 'apt-get', 'install', '-y', 'aide', 'aide-common'])
        print("Initializing AIDE...")
        subprocess.call(['sudo', 'aideinit'])
        subprocess.call(['sudo', 'mv', '/var/lib/aide/aide.db.new', '/var/lib/aide/aide.db'])

def monitor_system():
    print("Starting system overwatch...")
    # ClamAV Scan
    print("Initiating ClamAV scan...")
    subprocess.call(['clamscan', '-r', '/'])

    # Lynis Audit in a new terminal
    print("Running Lynis audit in a new terminal...")
    subprocess.call(['gnome-terminal', '--', 'lynis', 'audit', 'system'])

def run_initial_access():
    print("Running Initial Access Script...")
    # Uninstall and reinstall PAM
    print("Uninstalling and reinstalling PAM...")
    subprocess.call(['sudo', 'apt-get', 'remove', '--purge', '-y', 'libpam0g', 'libpam-modules', 'libpam-modules-bin'])
    subprocess.call(['sudo', 'apt-get', 'install', '-y', 'libpam0g', 'libpam-modules', 'libpam-modules-bin'])

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

def menu():
    print("Please select an option:")
    print("  1 - Run Initial Access Script")
    print("  2 - Install Monitor Software")
    print("  3 - Start System Audit")
    choice = input("Enter your choice (1-3): ")
    return choice

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
        elif choice == '4':
            print("Exiting...")
            sys.exit(1)
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
