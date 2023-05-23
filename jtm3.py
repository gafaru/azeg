import requests
import json
import os

JIRA_URL = "https://YOUR_JIRA_INSTANCE_URL"
USER_EMAIL = "YOUR_EMAIL_ADDRESS"
API_TOKEN = os.getenv('JIRA_API_TOKEN')

headers = {
    "Authorization": f"Basic {API_TOKEN}",
    "Content-Type": "application/json"
}

def create_test_and_update_status(story_key, test_summary, test_execution_status):
    # Create a Test and link it to the parent story
    test_fields = {
        "project": {
            "key": story_key.split("-")[0]  # Assuming the project key is the prefix of the story key
        },
        "summary": test_summary,
        "description": "",
        "issuetype": {
            "name": "Test"
        },
        "labels": ["CloudRelease", "Regression"],
        "customfield_XXXX": "Solution Testing",  # Replace XXXX with custom field id for 'Test Stage/Phase'
        "customfield_YYYY": "Manual",  # Replace YYYY with custom field id for 'Test Type'
    }

    response = requests.post(
        f"{JIRA_URL}/rest/api/2/issue/",
        headers=headers,
        data=json.dumps({"fields": test_fields})
    )

    if response.status_code != 201:
        print(f"Error creating Test. Response: {response.text}")
        return

    test_key = response.json()["key"]

    # Link the Test to the Story
    link_issue_data = {
        "type": {
            "name": "Tests"  # This might need to be updated based on your configuration
        },
        "inwardIssue": {
            "key": story_key
        },
        "outwardIssue": {
            "key": test_key
        },
        "comment": {
            "body": "Linking Test to Story"
        }
    }

    response = requests.post(
        f"{JIRA_URL}/rest/api/2/issueLink",
        headers=headers,
        data=json.dumps(link_issue_data)
    )

    if response.status_code != 201:
        print(f"Error linking Test to Story. Response: {response.text}")

    # Create a Test Execution for the Test and set the status
    test_execution_fields = {
        "project": {
            "key": story_key.split("-")[0]  # Assuming the project key is the prefix of the story key
        },
        "summary": "Test Execution for " + test_summary,
        "description": "",
        "issuetype": {
            "name": "Test Execution"
        },
        "customfield_ZZZZ": [  # Replace ZZZZ with custom field id for 'Tests'
            {
                "key": test_key
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

    test_execution_key = response.json()["key"]

    # Update the status of the Test Execution
    transition_id = "31" if test_execution_status == "pass" else "41"  # Replace '31' and '41' with actual transition ids for Pass and Fail

    transition_data = {
        "transition": {
            "id": transition_id
        }
    }

    response = requests.post(
        f"{JIRA_URL}/rest/api/2/issue/{test_execution_key}/transitions",
        headers=headers,
        data=json.dumps(transition_data)
    )

    if response.status_code != 204:
        print(f"Error updating Test Execution status. Response: {response.text}")

if __name__ == "__main__":
    story_key = input("Enter the key of the story: ")
    test_summary = input("Enter the summary of the test: ")
    test_execution_status = input("Enter the status of the test execution (pass or fail): ")
    
    create_test_and_update_status(story_key, test_summary, test_execution_status)

