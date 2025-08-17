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

campus_data = {}

def get_campus():
    campus_url = "https://api.intra.42.fr/v2/campus?per_page=100"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(campus_url, headers=headers)
    campuses = response.json()
    for campus in campuses:
        campus_data[campus["id"]] = Campus(name=campus["name"], id=campus["id"])