import time
import datetime as dt
import requests
import jwt
import json
import colorama

colorama.init(autoreset=True)


def readFile(filePath):
    try:
        with open(filePath, 'r') as file:
            data = json.loads(file.read())
            return data
    except FileNotFoundError:
        print(colorama.Fore.RED + "FILE NOT FOUND, PLEASE PROVIDE CORRECT FILE PATH\n")
        exit(-1)
    except json.decoder.JSONDecodeError:
        print(colorama.Fore.RED + "PROVIDED FILE IS NOT IN JSON FORMAT\n")
        exit(-1)
        
        
        
def readCredentials(filePath, expiry):
    # read the credentials file
    data = readFile(filePath=filePath)
    # API Headers
    exp = time.time() + expiry
    expiry = dt.datetime.fromtimestamp(exp).strftime('%Y-%m-%d %H:%M')

    domain = data["domain"] + data["domainSuffix"]
    key, secret = data["key"], data["secret"]
    token = jwt.encode({"iss":key, "exp":exp},secret)
    auth = f"Bearer {token}"
    credentials = {"domain":domain,"customerId":data["customerId"]}
    credentials["Expiration"] = expiry
    credentials["Authorization"] = auth
    print (colorama.Fore.MAGENTA + f"\nCredentials read for {domain}\n")

    return credentials


def apiCall(endpoint, credentials):
    domain = credentials["domain"]
    customerId = credentials["customerId"]
    url = f"https://{domain}/public/api/customers/{customerId}/{endpoint}?" + 'filters={"custom": {"equals": true}}'
    
    print("\n⌛ Collecting " + colorama.Fore.YELLOW + f'"{endpoint}"... \n')

    response = requests.get(url, headers=credentials)
    
    print(colorama.Fore.GREEN + "API Response Received\n")
    
    return response

def file_output(filename, data):
    try:
        with open(f"{filename}.json", 'w', encoding='utf8') as f:
            f.write(data)
            f.close()
        print(colorama.Fore.CYAN + f"\nData Stored to {filename}.json file")
    except Exception as e:
        print()
        print(colorama.Fore.RED + f"Error storing output to {filename}.json, \nError: {e}")



def showError(data):
    opinion = input(colorama.Fore.RED + "Do you want to display more context about the error(y/Yes)\n")
    if opinion.lower() in ["y", "yes"]:
        print(colorama.Fore.YELLOW + data)
    exit(-1)

def main():
    expiry = 3600 # jwt token lifespan
    credentialsPath = input(colorama.Fore.BLUE + f"\nEnter the Credentails File Path\n")
    credentials = readCredentials(credentialsPath, expiry)
    
    resources = [
        'flagProfiles', 
        'exceptions', 
        'alertRules', 
        'eventRules', 
        'eventExcludeProfiles', 
        'filePathGroups',
        'customdashboards',
        'yaraGroupRules',
        'roles',
        'customProfiles',
        ]
    for endpoint in resources:
        try:
            response = apiCall(endpoint=endpoint, credentials=credentials)
            status = response.status_code
            print(colorama.Fore.MAGENTA + f"Response Status: {status}\n")
            if status in [200, 201, 202, 204, 206]:
                today = dt.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')
                file_output(f'{today}_{endpoint}', json.dumps(response.json()))
            else:
                showError(response.text)
        except Exception as e:
            print(e)
    print('\n\n✅ Done!!!\n')
    
if __name__ == "__main__":
    main()