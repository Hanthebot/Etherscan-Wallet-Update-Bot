import string
import random
import json
import os

"""
Returns random number code of length
"""
def randString(length = 7):
    rand = ""
    for i in range(length):
        rand += random.choice(string.digits)
    return rand

def save_userData(userData):
    with open("userData.json", "w", encoding = "utf-8") as file:
        json.dump(userData, file, indent=4)

def load_manifest():
    if not os.path.exists("manifest.json"):
        # Set default value if data.json does not exist
        manifest = {
            "bot_token": "<bot_token>", #CHANGE to your bot's token
            "bot_id": "<bot_id>", #CHANGE to your bot's id
            "developer": 99999999, #CHANGE to manager's chat id
            "developer_id": "<developer_id>" #CHANGE to manager's telegram id
        }
        print("Creating manifest.json...")
        # Load data from manifest.json
        with open("manifest.json", "w", encoding = "utf-8") as file:
            json.dump(manifest, file, indent=4)
    else:
        # Load data from data.json
        with open("manifest.json", "r", encoding = "utf-8") as file:
            manifest = json.load(file)
    return manifest

def load_userData():
    # Check whether data.json exists
    if not os.path.exists("userData.json"):
        # Set default value if data.json does not exist
        userData = {
            "subscribers": [999999, 9999121], #CHANGE to chat_id of default users
            "white_list": [],
            "userData": {}
        }
        print("Creating userData.json...")
        # Load data from data.json
        save_userData(userData)
    else:
        # Load data from data.json
        with open("userData.json", "r", encoding = "utf-8") as file:
            userData = json.load(file)
    return userData

def user_default(subscriber):
    default_user = {
            "id": subscriber, 
            "link": "https://etherscan.io/tokentxns?<link>", #CHANGE
            "last_hash": ""
        }
    return default_user.copy()

def set_user_default(userData: dict):
    for subscriber in userData["subscribers"]:
        if str(subscriber) not in list(userData["userData"].keys()):
            userData["userData"][str(subscriber)] = user_default(subscriber)
    save_userData(userData)