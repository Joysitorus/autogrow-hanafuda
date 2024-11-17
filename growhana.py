import os
from dotenv import load_dotenv
import requests
import time
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load .env file
load_dotenv()

# Get API Key and Refresh Token from .env
api_key = os.getenv("API_KEY")
refresh_token = os.getenv("REFRESH_TOKEN")

# Define the endpoint and headers for the garden status check
url_check = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"
headers = {
    "accept": "application/graphql-response+json, application/json",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-length": "243",
    "content-type": "application/json",
    "origin": "https://hanafuda.hana.network",
    "referer": "https://hanafuda.hana.network/",
    "sec-ch-ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

# Define the payload for checking garden status
payload_check = {
    "operationName": "GetGardenForCurrentUser",
    "query": """
    query GetGardenForCurrentUser {
        getGardenForCurrentUser {
            id
            inviteCode
            gardenDepositCount
            gardenStatus {
                id
                growActionCount
                gardenRewardActionCount
            }
            gardenMilestoneRewardInfo {
                id
                gardenDepositCountWhenLastCalculated
                lastAcquiredAt
                createdAt
            }
            gardenMembers {
                id
                sub
                name
                iconPath
                depositCount
            }
        }
    }
    """
}

# Define the payload for executing the grow action
payload_grow = {
    "operationName": "ExecuteGrowAction",
    "query": """
    mutation ExecuteGrowAction($withAll: Boolean) {
        executeGrowAction(withAll: $withAll) {
            baseValue
            leveragedValue
            totalValue
            multiplyRate
        }
    }
    """,
    "variables": {"withAll": False},
}

# Function to refresh ID token using refresh token
def refresh_id_token(refresh_token, api_key):
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        data = response.json()
        new_id_token = data.get('id_token')
        return new_id_token
    else:
        print(Fore.RED + "Error refreshing ID token:", response.status_code, response.text)
        return None

# Start of the program
print(Fore.YELLOW + "Program dimulai . . .")
print(Style.BRIGHT + Fore.CYAN + "-"*38)

while True:
    # Refresh ID token if necessary
    new_id_token = refresh_id_token(refresh_token, api_key)
    
    if new_id_token:
        headers["authorization"] = f"Bearer {new_id_token}"
        
        # Send the POST request to check garden status
        response_check = requests.post(url_check, headers=headers, json=payload_check)

        if response_check.status_code == 200:
            try:
                data_check = response_check.json()
                if data_check and 'data' in data_check and 'getGardenForCurrentUser' in data_check['data']:
                    garden_status = data_check['data']['getGardenForCurrentUser']['gardenStatus']
                    grow_action_count = garden_status['growActionCount']

                    # Check if growActionCount is not 0
                    if grow_action_count != 0:
                        print(Fore.YELLOW + f"Grow = {Fore.GREEN + str(grow_action_count)}, executing grow action...")

                        # Loop for executing grow action multiple times
                        for i in range(grow_action_count):
                            response_grow = requests.post(url_check, headers=headers, json=payload_grow)
                            
                            if response_grow.status_code == 200:
                                data_grow = response_grow.json()
                                if data_grow and 'data' in data_grow and 'executeGrowAction' in data_grow['data']:
                                    result = data_grow['data']['executeGrowAction']
                                    base_value = result['baseValue']
                                    total_value = result['totalValue']
                                    multiply_rate = result['multiplyRate']
                                    
                                    # Print results for each grow action
                                    print(Fore.YELLOW + f"Execution {i+1}/{grow_action_count}:")
                                    print(Fore.YELLOW + f"  Average Point: {Fore.GREEN + str(base_value)}")
                                    print(Fore.YELLOW + f"  Hasil Point: {Fore.GREEN + str(total_value)}")
                                    print(Fore.YELLOW + f"  Multiply Rate: {Fore.GREEN + str(multiply_rate)}")
                                    print(Style.BRIGHT + Fore.CYAN + "-"*38)
                                else:
                                    print(Fore.RED + f"Unexpected response format from grow action at iteration {i+1}: {data_grow}")
                            else:
                                print(Fore.RED + f"Request to grow action failed at iteration {i+1} with status code: {response_grow.status_code}")
                        
                        print(Fore.YELLOW + f"All {grow_action_count} grow actions completed.")
                    else:
                        print(Fore.YELLOW + f"Grow = {Fore.GREEN + '0'}, retrying in {Fore.BLUE + '5 Menit'}...")
                        time.sleep(300)  # Wait for 5 menit
                else:
                    print(Fore.RED + "Unexpected response format from garden status check:", data_check)
            except ValueError:
                print(Fore.RED + "Error parsing JSON:", response_check.text)
        else:
            print(Fore.RED + f"Request to check garden status failed with status code: {response_check.status_code}")
            print(Fore.RED + "Response:", response_check.text)
    else:
        print(Fore.RED + "Unable to refresh ID token.")

    # Wait before checking again (check the growActionCount every 5 minutes)
    time.sleep(300)  # Retry every 5 menit
