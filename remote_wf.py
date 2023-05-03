import os
import requests
import time
import zipfile
import io

GITHUB_ENTERPRISE_API_BASE = "https://github.myinternal.net/api/v3"
REPO = "myorg/your_repo_name"  # Update this to match your on-premises repository
REF = os.environ["GITHUB_REF"]
WORKFLOW_ID = "your_workflow_id"
API_URL = f"{GITHUB_ENTERPRISE_API_BASE}/repos/{REPO}/actions/workflows/{WORKFLOW_ID}/dispatches"

CUSTOM_INPUT_1 = os.environ["CUSTOM_INPUT_1"]
CUSTOM_INPUT_2 = os.environ["CUSTOM_INPUT_2"]

GITHUB_ENTERPRISE_TOKEN = os.environ["GITHUB_ENTERPRISE_TOKEN"]

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {GITHUB_ENTERPRISE_TOKEN}",
}

payload = {
    "ref": REF,
    "inputs": {
        "custom_input_1": CUSTOM_INPUT_1,
        "custom_input_2": CUSTOM_INPUT_2,
    },
}

def download_artifacts(workflow_run_id):
    artifacts_url = f"{GITHUB_ENTERPRISE_API_BASE}/repos/{REPO}/actions/runs/{workflow_run_id}/artifacts"
    response = requests.get(artifacts_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch artifacts: {response.text}")
        return

    artifacts_data = response.json()
    for artifact in artifacts_data['artifacts']:
        download_url = artifact['archive_download_url']
        artifact_name = artifact['name']

        print(f"Downloading artifact '{artifact_name}'")
        download_response = requests.get(download_url, headers=headers, stream=True)

        if download_response.status_code != 200:
            print(f"Failed to download artifact: {download_response.text}")
            continue

        zipped_artifact = io.BytesIO(download_response.content)
        with zipfile.ZipFile(zipped_artifact, 'r') as zip_ref:
            zip_ref.extractall(f'./{artifact_name}')

        print(f"Artifact '{artifact_name}' downloaded and extracted")

def stream_workflow_logs(workflow_run_id):
    jobs_url = f"{GITHUB_ENTERPRISE_API_BASE}/repos/{REPO}/actions/runs/{workflow_run_id}/jobs"
    response = requests.get(jobs_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch jobs: {response.text}")
        return

    jobs_data = response.json()
    for job in jobs_data['jobs']:
        logs_url = job['logs_url']
        logs_response = requests.get(logs_url, headers=headers, stream=True)

        if logs_response.status_code != 200:
            print(f"Failed to fetch logs: {logs_response.text}")
            continue

        print(f"==== Job {job['name']} ====")
        for chunk in logs_response.iter_content(chunk_size=128):
            print(chunk.decode(), end='')

    # Wait for the workflow to complete
    while True:
        run_url = f"{GITHUB_ENTERPRISE_API_BASE}/repos/{REPO}/actions/runs/{workflow_run_id}"
        run_response = requests.get(run_url, headers=headers)
        if run_response.status_code != 200:
            print(f"Failed to fetch workflow run: {run_response.text}")
            break

        run_data = run_response.json()
        if run_data['status'] == 'completed':
            print("Workflow completed")
            download_artifacts(workflow_run_id)
            break

        time.sleep(10)  # Wait 10 seconds before checking the workflow status again

# Trigger the workflow
response = requests.post(API_URL, headers=headers, json=payload)

if response.status_code != 204:
    print(f"Failed to trigger workflow: {response.text}")
else:
    print("Workflow triggered successfully")
    time.sleep(10)  # Wait for the workflow run to appear in the API
    workflow_run_id = get_workflow_run_id()

    if workflow_run_id:
        print(f"Streaming logs for workflow run {workflow_run_id}")
        stream_workflow_logs(workflow_run_id)
    else:
        print("Failed to find the triggered workflow run")
