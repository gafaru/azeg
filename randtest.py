import os
import requests
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.network import NetworkManagementClient
from csv_report import CsvReport  # Import the CsvReport class

# (The rest of the imports and variables here...)

# Initialize the CsvReport instance
csv_report = CsvReport("validation_report.csv")
csv_report.create_csv()

# Initialize the JSON report data
json_report = []

# (The rest of the validation code here...)

# Validate Azure resources
event_grid_domain = azure_resources["event_grid_domain"]
private_endpoint = azure_resources["private_endpoint"]
domain_topic = azure_resources["domain_topic"]

# Check if the Event Grid Domain exists
domain = event_grid_client.domains.get(
    event_grid_domain["resource_group_name"], event_grid_domain["name"]
)

status = "Pass" if domain else "Fail"
print("Event Grid Domain:", status)
csv_report.write_row({
    # (CSV row data here...)
})

# Update JSON report data
json_report.append({
    "Resource Name": event_grid_domain["name"],
    "Resource ID": domain.id if domain else None,
    "Status": status
})

# Check if the Private Endpoint exists
pe = network_client.private_endpoints.get(
    private_endpoint["resource_group_name"], private_endpoint["name"]
)

status = "Pass" if pe else "Fail"
print("Private Endpoint:", status)
csv_report.write_row({
    # (CSV row data here...)
})

# Update JSON report data
json_report.append({
    "Resource Name": private_endpoint["name"],
    "Resource ID": pe.id if pe else None,
    "Status": status
})

# Check if the Domain Topic exists
topic = event_grid_client.domain_topics.get(
    domain_topic["resource_group_name"],
    event_grid_domain["name"],
    domain_topic["name"],
)

status = "Pass" if topic else "Fail"
print("Domain Topic:", status)
csv_report.write_row({
    # (CSV row data here...)
})

# Update JSON report data
json_report.append({
    "Resource Name": domain_topic["name"],
    "Resource ID": topic.id if topic else None,
    "Status": status
})

# Save the JSON report data to a file
with open("report.json", "w") as json_file:
    json.dump(json_report, json_file, indent=4)
