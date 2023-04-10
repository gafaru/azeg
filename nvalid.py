import os
import json
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.identity import ClientSecretCredential
from csv_module import CSVReport

def validate_domain(eg_client, domain_name):
    # Validate that the Event Grid Domain exists
    try:
        domain = eg_client.domains.get_by_resource_group(resource_group, domain_name)
        print(f"Found Event Grid Domain: {domain.name} with ID: {domain.id}")
        return True
    except Exception as e:
        print(f"Error finding Event Grid Domain: {e}")
        return False

def validate_domain_topic(eg_client, domain_name, topic_name):
    # Validate that the Domain Topic exists
    try:
        domain_topic = eg_client.domain_topics.get(resource_group, domain_name, topic_name)
        print(f"Found Domain Topic: {domain_topic.name} with ID: {domain_topic.id}")
        return True
    except Exception as e:
        print(f"Error finding Domain Topic: {e}")
        return False

def validate_private_endpoint(eg_client, domain_name, pe_name):
    # Validate that the Private Endpoint Connection exists
    try:
        pe_connections = eg_client.domains.list_private_endpoint_connections(resource_group, domain_name)
        for connection in pe_connections:
            if connection.private_endpoint.name == pe_name:
                print(f"Found Private Endpoint Connection for Domain {domain_name}: {connection.name} with ID: {connection.id}")
                return True
        print(f"No Private Endpoint Connection found for Domain {domain_name} and Private Endpoint {pe_name}.")
        return False
    except Exception as e:
        print(f"Error finding Private Endpoint Connection: {e}")
        return False

# Load the Terraform state file from the environment variable
state_file_path = os.environ['TF_STATE']
with open(state_file_path) as f:
    state_content = json.load(f)

resources = state_content['values']['root_module']['resources']

# Your Azure AD Application (Service Principal) credentials
subscription_id = 'your-subscription-id'
client_id = 'your-client-id'
client_secret = 'your-client-secret'
tenant_id = 'your-tenant-id'

# Initialize Azure SDK clients
credentials = ClientSecretCredential(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)
event_grid_client = EventGridManagementClient(credentials, subscription_id)

# Initialize the CSV report
csv_report = CSVReport("report.csv")

           
# Iterate through the resources and validate them
for resource in resources:
    if resource['provider'] == "registry.terraform.io/hashicorp/azurerm":
        if resource['name'] == "azure_event_grid_domain":
            domain_name = resource['values']['name']
            resource_group = resource['values']['resource_group_name']
            status = "Pass" if validate_domain(event_grid_client, domain_name) else "Fail"
            csv_report.add_row("Event Grid Domain", subscription_id, "East US", "TC001", "Check if Event Grid Domain exists", "N/A", status, "Event Grid Domain should exist", "N/A")

        elif resource['name'] == "azure_event_grid_domain_topic":
            topic_name = resource['values']['name']
            domain_name = resource['values']['domain_name']
            resource_group = resource['values']['resource_group_name']
            status = "Pass" if validate_domain_topic(event_grid_client, domain_name, topic_name) else "Fail"
            csv_report.add_row("Event Grid Domain Topic", subscription_id, "East US", "TC002", "Check if Domain Topic exists", "N/A", status, "Domain Topic should exist", "N/A")

        elif resource['name'] == "azure_private_endpoint":
            pe_name = resource['values']['name']
            resource_group = resource['values']['resource_group_name']
            status = "Pass" if validate_private_endpoint(private_link_client, pe_name) else "Fail"
            csv_report.add_row("Private Endpoint", subscription_id, "East US", "TC003", "Check if Private Endpoint exists", "N/A", status, "Private Endpoint should exist", "N/A")

# Save the CSV report
csv_report.save()


# Iterate through the resources and validate them
for resource in resources:
    if resource['provider'] == "registry.terraform.io/hashicorp/azurerm":
        if resource['name'] == "azure_event_grid_domain":
            domain_name = resource['values']['name']
            resource_group = resource['values']['resource_group_name']
            status = "Pass" if validate_domain(event_grid_client, domain_name) else "Fail"
            csv_report.add_row("Event Grid Domain", subscription_id, "East US", "TC001", "Check if Event Grid Domain exists", "N/A", status, "Event Grid Domain should exist", "N/A")

        elif resource['name'] == "azure_event_grid_domain_topic":
            topic_name = resource['values']['name']
            domain_name = resource['values']['domain_name']
            resource_group = resource['values']['resource_group_name']
            status = "Pass" if validate_domain_topic(event_grid_client, domain_name, topic_name) else "Fail"
            csv_report.add_row("Event Grid Domain Topic", subscription_id, "East US", "TC002", "Check if Domain Topic exists", "N/A", status, "Domain Topic should exist", "N/A")

        elif resource['name'] == "azure_private_endpoint":
            pe_name = resource['values']['name']
            resource_group = resource['values']['resource_group_name']
            domain_name = resource['values']['private_service_connection']['subresource_names'][0]  # Assuming the domain name is the first subresource
            status = "Pass" if validate_private_endpoint(event_grid_client, domain_name, pe_name) else "Fail"
            csv_report.add_row("Private Endpoint", subscription_id, "East US", "TC003", "Check if Private Endpoint exists", "N/A", status, "Private Endpoint should exist", "N/A")
