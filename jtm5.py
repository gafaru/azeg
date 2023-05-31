import os
import requests
import json

JIRA_URL = 'https://your_jira_instance'
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

def get_sub_test_executions_from_story(story_key):
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/search?jql=issueFunction in subTestsOf('key = {story_key}')",
        headers=headers
    )

    if response.status_code == 200:
        sub_test_executions = response.json()
        return [ste['key'] for ste in sub_test_executions['issues']]
    else:
        print(f"Error getting sub-test executions from story. Response: {response.text}")
        return []

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

def update_test_execution_status(test_key, status):
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
    story_key = input("Enter the key of the story: ")
    status = input("Enter the status to set (pass or fail): ")

    sub_test_execution_keys = get_sub_test_executions_from_story(story_key)
    for sub_test_execution_key in sub_test_execution_keys:
        test_keys = get_test_keys_from_execution(sub_test_execution_key)
        for test_key in test_keys:
            update_test_execution_status(test_key, status)

if __name__ == '__main__':
    main()
