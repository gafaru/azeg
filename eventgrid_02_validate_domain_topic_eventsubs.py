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

# Initialize a variable to track whether the domain topic with an event subscription was found
domain_topic_found = False

# Iterate over the resources and look for the Azure Event Grid domain and domain topic
for resource in resources:
    # Check if the resource is an Azure Event Grid domain
    if resource['type'] == 'azurerm_eventgrid_domain':
        # Get the properties of the domain
        domain_resource_id = resource['id']
        domain_resource_group = resource['values']['resource_group_name']
        domain_name = resource['values']['name']
        domain_location = resource['values']['location']
        domain_private_endpoint_enabled = resource['values']['private_endpoint_enabled']
        
        # Print the domain properties
        print(f'Azure Event Grid domain "{domain_name}" found with resource ID "{domain_resource_id}"')
        print(f'\tResource group: {domain_resource_group}')
        print(f'\tLocation: {domain_location}')
        print(f'\tPrivate endpoint enabled: {domain_private_endpoint_enabled}')
        
        # Check if the domain has a private endpoint
        if domain_private_endpoint_enabled:
            # Get the private endpoint connection associated with the domain
            domain_private_endpoint_connections = eventgrid_client.private_endpoint_connections.list_by_resource(domain_resource_id)
            
            # Iterate over the private endpoint connections and look for the one associated with the domain
            for connection in domain_private_endpoint_connections:
                if connection.private_endpoint.id.startswith(f'/subscriptions/{os.environ["ARM_SUBSCRIPTION_ID"]}/resourceGroups/{domain_resource_group}/providers/Microsoft.EventGrid/domains/{domain_name}'):
                    # Get the properties of the private endpoint
                    private_endpoint_id = connection.private_endpoint.id
                    private_endpoint_name = connection.private_endpoint.name
                    
                    # Print the private endpoint properties
                    print(f'\tPrivate endpoint "{private_endpoint_name}" found with resource ID "{private_endpoint_id}"')
                    break
            else:
                print(f'\tNo private endpoint found for domain "{domain_name}"')
        else:
            print(f'\tDomain "{domain_name}" does not have a private endpoint')
        
        # Check if the domain has a domain topic
        if 'domain_topic_name' in resource['values']:
            domain_topic_name = resource['values']['domain_topic_name']
            
            # Get the domain topic by name
            domain_topics = eventgrid_client.domain_topics.list_by_domain(domain_resource_id)
            for topic in domain_topics:
                if topic.name == domain_topic_name:
                    # Print the domain topic properties
                    print(f'\tDomain topic "{domain_topic_name}" found with resource ID "{topic.id}"')
                    
                    # Check if the domain topic has an event subscription
                    event_subscriptions = eventgrid_client.event_subscriptions.list_by_domain_topic(domain_resource_id, topic.name)
                    if event_subscriptions:
                        # Print the event subscription properties
                        for subscription in event_subscriptions:
                            print(f'\tEvent subscription "{subscription.name}" found with resource ID "{subscription.id}"')
                            print(f'\tEndpoint URL: {subscription.endpoint_url}')
                            print(f'\tEvent delivery schema: {subscription.event_delivery_schema}')
                            print(f'\tIncluded event types: {subscription.included_event_types}')
                        domain_topic_found = True
                    else:
                        print(f'\tNo event subscriptions found for domain topic "{domain_topic_name}"')
                    break
            else:
                print(f'\tDomain topic "{domain_topic_name}" not found')
                
# Print a message if the domain topic with an event subscription was not found
if not domain_topic_found:
    print('No domain topic with an event subscription found')
