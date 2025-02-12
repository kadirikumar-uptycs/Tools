try:
    import os
    import argparse
    import pandas as pd
    import requests
    import datetime as dt
    import colorama
    import jwt
    import json
    import time
except ImportError as e:
    print("Import Error: please install below modules\n\n pip install pyJWT pandas requests colorama\n\n")
    exit(1)

colorama.init(autoreset=True)

def new_line():
    print()


def wait_a_second():
    time.sleep(1)
    
def parse_args():
    try:
        parser = argparse.ArgumentParser(description="Remove Host Tags")
        parser.add_argument("-creds_file", "--credentials_file", help="Credentials file path", required=True)
        parser.add_argument("-csv_file", "--csv_file", help="CSV file path with columns asset_id and tag_name", required=True)
        args = parser.parse_args()
        if args.credentials_file is None or args.csv_file is None:
            print(colorama.Fore.RED + "\n⛔ Please provide all the required arguments")
            exit(1)
        return args
    except Exception as e:
        print(colorama.Fore.RED + f"\n⛔ Error while parsing arguments: {e}")
        exit(1)

def get_full_path(file_path):
    try:
        if len(file_path.split("/")) == 1:
            return os.path.join(os.getcwd(), file_path)
        return file_path
    except Exception as e:
        print(colorama.Fore.RED + f"\n⛔ Error while getting full path: {e}")
        exit(1)

def read_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
        if "asset_id" not in df.columns or "tag_name" not in df.columns:
            print(colorama.Fore.RED + f"❌ Columns asset_id and tag_name not found in {file_path} file")
            exit(1)
        print(colorama.Fore.MAGENTA + f"✅ {file_path} file read successfully\n")
        
        host_tags_dict = {}
        for _, row in df.iterrows():
            asset_id = row["asset_id"]
            tag_name = row["tag_name"]
            host_tags_dict[asset_id] = host_tags_dict.get(asset_id, []) + [tag_name]
        return host_tags_dict
    except FileNotFoundError as e:
        print(colorama.Fore.RED + f"⛔ {file_path} File Not Found: please check the file path")
        exit(1)
    except Exception as e:
        print(colorama.Fore.RED + "⛔ Error: ", e)
        exit(1)


def read_credentials(file_path, expiry):
    try:
        with open(file_path, 'r') as file:
            data = json.loads(file.read())
    except FileNotFoundError:
        print(colorama.Fore.RED + f"\n⛔ {file_path} FILE NOT FOUND, PLEASE PROVIDE CORRECT FILE PATH\n")
        exit(-1)
    except json.decoder.JSONDecodeError:
        print(colorama.Fore.RED + f"\n⛔ PROVIDED FILE {file_path} IS NOT IN JSON FORMAT\n")
        exit(-1)
    except Exception as e:
        print(colorama.Fore.RED + "\n⛔ Error: ", e)
        exit(1)
    
    
    try:
        exp = time.time() + expiry
        expiry = dt.datetime.fromtimestamp(exp).strftime('%Y-%m-%d %H:%M')

        domain = data["domain"] + data["domainSuffix"]
        key, secret = data["key"], data["secret"]
        token = jwt.encode({"iss":key, "exp":exp},secret)
        auth = f"Bearer {token}"
        credentials = {"domain":domain,"customerId":data["customerId"]}
        credentials["Expiration"] = expiry
        credentials["Authorization"] = auth
        print (colorama.Fore.MAGENTA + f"\n✅ Credentials read for {domain}\n")
    except Exception as e:
        print(colorama.Fore.RED + f"\n⛔ Encountered error while generating Auth Token, Error: {e}")
        exit(-1)

    return credentials


def get_base_url(credentials):
    domain = credentials["domain"]
    customerId = credentials["customerId"]
    return f"https://{domain}/public/api/customers/{customerId}"


def get_tags(credentials, asset_id) -> list:
    BASE_URL = get_base_url(credentials)
    url = f"{BASE_URL}/assets/{asset_id}"
    
    try:
        response = requests.get(url, headers=credentials)
        data = response.json()
        return data.get("tags", []), data.get("hostName", "Unknown")
    except Exception as e:
        print(colorama.Fore.RED + f"\t⛔ Error while retrieving asset tags for {asset_id}: {e}")
        exit(1)
    
def update_tags(credentials, new_tags, asset_id):
    BASE_URL = get_base_url(credentials)
    url = f"{BASE_URL}/assets/{asset_id}"
    data = {"tags": new_tags}
    
    try:
        response = requests.put(url, headers=credentials, data=data)
        return response
    except Exception as e:
        print(colorama.Fore.RED + f"\t⛔ Error while updating/removing tags from asset {asset_id}\n Error: {e}")


def showError(data):
    opinion = input("\tDo you want to display more context about the error (y/Yes)\n")
    if opinion.lower() in ["y", "yes", ""]:
        print(colorama.Fore.YELLOW + data)
    exit(-1)



def remove_tags(credentials, host_tag_dict:dict):
    index = 1
    for asset_id, tags_to_be_removed in host_tag_dict.items():
        asset_tags, host_name = get_tags(credentials, asset_id)
        print(colorama.Fore.LIGHTBLUE_EX + f"\n({index}) Host Name --> {colorama.Fore.YELLOW} {host_name} ", end='')
        print(colorama.Fore.LIGHTBLUE_EX + f" Asset Id --> {colorama.Fore.YELLOW} {asset_id }")
        print(colorama.Fore.LIGHTGREEN_EX + f"\n\t→ Found {len(asset_tags)} tags in the Asset")
        print(colorama.Fore.LIGHTCYAN_EX + f"\n\t→ Tags to be removed: {colorama.Fore.LIGHTWHITE_EX} {tags_to_be_removed }")

        missing_tags = [tag for tag in tags_to_be_removed if tag not in asset_tags]
        
        if len(missing_tags) == len(tags_to_be_removed):
            print(colorama.Fore.LIGHTRED_EX + f"\n\t→ ❌ No provided tags found in the asset")
            index += 1
            continue
        for tag in missing_tags:
            print(colorama.Fore.LIGHTRED_EX + f"\n\t→ ❌ Tag {tag} not found in the Asset")
            tags_to_be_removed.remove(tag)
                        
        print(colorama.Fore.LIGHTYELLOW_EX + f'\n\t→ Removing "{len(tags_to_be_removed)}" tag{'s' if len(tags_to_be_removed) > 1 else ''} from Asset "{host_name}"')
        
        new_asset_tags = [tag for tag in asset_tags if tag not in tags_to_be_removed]
        
        response = update_tags(credentials, new_asset_tags, asset_id)
        status = response.status_code
        print(colorama.Fore.LIGHTYELLOW_EX + f"\n\t→ Response Status : {status}\n")
        if response.status_code != 200:
            showError(json.dumps(response.json()))
        print(colorama.Fore.LIGHTGREEN_EX + f'\n\t→ ✅ Tags {tags_to_be_removed} removed from the {asset_id}')
        index += 1
    new_line()
    new_line()
    print(colorama.Back.WHITE + colorama.Fore.GREEN + " ✅ All Tags Removed Successfully ")
    new_line()



def main():
    expiry = 3600 # jwt token lifespan
    print(colorama.Fore.LIGHTBLUE_EX + "\n\n🔥🔥🔥 Welcome to Remove Host Tags Script 🔥🔥🔥\n")
    
    wait_a_second()
        
    args = parse_args()
    credentials_path = args.credentials_file
    csv_path = args.csv_file
    print(colorama.Fore.MAGENTA + f"\n✅ Arguments Parsed Successfully")
    wait_a_second()
    
    print(colorama.Fore.CYAN + f"\nRecieved Following Paths: \n")
    print(colorama.Fore.LIGHTYELLOW_EX + f"\tCredentials File: {colorama.Fore.LIGHTWHITE_EX} {credentials_path}")
    print(colorama.Fore.LIGHTYELLOW_EX + f"\tCSV File: {colorama.Fore.LIGHTWHITE_EX} {csv_path}")
    wait_a_second()
    
    credentials_path = get_full_path(credentials_path)
    csv_path = get_full_path(csv_path)

    credentials = read_credentials(credentials_path, expiry)
    wait_a_second()
    host_tag_dict = read_csv_file(csv_path)
    wait_a_second()
    
    print(colorama.Fore.CYAN + f"\n\t\t\t\t\t⌛ R̲e̲m̲o̲v̲i̲n̲g̲ T̲a̲g̲s̲ ⌛")
    remove_tags(credentials, host_tag_dict)

if __name__ == "__main__":
    main()
    
