import requests
import json
import os

JIRA_URL = "https://YOUR_JIRA_INSTANCE_URL"
USER_EMAIL = "YOUR_EMAIL_ADDRESS"
API_TOKEN = os.getenv('JIRA_API_TOKEN')

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {API_TOKEN}"
}

def create_test_execution_and_update_test_run(parent_story_key, test_case_key, test_run_status):
    # Create a Test Execution and link it to the parent story
    test_execution_fields = {
        "project": {
            "key": parent_story_key.split("-")[0]
        },
        "summary": "Test Execution for " + parent_story_key,
        "description": "",
        "issuetype": {
            "name": "Test Execution"
        },
        "customfield_XXXX": [  # Replace XXXX with custom field id for 'Test Cases'
            {
                "key": test_case_key
            }
        ]
    }

    response = requests.post(
        f"{JIRA_URL}/rest/api/2/issue/",
        headers=headers,
        data=json.dumps({"fields": test_execution_fields})
    )

    if response.status_code != 201:
        print(f"Error creating Test Execution. Response: {response.text}")
        return

    # Update the test run status to Pass or Fail
    test_execution_key = response.json()["key"]
    test_run_data = {
        "status": test_run_status.upper(),
        "comment": "Executed automatically"
    }

    response = requests.put(
        f"{JIRA_URL}/rest/raven/1.0/api/test/{test_case_key}/testrun/{test_execution_key}/status",
        headers=headers,
        data=json.dumps(test_run_data)
    )

    if response.status_code != 200:
        print(f"Error updating test run {test_case_key}. Response: {response.text}")

if __name__ == "__main__":
    parent_story_key = input("Enter the key of the parent story: ")
    test_case_key = input("Enter the key of the test case to run: ")
    test_run_status = input("Enter the status of the test run (pass or fail): ")
    
    create_test_execution_and_update_test_run(parent_story_key, test_case_key, test_run_status)
