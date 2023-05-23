import os
import requests
import json

JIRA_URL = 'https://your_jira_instance'
EMAIL = 'your_email'
TOKEN = os.getenv('JIRA_API_TOKEN')

headers = {
    "Authorization": f"Basic {TOKEN}",
    "Content-Type": "application/json"
}

# Creates a test issue and link it to the story issue
def create_test_and_link_to_story(story_key, test_summary):
    # Create test
    data = {
        "fields": {
            "project": {
                "key": story_key.split('-')[0]
            },
            "summary": test_summary,
            "description": "Created via API",
            "issuetype": {
                "name": "Test"
            },
            "labels": ["CloudRelease", "Regression"]
            # Add custom fields as needed
        }
    }

    response = requests.post(f"{JIRA_URL}/rest/api/3/issue", headers=headers, json=data)

    if response.status_code == 201:
        test_key = response.json()['key']

        # Link test to story
        data = {
            "type": {
                "name": "Tests",
                "inward": "is tested by",
                "outward": "tests"
            },
            "inwardIssue": {
                "key": story_key
            },
            "outwardIssue": {
                "key": test_key
            }
        }
        response = requests.post(f"{JIRA_URL}/rest/api/3/issueLink", headers=headers, json=data)
        return test_key if response.status_code == 201 else None
    else:
        return None


# Create a test execution for the test and set the status to pass/fail
def create_test_execution_and_set_status(test_key, status):
    # Create test execution
    data = {
        "fields": {
            "project": {
                "key": test_key.split('-')[0]
            },
            "summary": "Test Execution for " + test_key,
            "description": "",
            "issuetype": {
                "name": "Test Execution"
            },
            "customfield_10000": [  # Replace with actual custom field id for 'Test'
                {
                    "key": test_key
                }
            ]
        }
    }

    response = requests.post(f"{JIRA_URL}/rest/api/3/issue", headers=headers, json=data)

    if response.status_code == 201:
        execution_key = response.json()['key']

        # Add result (pass/fail)
        data = {
            "info": {
                "summary": "Execution of test " + test_key,
                "description": "This execution was automatically created via API",
                "user": EMAIL,
                "status": {
                    "id": "2" if status.lower() == 'pass' else '3'  # 2 is 'PASS', 3 is 'FAIL' in Xray
                }
            },
            "tests": [{
                "testKey": test_key
            }]
        }

        response = requests.post(f"{JIRA_URL}/rest/raven/1.0/import/execution", headers=headers, json=data)
        return execution_key if response.status_code == 200 else None
    else:
        return None

def main():
    story_key = input("Enter the key of the story: ")
    test_summary = input("Enter the summary of the test: ")
    status = input("Enter the status of the test execution (pass or fail): ")

    test_key = create_test_and_link_to_story(story_key, test_summary)
    if test_key:
        execution_key = create_test_execution_and_set_status(test_key, status)
        if execution_key:
            print("Test execution created and status set")
        else:
            print("Failed to create test execution or set status")
    else:
        print("Failed to create test or link to story")

if __name__ == '__main__':
    main()
