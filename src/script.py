import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import time

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


evaluation_points_date_map = {}
projects_map = {}
evaluation_points_non_active_users = 0
get_total_active_points = 0
total_users_analyzed = 0
total_amount_of_transactions = 0
transactions_per_day = {}


def filter_by_start(data, start_date):
    created_at = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    filtered = [entry for entry in data if datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00")) >= created_at]
    return filtered

def normalize_date(date):
    try:
        dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
        return dt.date().isoformat()
    except Exception:
        return None


def correction_point_historics(user):
    combined_data = []
    page = 1
    while True:
        params = {
            "page": page,
            "per_page": 100
        }
        url = f"https://api.intra.42.fr/v2/users/{user}/correction_point_historics"
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            return []
        data = resp.json()
        if not data:
            break
        combined_data.extend(data)
        page += 1
    return combined_data


def scale_teams(user):
    combined_data = []
    page = 1
    while True:
        params = {
            "page": page,
            "per_page": 100
        }
        url = f"https://api.intra.42.fr/v2/users/{user}/scale_teams"
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            return []
        data = resp.json()
        if not data:
            break
        combined_data.extend(data)
        page += 1
    return combined_data

def update_evaluation_points_date_map(i, correction, total, append_value, norm_date):
    global evaluation_points_date_map
    if i == 0:
        if correction.get("scale_team_id") is not None:
            if norm_date in evaluation_points_date_map:
                evaluation_points_date_map[norm_date] += total
            else:
                evaluation_points_date_map[norm_date] = total
        else:
            if norm_date in evaluation_points_date_map:
                evaluation_points_date_map[norm_date] += (total + append_value)
            else:
                evaluation_points_date_map[norm_date] = (total + append_value)
        return
    if norm_date in evaluation_points_date_map:
        evaluation_points_date_map[norm_date] += append_value
    else:
        evaluation_points_date_map[norm_date] = append_value


def update_projects_map(correction, evaluation_history):
    pass
    

def get_users_evaluation_history(user):
    global projects_map
    global evaluation_points_non_active_users
    global get_total_active_points
    global total_users_analyzed
    global total_amount_of_transactions
    start_date = get_cursus_start(user=user)
    if start_date == None:
        return
    user_name = user.get("login")
    evaluation_history = scale_teams(user=user_name)
    correction_history = correction_point_historics(user=user_name)
    evaluation_history = filter_by_start(evaluation_history, start_date)
    correction_history = filter_by_start(correction_history, start_date)
    points = user.get("correction_point") or 0
    active = user.get("active") or False
    get_total_active_points += points
    total_users_analyzed += 1
    if not active:
        evaluation_points_non_active_users += points
    for i, correction in enumerate(correction_history):
        total = correction.get("total") or 0
        append_value = correction.get("sum") or 0
        date = correction.get("created_at")
        norm_date = normalize_date(date)
        update_evaluation_points_date_map(i=i, correction=correction, total=total, append_value=append_value, norm_date=norm_date)
        update_projects_map()
    time.sleep(2) # delay because of the rate limit...

def iterate_all_campus_users(campus_id):
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
            print("error")
            break
        data = resp.json()
        for user in data:
            if user.get("wallet", 0) > 0:
                get_users_evaluation_history(user)
        if not data:
            break
        page += 1
        time.sleep(2) # delay because of the rate limit...

def get_cursus_start(user, cursus_id=21):
    url = f"https://api.intra.42.fr/v2/users/{user['login']}/cursus_users"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    for cursus in resp.json():
        if cursus["cursus_id"] == cursus_id:
            return cursus["begin_at"]
    return None




def generate_statistics(campus_id):
    iterate_all_campus_users(campus_id)

campus = 39
generate_statistics(campus)