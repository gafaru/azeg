import argparse
import os
import requests
import json

JIRA_URL = "https://YOUR_JIRA_INSTANCE_URL"
USER_EMAIL = "YOUR_EMAIL_ADDRESS"
API_TOKEN = os.getenv('JIRA_API_TOKEN')

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {API_TOKEN}"
}

def add_and_update_test(parent_ticket_key, test_summary, test_status):
    # Add test to the parent ticket
    test_fields = {
        "project": {
            "key": parent_ticket_key.split("-")[0]
        },
        "summary": test_summary,
        "description": "",
        "issuetype": {
            "name": "Test"
        },
        "labels": ["CloudRelease", "Regression"],
        "customfield_XXXX": "Solution Testing",  # Replace XXXX with custom field id for 'Test Stage/Phase'
        "customfield_YYYY": "Manual",  # Replace YYYY with custom field id for 'Test Type'
        "parent": {
            "key": parent_ticket_key
        }
    }

    response = requests.post(
        f"{JIRA_URL}/rest/api/2/issue/",
        headers=headers,
        data=json.dumps({"fields": test_fields})
    )

    if response.status_code != 201:
        print(f"Error adding test {test_summary}. Response: {response.text}")
        return

    # Update the test status to Pass or Fail
    test_key = response.json()["key"]
    update_status_data = {
        "transition": {
            "id": "31" if test_status == "pass" else "41"  # Replace '31' and '41' with actual transition ids for Pass and Fail
        }
    }

    response = requests.post(
        f"{JIRA_URL}/rest/api/2/issue/{test_key}/transitions",
        headers=headers,
        data=json.dumps(update_status_data)
    )

    if response.status_code != 204:
        print(f"Error updating test {test_key}. Response: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("parent_ticket_key", help="The key of the parent ticket to add the test to.")
    parser.add_argument("test_summary", help="The summary of the test to add.")
    parser.add_argument("test_status", choices=['pass', 'fail'], help="The status of the test to add.")
    args = parser.parse_args()
    
    add_and_update_test(args.parent_ticket_key, args.test_summary, args.test_status)
