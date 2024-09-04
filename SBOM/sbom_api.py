import requests
import time
import jwt
import datetime as dt
import json

# get file name
def getFileName():
    file_name = input("\nEnter the File name of access keys (User_apikey.json)\n")
    return file_name


def getCredentials(file_name):
    # open credentials file
    try:
        with open(file_name, 'r') as file:
            content = file.read()
            return json.loads(content)
    except FileNotFoundError:
        print(f"The file '{file_name}' could not be found.")
    except Exception as e:
        print(f"An error occurred while trying to open the file: {e}")
    return {}

# API POST Call
def POSTCall(url, creds, payload):
    response = requests.post(url, headers=creds, data=payload)

    data = response.json()

    return data

def main():
    file_name = getFileName()
    credentials = getCredentials(file_name)
    seconds_to_expiry = 3600
    exp = time.time() + seconds_to_expiry
    expiry = dt.datetime.fromtimestamp(exp).strftime('%Y-%m-%d %H:%M')
    domain = credentials['domain']
    customerId = credentials['customerId']
    key = credentials['key']
    secret = credentials['secret']
    token = jwt.encode({'iss':key, 'exp':exp}, secret, algorithm='HS256')
    auth = f'Bearer {token}'
    creds = {'domain':domain,'customerId':customerId}
    creds['Expiration'] = expiry
    creds['Authorization'] = auth
    resourceId = input("\nEnter the Correct Resource Id of the Asset\n")
    formatType = "CycloneDX" if input("\nEnter the format spdx (1) | CycloneDX (2)\n") == "2" else "SPDX"
    print (f'\nCredentials read for domain {domain}\n')

    # Format the URL
    url = f'https://{domain}.uptycs.io/public/api/v2/customers/{customerId}/sbom'

    # payload
    payload = {
        "name": "HOST_SBOM",
        "resourceId": resourceId,
        "resourceName": "host-sbom",
        "format": formatType
    }
    response = POSTCall(url, creds, payload)
    print(f"Query is {response['status']}\n")

    # call the API until it finishes
    while response['status'] != 'FINISHED':
        response = POSTCall(url, creds, payload)
        print(f"Query is {response['status']}\n")
        time.sleep(1)
    
    # load the API response to output.json file
    with open('output.json', 'w') as f:
        f.write(json.dumps(response))
    
    print("Created output.json in the current folder where response has imported.\n")


if __name__ == "__main__":
    main()


