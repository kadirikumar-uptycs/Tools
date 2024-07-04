import math
import pandas as pd
import requests
from dotenv import load_dotenv
import os

load_dotenv()

TOTANGO_USAGE_API_URL = "https://int-hub.totango.com/api/v1/usage"

def read_usage_data(file, end, start=0):
    try:
        df = pd.read_csv(file)
        if not end: end = len(pd)-1
        return df.iloc[start:end+1]
    except Exception as e:
        print(f"Error: {e}")
        exit(-1)

def get_count(number):
    res = number % 5
    return number // 5 if res < 2.5 else math.ceil(number / 5)

def contains(test_str:str, query:str)->bool:
    """ Checks if the test_str contain the provided query string or not"""
    return test_str.find(query) != -1

def find_module(api_name:str):
    if contains(api_name, 'cloud') or contains(api_name, 'sideQuery') or contains(api_name, 'agentless'):
        if contains(api_name, 'aws'):
            return 'AWS'
        elif contains(api_name, 'gcp'):
            return 'GCP'
        elif contains(api_name, 'azure'):
            return 'AZURE'
        else:
            return 'Cloud'
    if contains(api_name, 'selfmanaged'):
        return 'SELF MANAGED'
    if contains(api_name, 'kube') or contains(api_name, 'container') or  contains(api_name, 'orchestration') or  contains(api_name, 'clusters'):
        return 'KUBERNETES'
    if contains(api_name, 'image-security') or  contains(api_name, 'image-details') or contains(api_name, 'supplyChainActivities'):
        return 'IMAGE SECURITY'
    if contains(api_name, 'github'):
        return 'GITHUB'
    return 'ENDPOINT'

def post_usage_datum(headers, payload):
    try:
        response = requests.post(url=TOTANGO_USAGE_API_URL, json=payload, headers=headers)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_usage_data_to_totango(usage_df:pd.DataFrame, service_id, secret_token):
    headers = {"service_id": service_id, "Authorization": f"app-token {secret_token}"}
    
    for index, row in usage_df.iterrows():
        if pd.isna(row["name"]) or contains(row["customer_name"], "demo") or \
        contains(row["customer_name"], "cloud2") or \
        contains(row["customer_name"], "quality2"):
            print(f"⚠️  Index- {index}: Skipping...\n\n")
            continue
        payload = {
            "account_id": row["salesforce_id"],
            "user_id": row["name"],
            "module": find_module(row["api_name"]),
            "activity": row["api_name"]
        }
        
        no_of_records = get_count(row['cnt'])
        
        payload = {
            "usages": [payload for i in range(no_of_records)]
        }
        
        response = post_usage_datum(headers, payload)
        
        if response and response.status_code in [200, 201, 202]:
            print(f"✅ Index-{index}: Success\n\n")
        else:
            if response:
                print(f"⛔ Index-{index}: Failed with response code {response.status_code}\n\n")
                print(response.json())

def main():
    
    # get usage file path
    file_path = input("Enter the file name of the Usage Data (csv format)\n")
    
    #start and end indices
    start = int(input("Enter the Start Index\n"))
    end = int(input("Enter the End Index\n"))
    
    # read the usage data
    df = read_usage_data(file=file_path, start=start, end=end)
    
    # get secrets from environment variables
    service_id = os.getenv('totango_service_id')
    secret_token = os.getenv('totango_secret_token')
    
    # send usage data to totango
    send_usage_data_to_totango(df, service_id, secret_token)


if __name__ == "__main__":
    main()