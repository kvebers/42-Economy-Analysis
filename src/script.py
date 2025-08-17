import requests
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

def get_new_token():
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
    return headers


    
headers = get_new_token()

#get_campus()

# target campus 39 for now Heilbronn


evaluation_points_date_map = {}
projects_map = {}
evaluation_points_non_active_users = 0
get_total_active_points = 0
total_users_analyzed = 0
total_amount_of_transactions = 0
transactions_per_day = {}
total_active_users_per_date = {}
project_count_map = {}

def dump_global_to_file(filename="campus.json"):
    global projects_map, evaluation_points_date_map, total_users_analyzed, project_count_map
    global get_total_active_points, total_amount_of_transactions, evaluation_points_non_active_users
    global total_active_users_per_date
    data = {
        "total_users_analyzed": total_users_analyzed,
        "get_total_active_points": get_total_active_points,
        "total_amount_of_transactions": total_amount_of_transactions,
        "evaluation_points_non_active_users": evaluation_points_non_active_users,
        "projects_map": projects_map,
        "project_count_map": project_count_map,
        "evaluation_points_date_map": evaluation_points_date_map,
        "total_active_users_per_date": total_active_users_per_date
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


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
    global headers
    combined_data = []
    page = 1
    while True:
        params = {
            "page": page,
            "per_page": 100
        }
        url = f"https://api.intra.42.fr/v2/users/{user}/correction_point_historics"
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 429:
            time.sleep(20)
            continue
        elif resp.status_code != 200:
            return []
        data = resp.json()
        time.sleep(2)
        if not data:
            break
        combined_data.extend(data)
        page += 1
    return combined_data


def scale_teams(user):
    global headers
    combined_data = []
    page = 1
    while True:
        params = {
            "page": page,
            "per_page": 100
        }
        url = f"https://api.intra.42.fr/v2/users/{user}/scale_teams"
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 429:
            time.sleep(20)
            continue
        elif resp.status_code != 200:
            return []
        data = resp.json()
        time.sleep(2)
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


def update_projects_map(i, correction, evaluation_history):
    global projects_map
    global project_count_map
    global headers
    if correction.get("scale_team_id") is not None:
        id = correction.get("scale_team_id") or 0
        points = correction.get("sum") or 0
        if (i == 0): # just an edge case for now will default to 3
            if "kick off reset" in projects_map:
                projects_map["kick off reset"] += 3
            else:
                projects_map["kick off reset"] = 3
        for evaluation in evaluation_history:
            eval_id = evaluation.get("id") or 0
            if (eval_id == id):
                project_path = evaluation.get("team", {}).get("project_gitlab_path", "Unknown")
                if project_path in projects_map:
                    projects_map[project_path] += points
                else:
                    projects_map[project_path] = points
                if (project_path in project_count_map):
                    project_count_map[project_path] += 1
                else:
                    project_count_map[project_path] = 1
                return
        if "Evaluator cancelled a defense" in projects_map:
            projects_map["Evaluator cancelled a defense"] += points
        else:
            projects_map["Evaluator cancelled a defense"] = points
        if ("Evaluator cancelled a defense" in project_count_map):
            project_count_map["Evaluator cancelled a defense"] += 1
        else:
            project_count_map["Evaluator cancelled a defense"] = 1
    else:
        explanation = correction.get("reason") or "Unknown"
        points = correction.get("sum") or 0
        total = correction.get("total") or 0
        if i == 0 and explanation != "sanction":
            points = (total + points)
        else:
            if "kick off reset" in projects_map:
                projects_map["kick off reset"] += total
            else:
                projects_map["kick off reset"] = total
        if explanation in projects_map:
            projects_map[explanation] += points
        else:
            projects_map[explanation] = points
    

def updated_transaction_count_per_day(norm_date):
    global transactions_per_day
    global headers
    if norm_date in transactions_per_day:
        transactions_per_day[norm_date] += 1
    else:
        transactions_per_day[norm_date] = 1


def update_active_user_count(user, evaluation_history, correction_history):
    global total_active_users_per_date
    global headers
    active = bool(user.get("active?"))
    dates = []
    for evals in evaluation_history:
        if evals.get("created_at"):
            try:
                dt = datetime.fromisoformat(normalize_date(evals["created_at"]))
                dates.append(dt)
            except ValueError:
                continue
    if not dates:
        return
    start_date = min(dates)
    end_date = max(dates)
    if active:
        end_date = datetime.now()
    current = start_date.date()
    end = end_date.date()
    while current <= end:
        norm_date = current.isoformat()
        if norm_date in total_active_users_per_date:
            total_active_users_per_date[norm_date] += 1
        else:
            total_active_users_per_date[norm_date] = 1
        current += timedelta(days=1)

    
def get_users_evaluation_history(user):
    global evaluation_points_non_active_users
    global get_total_active_points
    global total_users_analyzed
    global transactions_per_day
    global total_amount_of_transactions
    global headers
    if total_users_analyzed != 0 and total_users_analyzed % 50 == 0:
        print("Got new Token")
        headers = get_new_token()
    start_date = get_cursus_start(user=user)
    if start_date == None:
        return
    user_name = user.get("login")
    time.sleep(2) # delay because of the rate limit...
    evaluation_history = scale_teams(user=user_name)
    correction_history = correction_point_historics(user=user_name)
    evaluation_history = filter_by_start(evaluation_history, start_date)
    correction_history = filter_by_start(correction_history, start_date)
    points = user.get("correction_point") or 0
    active = bool(user.get("active?"))
    get_total_active_points += points
    total_users_analyzed += 1
    if not active:
        evaluation_points_non_active_users += points
    total_amount_of_transactions += len(correction_history)
    for i, correction in enumerate(correction_history):
        total = correction.get("total") or 0
        append_value = correction.get("sum") or 0
        date = correction.get("created_at")
        norm_date = normalize_date(date)
        update_evaluation_points_date_map(i=i, correction=correction, total=total, append_value=append_value, norm_date=norm_date)
        update_projects_map(i=i, correction=correction, evaluation_history=evaluation_history)
        if (correction.get("scale_team_id") is not None):
            updated_transaction_count_per_day(norm_date=norm_date)
    update_active_user_count(user, evaluation_history, correction_history)
    dump_global_to_file()
    time.sleep(5) # delay because of the rate limit...

def iterate_all_campus_users(campus_id):
    global total_users_analyzed
    global headers
    page = 1
    while True:
        url = "https://api.intra.42.fr/v2/users"
        params = {
            "page": page,
            "per_page": 100,
            "filter[primary_campus_id]": campus_id   
        }
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 429:
            time.sleep(20)
            continue
        elif resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
            break
        data = resp.json()
        for user in data:
            if user.get("wallet", 0) > 0:
                get_users_evaluation_history(user)
        if not data:
            break
        page += 1
        time.sleep(3) # delay because of the rate limit...

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