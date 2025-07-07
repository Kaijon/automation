import requests
import os

# Configuration
FIRMWARE_SERVER_URL = "http://192.168.5.52:8081" # Confirmed correct port
UPLOAD_ENDPOINT = "/Upgrade" # Confirmed from your JavaScript
FIRMWARE_FILE_PATH = "/home/jenkins/ca42-automation/test.img" # Adjust to your downloaded firmware path
FILE_INPUT_NAME = "image_file" # Confirmed from your HTML <input type="file" name="image_file">

def upload_firmware():
    if not os.path.exists(FIRMWARE_FILE_PATH):
        print(f"Error: Firmware file not found at {FIRMWARE_FILE_PATH}")
        return False

    with open(FIRMWARE_FILE_PATH, 'rb') as f:
        # 'image_file' matches the 'name' attribute of the <input type="file"> HTML tag
        # The filename (os.path.basename) is important for the server.
        files = {FILE_INPUT_NAME: (os.path.basename(FIRMWARE_FILE_PATH), f, 'application/octet-stream')}

        # If there are other form fields (e.g., hidden inputs), add them here:
        # data = {'other_field': 'value'}

        try:
            full_upload_url = f"{FIRMWARE_SERVER_URL}{UPLOAD_ENDPOINT}"
            print(f"Attempting to upload firmware to: {full_upload_url}")
            response = requests.post(full_upload_url, files=files, timeout=120) # Increased timeout for uploads

            print(f"Response Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code == 200:
                print("Firmware upload successful!")
                # You might want to parse response.text to confirm success message
                return True
            else:
                print(f"Firmware upload failed with status code {response.status_code}")
                # Print response headers for more debugging info if needed
                print("Response Headers:")
                for header, value in response.headers.items():
                    print(f"  {header}: {value}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request: {e}")
            return False

if __name__ == "__main__":
    # Ensure to replace 'your_firmware.bin' with the actual filename.
    if upload_firmware():
        print("Pipeline stage completed successfully.")
    else:
        print("Pipeline stage failed.")
        exit(1) # Exit with a non-zero code to fail the Jenkins stage
