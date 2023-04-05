import csv

class CsvReport:
    def __init__(self, filename):
        self.filename = filename
        self.fieldnames = [
            "Service",
            "Subscription",
            "Region",
            "Test Case ID",
            "Test Case Description",
            "STIG",
            "Status",
            "Expected Result",
            "Attachments",
        ]

    def create_csv(self):
        with open(self.filename, mode="w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()

    def write_row(self, data):
        with open(self.filename, mode="a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writerow(data)

# Usage example
csv_report = CsvReport("validation_report.csv")
csv_report.create_csv()

# Add a row to the CSV file
data = {
    "Service": "Azure Event Grid",
    "Subscription": "your_subscription",
    "Region": "East US",
    "Test Case ID": "TC1",
    "Test Case Description": "Validate Event Grid Domain",
    "STIG": "Some STIG reference",
    "Status": "Pass",
    "Expected Result": "Event Grid Domain should be created",
    "Attachments": "",
}

csv_report.write_row(data)
