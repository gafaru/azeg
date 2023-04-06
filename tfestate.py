import os
import json
import base64
import requests

# Set your Terraform Enterprise API token, organization name, workspace name, and state ID
TFE_API_TOKEN = os.environ.get("TFE_API_TOKEN")
TFE_ORG_NAME = "your_organization_name"
TFE_WORKSPACE_NAME = "your_workspace_name"
TFE_STATE_ID = "your_state_id"

# Set the Terraform Enterprise API URL
TFE_BASE_URL = "https://app.terraform.io/api/v2"

# Set up the headers for the API request
headers = {
    "Authorization": f"Bearer {TFE_API_TOKEN}",
    "Content-Type": "application/vnd.api+json",
}

# Get the workspace ID using the organization and workspace names
workspace_url = f"{TFE_BASE_URL}/organizations/{TFE_ORG_NAME}/workspaces/{TFE_WORKSPACE_NAME}"
response = requests.get(workspace_url, headers=headers)
workspace_data = response.json()["data"]
TFE_WORKSPACE_ID = workspace_data["id"]

# Get the state version with the specified state ID
state_version_url = f"{TFE_BASE_URL}/state-versions/{TFE_STATE_ID}"
response = requests.get(state_version_url, headers=headers)
state_version = response.json()["data"]

# Get the state file URL and download the state file
state_file_url = state_version["attributes"]["hosted-state-download-url"]
response = requests.get(state_file_url)

# Decode the state file content and load it as JSON
state_file_content = base64.b64decode(response.content).decode("utf-8")
state_data = json.loads(state_file_content)

# Extract the resources from the state file
resources = state_data["values"]["root_module"]["resources"]

# Print the list of resources
for resource in resources:
    print(f"Resource: {resource['name']}, Type: {resource['provider_config_key']}")
