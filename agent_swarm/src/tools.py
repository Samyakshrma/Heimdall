import os
import requests
import subprocess
import git 
from slack_sdk import WebClient
from langchain.tools import tool
from typing import List, Dict

# --- Configuration ---
# Assuming code is run from agent_swarm/
TARGET_APP_PATH = os.path.abspath(os.path.join(os.getcwd(), "../target_app"))
TARGET_APP_URL = "http://localhost:5000/"
CONTAINER_NAME = "target-app-container"
SLACK_CHANNEL = "#alerts"

slack_token = os.environ.get("SLACK_BOT_TOKEN")
slack_client = WebClient(token=slack_token) if slack_token else None

@tool
def check_app_health() -> str:
    """Checks if the target application returns 200 OK."""
    try:
        response = requests.get(TARGET_APP_URL, timeout=5)
        if response.status_code == 200:
            return "App is healthy. Status code 200."
        return f"App is unhealthy. Status code {response.status_code}. Response: {response.text}"
    except Exception as e:
        return f"App is down. Connection error: {e}"

@tool
def get_docker_logs() -> str:
    """Fetches the last 20 lines of Docker logs."""
    result = subprocess.run(
        ["docker", "logs", CONTAINER_NAME, "--tail", "20"],
        capture_output=True, text=True
    )
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

@tool
def get_recent_commits() -> List[Dict]:
    """Fetches the last 5 git commits."""
    repo = git.Repo(TARGET_APP_PATH)
    commits = []
    for commit in repo.iter_commits(max_count=5):
        commits.append({
            "hash": commit.hexsha,
            "message": commit.message.strip(),
            "author": commit.author.name,
            "timestamp": commit.authored_datetime.isoformat()
        })
    return commits

@tool
def get_commit_diff(commit_hash: str) -> str:
    """Gets the git diff for a specific commit."""
    repo = git.Repo(TARGET_APP_PATH)
    commit = repo.commit(commit_hash)
    return repo.git.diff(f"{commit.hexsha}^", commit.hexsha)

@tool
def execute_revert_and_redeploy(commit_hash: str) -> str:
    """Reverts a commit and runs the deploy script."""
    try:
        repo = git.Repo(TARGET_APP_PATH)
        repo.git.revert(commit_hash, no_edit=True)
        
        deploy_result = subprocess.run(
            ["./deploy.sh"],
            cwd=TARGET_APP_PATH,
            capture_output=True, text=True, timeout=60
        )
        return f"Revert Success. Deploy Output:\n{deploy_result.stdout}"
    except Exception as e:
        return f"Error executing fix: {e}"

@tool
def post_slack_message(message: str) -> str:
    """Posts to Slack."""
    if not slack_client:
        return "Slack client not configured."
    try:
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        return "Message posted."
    except Exception as e:
        return f"Slack Error: {e}"

# Export tool list
ALL_TOOLS = [
    check_app_health, get_docker_logs, get_recent_commits, 
    get_commit_diff, execute_revert_and_redeploy, post_slack_message
]