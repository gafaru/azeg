import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.core.exceptions import HttpResponseError

# Replace <subscription-id>, <resource-group-name>, and <event-grid-domain-name> with your values
subscription_id = '<subscription-id>'
resource_group_name = '<resource-group-name>'
event_grid_domain_name = '<event-grid-domain-name>'

# Authenticate with Azure using the default credentials
credential = DefaultAzureCredential()

# Create the Event Grid and Monitor management clients
eventgrid_client = EventGridManagementClient(credential, subscription_id)
monitor_client = MonitorManagementClient(credential, subscription_id)

try:
    # Get the Event Grid domain
    event_grid_domain = eventgrid_client.domains.get(resource_group_name, event_grid_domain_name)

    try:
        # Get the diagnostic settings for the Event Grid domain
        diagnostic_settings = monitor_client.diagnostic_settings.list(event_grid_domain.id)

        # Check if the diagnostic settings exist for the Event Grid domain
        if diagnostic_settings:
            print(f'Diagnostic settings found for Event Grid domain "{event_grid_domain_name}" in resource group "{resource_group_name}":')

            # Print the diagnostic settings
            for setting in diagnostic_settings:
                print(f'\tDiagnostic setting ID: {setting.id}')
                print(f'\tResource ID: {setting.resource_id}')
                print(f'\tName: {setting.name}')
                print(f'\tWorkspace ID: {setting.workspace_id}')
                print(f'\tLogs: {setting.logs}')
                print(f'\tMetrics: {setting.metrics}')
        else:
            print(f'No diagnostic settings found for Event Grid domain "{event_grid_domain_name}" in resource group "{resource_group_name}"')

    except HttpResponseError as ex:
        print(f'An error occurred while retrieving diagnostic settings: {ex}')

except HttpResponseError as ex:
    print(f'An error occurred while retrieving Event Grid domain "{event_grid_domain_name}": {ex}')
