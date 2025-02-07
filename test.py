import requests
import time

# GitHub API settings
GITHUB_TOKEN = ""
OWNER = "alexmllo"
REPO = "test-pipelines"
WORKFLOW_ID = "github-pipeline.yml"  # Can be the workflow filename or ID
BRANCH = "main"  # Specify the branch

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

payload = {
    "ref": BRANCH,
    "inputs": {
        "environment": "pro",
        "job-to-run": "job1"
    }
}

def trigger_workflow():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_ID}/dispatches"
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 204:
        print("Workflow triggered successfully.")
    else:
        print("Failed to trigger workflow:", response.text)
        exit(1)

def get_latest_run():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"
    response = requests.get(url, headers=HEADERS)
    runs = response.json().get("workflow_runs", [])
    if runs:
        return runs[0]["id"]
    return None

def get_jobs(run_id):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/jobs"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("jobs", [])

def get_logs(job_id):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/jobs/{job_id}/logs"
    response = requests.get(url, headers=HEADERS)
    return response.text

def get_state(run_id):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}"
    response = requests.get(url, headers=HEADERS)
    print(response.text)


trigger_workflow()
time.sleep(10)  # Wait a bit for the workflow to start
run_id = None
while not run_id:
    run_id = get_latest_run()
    time.sleep(5)
print(f"Monitoring workflow run {run_id}...")

completed_jobs = set()
while True:
    jobs = get_jobs(run_id)
    for job in jobs:
        job_id = job["id"]
        job_name = job["name"]
        job_status = job["status"]
        if job_status == "completed" and job_id not in completed_jobs:
            print(f"Job '{job_name}' completed. Fetching logs...")
            logs = get_logs(job_id)
            print(f"Logs for '{job_name}':\n{logs}")
            completed_jobs.add(job_id)
    if len(completed_jobs) == len(jobs):
        break
    time.sleep(10)

get_state(run_id)
