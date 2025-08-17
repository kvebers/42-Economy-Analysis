import requests
import os
import json
from dotenv import load_dotenv
from capus import Campus

load_dotenv()
SECRET = os.getenv("SECRET")
ID = os.getenv("ID")
token_url = "https://api.intra.42.fr/oauth/token"
token_data = {
    "grant_type": "client_credentials",
    "client_id": ID,
    "client_secret": SECRET
}

response = requests.post(token_url, data=token_data)
access_token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}

#get_campus()

# target campus 39 for now Heilbronn
output_folder = "users"
def get_all_users(campus_id):
    page = 1
    while True:
        url = "https://api.intra.42.fr/v2/users"
        params = {
            "page": page,
            "per_page": 100,
            "filter[primary_campus_id]": campus_id   
        }
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
            break
        data = resp.json()
        if not data:
            break
        page += 1

heilbronn = 39
users = get_all_users(heilbronn)
