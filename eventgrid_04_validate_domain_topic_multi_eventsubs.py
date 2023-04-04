import os
import requests
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.eventgrid import EventGridManagementClient

# Replace <terraform-cloud-org-name>, <terraform-cloud-workspace-name>, and <terraform-state-id> with your values
terraform_org_name = '<terraform-cloud-org-name>'
terraform_workspace_name = '<terraform-cloud-workspace-name>'
terraform_state_id = '<terraform-state-id>'

# Authenticate with Azure using the default credentials
credential = DefaultAzureCredential()

# Create the Event Grid management client
eventgrid_client = EventGridManagementClient(credential, os.environ['ARM_SUBSCRIPTION_ID'])

# Retrieve the Terraform Cloud API token from an environment variable
api_token = os.environ['TERRAFORM_CLOUD_API_TOKEN']

# Define the API endpoint URL
api_url = f'https://app.terraform.io/api/v2/workspaces/{terraform_org_name}/{terraform_workspace_name}/states/{terraform_state_id}'

# Define the headers to include the API token
headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/vnd.api+json'
}

# Make the API request to retrieve the state of the workspace
response = requests.get(api_url, headers=headers)

# Parse the response JSON into a dictionary
response_dict = json.loads(response.content)

# Get the "resources" object from the response dictionary
resources = response_dict['data']['attributes']['resources']

# Iterate over the resources and look for the Azure Event Grid domain and domain topic
for resource in resources:
    # Check if the resource is an Azure Event Grid domain topic
    if resource['type'] == 'azurerm_eventgrid_domain_topic':
        # Get the properties of the domain topic
        domain_topic_resource_id = resource['id']
        domain_topic_name = resource['values']['name']
        domain_topic_domain_name = resource['values']['domain_name']
        
        # Print the domain topic properties
        print(f'Azure Event Grid domain topic "{domain_topic_name}" found with resource ID "{domain_topic_resource_id}" in domain "{domain_topic_domain_name}"')
        
        # Get the subscriptions for the domain topic
        event_subscriptions = eventgrid_client.event_subscriptions.list_by_domain_topic(domain_topic_domain_name, domain_topic_name)
        
        # Check if the domain topic has multiple subscriptions
        if len(list(event_subscriptions)) > 1:
            # Print the properties of each subscription
            print(f'Multiple event subscriptions found for domain topic "{domain_topic_name}":')
            for subscription in event_subscriptions:
                print(f'\tSubscription name: {subscription.name}')
                print(f'\tResource ID: {subscription.id}')
                print(f'\tEndpoint URL: {subscription.endpoint_url}')
                print(f'\tEvent delivery schema: {subscription.event_delivery_schema}')
                print(f'\tIncluded event types: {subscription.included_event_types}')
        else:
            print(f'Only one event subscription found for domain topic "{domain_topic_name}"')
