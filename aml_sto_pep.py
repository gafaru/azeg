from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from csv_report import CSVReport

def validate_aml_storage_account_with_private_endpoint(storage_account_name, resource_group_name, private_endpoint_name, subscription_id):
    # Authenticate and create a StorageManagementClient and NetworkManagementClient
    credential = DefaultAzureCredential()
    storage_client = StorageManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    # Initialize the CSVReport
    csv_report = CSVReport("aml_validation_report.csv")

    # Check if the storage account exists
    storage_account_exists = False
    for account in storage_client.storage_accounts.list_by_resource_group(resource_group_name):
        if account.name == storage_account_name:
            storage_account_exists = True
            break

    status = "Pass" if storage_account_exists else "Fail"
    csv_report.write_row(
        Service='Azure ML',
        Subscription=subscription_id,
        Region='',  # You can provide the region if needed
        Test_Case_ID='TC01',
        Test_Case_Description='Validate AML storage account existence',
        STIG='',  # You can provide the STIG if needed
        Status=status,
        Expected_Result='AML storage account exists',
        Attachments=''
    )

    # Check if the private endpoint exists
    private_endpoint_exists = False
    for pe in network_client.private_endpoints.list(resource_group_name):
        if pe.name == private_endpoint_name:
            private_endpoint_exists = True
            break

    status = "Pass" if private_endpoint_exists else "Fail"
    csv_report.write_row(
        Service='Azure ML',
        Subscription=subscription_id,
        Region='',  # You can provide the region if needed
        Test_Case_ID='TC02',
        Test_Case_Description='Validate private endpoint existence',
        STIG='',  # You can provide the STIG if needed
        Status=status,
        Expected_Result='Private endpoint exists',
        Attachments=''
    )

    # Check if the private endpoint is connected to the storage account
    private_link_service_connection_exists = False
    for pe_conn in network_client.private_link_services.list_private_endpoint_connections_by_resource_group(resource_group_name, storage_account_name):
        if pe_conn.private_endpoint.name == private_endpoint_name:
            private_link_service_connection_exists = True
            break

    status = "Pass" if private_link_service_connection_exists else "Fail"
    csv_report.write_row(
        Service='Azure ML',
        Subscription=subscription_id,
        Region='',  # You can provide the region if needed
        Test_Case_ID='TC03',
        Test_Case_Description='Validate private endpoint connection to AML storage account',
        STIG='',  # You can provide the STIG if needed
        Status=status,
        Expected_Result='Private endpoint connected to AML storage account',
        Attachments=''
    )

    # Save the CSV report
    csv_report.save()

    return storage_account_exists and private_endpoint_exists and private_link_service_connection_exists

# Example usage
subscription_id = "your_subscription_id"
resource_group_name = "your_resource_group_name"
storage_account_name = "your_storage_account_name"
private_endpoint_name = "your_private_endpoint_name"

validation_result = validate_aml_storage_account_with_private_endpoint(storage_account_name, resource_group_name, private_endpoint_name, subscription_id)
print("Validation result:", validation_result)
