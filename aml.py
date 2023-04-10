import os
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.machinelearningservices import AzureMachineLearningWorkspaces
from azure.mgmt.network import NetworkManagementClient

# Load the Terraform state
state_file = 'path/to/your/terraform_state_file.json'

with open(state_file, 'r') as f:
    state_data = json.load(f)

resources = state_data['values']['root_module']['resources']

# Extract Azure ML workspace and private endpoint information
aml_workspace = None
private_endpoint = None

for resource in resources:
    if resource['provider']['provider'] == 'registry.terraform.io/hashicorp/azurerm' and resource['name'] == 'your_azureml_workspace_name':
        aml_workspace = resource
    if resource['provider']['provider'] == 'registry.terraform.io/hashicorp/azurerm' and resource['name'] == 'your_private_endpoint_name':
        private_endpoint = resource

if not aml_workspace or not private_endpoint:
    print("Error: Azure ML Workspace or Private Endpoint not found in Terraform state.")
    exit(1)

# Get the required properties
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = aml_workspace['values']['resource_group_name']
workspace_name = aml_workspace['values']['name']
private_endpoint_name = private_endpoint['values']['name']

# Create the credentials and clients
credential = DefaultAzureCredential()
ml_workspace_client = AzureMachineLearningWorkspaces(subscription_id, credential)
network_client = NetworkManagementClient(subscription_id, credential)

# Check if the Azure ML workspace exists
try:
    workspace = ml_workspace_client.workspaces.get(resource_group, workspace_name)
    print(f"Azure ML Workspace '{workspace_name}' exists.")
except Exception as e:
    print(f"Error: {e}")
    print(f"Azure ML Workspace '{workspace_name}' does not exist.")

# Check if the private endpoint for the Azure ML workspace exists
try:
    pe = network_client.private_endpoints.get(resource_group, private_endpoint_name)
    print(f"Private Endpoint '{private_endpoint_name}' exists.")
except Exception as e:
    print(f"Error: {e}")
    print(f"Private Endpoint '{private_endpoint_name}' does not exist.")
