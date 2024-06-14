import requests
import time
import sys
import json

API_URL = "****"
USERNAME = "***"
PASSWORD = "***"

# Sample PDF_ID, this should be tracked in DB
pdf_id = "19c85c87-d464-407b-87e4-8174c996ee1d"
sample = "random.pdf"
api_token = "you_should_keep_live_token_in_db"


def get_token(username, password):
    response = requests.post(f"{API_URL}/login", auth=(username, password))
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print("Failed to login")
        return None


def token_required(func):
    def wrapper(*args, **kwargs):
        global api_token
        headers = {"Authorization": api_token}
        response = func(headers, *args, **kwargs)
        if response.status_code == 401:
            print("Token expired, fetching a new one...")
            api_token = get_token(USERNAME, PASSWORD)
            if api_token:
                headers = {"Authorization": api_token}
                response = func(headers, *args, **kwargs)
        return response

    return wrapper


@token_required
def ping(headers):
    response = requests.get(f"{API_URL}/ping", headers=headers)
    print(response.text)
    print(response.status_code)
    return response


@token_required
def upload_pdf(headers, file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_URL}/upload", files=files, headers=headers)
    return response


@token_required
def check_pdf_status(headers, pdf_id):
    response = requests.get(f"{API_URL}/status/{pdf_id}", headers=headers)
    return response


if __name__ == "__main__":
    print("--- Crystal-Granit API Prompt ---")
    print("Use 'h' for help")
    while True:
        print("-"*120)
        print(f"file id to check:{pdf_id}")
        c = input("Crystal_API> ")
        if c in ["t?"]:
            print(f"Current token is: {api_token}")
        if c in ["q", "quit", "exit"]:
            break
        if c in ["p"]:
            ping()
        if c in ["t"]:
            t = get_token(USERNAME, PASSWORD)
            if t:
                print(t)
                api_token = t
        if c in ["c"]:
            some_data = check_pdf_status(pdf_id).json()
            pretty = json.dumps(some_data, indent=4)
            print(pretty)
        if c[0] in ["u"]:
            file = c[2:]
            res = upload_pdf(file)
            data = res.json()
            pdf_id = data['id']
            print(res.json())
        if c in ["h"]:
            print(
                """
h - show this help
p - ping service
t - update token via login
u - upload pdf (defined in code)
"""
            )
