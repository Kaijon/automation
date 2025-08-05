import paramiko
import time
import sys
import os
import socket

# --- Configuration ---
DEVICE_HOSTNAME = os.environ.get('DEVICE_IP')
DEVICE_USERNAME = os.environ.get('USERNAME')
DEVICE_PASSWORD = os.environ.get('PASSWORD')

MAX_TOTAL_WAIT_TIME_SECONDS = 300 # Max 5 minutes total wait for device to become ready
SSH_RECONNECT_TIMEOUT_SECONDS = 60 # Max 1 minute for SSH connection attempts
POLLING_INTERVAL_SECONDS = 1 # Check LED values every 3 seconds once SSH is connected

# --- SSH Connection Function ---
def connect_ssh(hostname, username, password, timeout):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Insecure for production; consider known_hosts

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            print(f"Attempting SSH connection to {username}@{hostname} (timeout: {timeout}s)...")
            client.connect(hostname, username=username, password=password, timeout=10) # Individual connection attempt timeout
            print("SSH connection established.")
            return client
        except (paramiko.AuthenticationException, socket.timeout) as e:
            print(f"Authentication failed or timed out: {e}. Retrying...", file=sys.stderr)
        except (paramiko.SSHException, socket.error) as e:
            print(f"SSH connection failed: {e}. Retrying...", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred during SSH connection: {e}. Retrying...", file=sys.stderr)

        time.sleep(POLLING_INTERVAL_SECONDS) # Wait before next connection attempt
    
    print(f"Failed to establish SSH connection within {timeout} seconds.", file=sys.stderr)
    return None

def wait_for_device_ready():
    if not DEVICE_USERNAME or not DEVICE_PASSWORD:
        print("Error: SSH credentials (DEV_USER, DEV_PASS) not provided as environment variables.", file=sys.stderr)
        return False

    ssh_client = None
    start_total_wait_time = time.time()

    try: # <--- THIS IS THE START OF THE TRY BLOCK FOR THE MAIN LOOP
        while time.time() - start_total_wait_time < MAX_TOTAL_WAIT_TIME_SECONDS:
            # 1. Ensure SSH connection is active
            if not ssh_client or not ssh_client.get_transport() or not ssh_client.get_transport().is_active():
                if ssh_client:
                    print("SSH client not active or disconnected. Attempting to reconnect...", file=sys.stderr)
                    ssh_client.close() # Ensure it's closed before retrying
                
                ssh_client = connect_ssh(DEVICE_HOSTNAME, DEVICE_USERNAME, DEVICE_PASSWORD, SSH_RECONNECT_TIMEOUT_SECONDS)
                if not ssh_client:
                    print(f"Could not establish SSH connection after {SSH_RECONNECT_TIMEOUT_SECONDS}s. Total elapsed: {int(time.time() - start_total_wait_time)}s. Retrying SSH connection...", file=sys.stderr)
                    time.sleep(POLLING_INTERVAL_SECONDS)
                    continue
            time.sleep(POLLING_INTERVAL_SECONDS)

        print(f"SSH not working", file=sys.stderr)
        return False
    except Exception as e: # <--- CATCH ANY OTHER EXCEPTIONS FROM THE MAIN LOOP
        print(f"An unexpected error occurred in main monitoring loop: {e}", file=sys.stderr)
        return False
    finally: # <--- THIS FINALLY BLOCK MUST BE INDENTED TO THE SAME LEVEL AS THE 'TRY' IT BELONGS TO
        if ssh_client:
            ssh_client.close()
            print("SSH connection closed.")

if __name__ == "__main__":
    if wait_for_device_ready():
        sys.exit(0)
    else:
        sys.exit(1)
