import os
import requests
import json

JIRA_URL = 'https://your_jira_instance'
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

def get_test_keys_from_execution(sub_test_execution_key):
    response = requests.get(
        f"{JIRA_URL}/rest/raven/1.0/api/testexec/{sub_test_execution_key}/test",
        headers=headers
    )

    if response.status_code == 200:
        tests = response.json()
        return [test['key'] for test in tests]
    else:
        print(f"Error getting tests from execution. Response: {response.text}")
        return []

def update_test_execution_status(test_key, target_test_key, status):
    if test_key != target_test_key:
        return

    status_id = '2' if status.lower() == 'pass' else '3'  # 2 is 'PASS', 3 is 'FAIL' in Xray

    data = {
        "info": {
            "user": "email@example.com",  # Replace with your actual email
            "status": {
                "id": status_id
            }
        },
        "tests": [{
            "testKey": test_key
        }]
    }

    response = requests.post(
        f"{JIRA_URL}/rest/raven/1.0/import/execution",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        print(f"Error updating test execution status. Response: {response.text}")

def main():
    sub_test_execution_key = input("Enter the key of the sub test execution: ")
    target_test_key = input("Enter the key of the test to match: ")
    status = input("Enter the status to set (pass or fail): ")

    test_keys = get_test_keys_from_execution(sub_test_execution_key)
    for test_key in test_keys:
        update_test_execution_status(test_key, target_test_key, status)

if __name__ == '__main__':
    main()
