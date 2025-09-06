#!/usr/bin/env python3
"""
Script to delete all GitHub Actions workflow runs from the smartcloudops-ai repository.
This script will systematically delete all workflow runs from all workflows.
"""

import requests
import time
import json
from typing import List, Dict, Any

# GitHub API configuration
GITHUB_TOKEN = "ghp_2Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q"  # Replace with your actual token
OWNER = "TechTyphoon"
REPO = "smartcloudops-ai"
BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "WorkflowCleanupScript/1.0"
}

def get_workflows() -> List[Dict[str, Any]]:
    """Get all workflows in the repository."""
    url = f"{BASE_URL}/actions/workflows"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("workflows", [])
    else:
        print(f"Error fetching workflows: {response.status_code} - {response.text}")
        return []

def get_workflow_runs(workflow_id: int, per_page: int = 100) -> List[Dict[str, Any]]:
    """Get all workflow runs for a specific workflow."""
    all_runs = []
    page = 1
    
    while True:
        url = f"{BASE_URL}/actions/workflows/{workflow_id}/runs"
        params = {
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            runs = data.get("workflow_runs", [])
            
            if not runs:
                break
                
            all_runs.extend(runs)
            page += 1
            
            # Rate limiting
            time.sleep(0.1)
        else:
            print(f"Error fetching workflow runs for {workflow_id}: {response.status_code} - {response.text}")
            break
    
    return all_runs

def delete_workflow_run(run_id: int) -> bool:
    """Delete a specific workflow run."""
    url = f"{BASE_URL}/actions/runs/{run_id}"
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        return True
    else:
        print(f"Error deleting run {run_id}: {response.status_code} - {response.text}")
        return False

def main():
    """Main function to delete all workflow runs."""
    print("🚀 Starting workflow cleanup process...")
    
    # Get all workflows
    workflows = get_workflows()
    print(f"📋 Found {len(workflows)} workflows")
    
    total_deleted = 0
    
    for workflow in workflows:
        workflow_id = workflow["id"]
        workflow_name = workflow["name"]
        
        print(f"\n🔍 Processing workflow: {workflow_name} (ID: {workflow_id})")
        
        # Get all runs for this workflow
        runs = get_workflow_runs(workflow_id)
        print(f"   Found {len(runs)} runs to delete")
        
        # Delete each run
        for run in runs:
            run_id = run["id"]
            run_title = run["display_title"]
            status = run["status"]
            conclusion = run.get("conclusion", "unknown")
            
            print(f"   🗑️  Deleting run {run_id}: {run_title} ({status}/{conclusion})")
            
            if delete_workflow_run(run_id):
                total_deleted += 1
                print(f"   ✅ Successfully deleted run {run_id}")
            else:
                print(f"   ❌ Failed to delete run {run_id}")
            
            # Rate limiting to avoid hitting API limits
            time.sleep(0.2)
    
    print(f"\n🎉 Cleanup complete! Deleted {total_deleted} workflow runs total.")
    
    # Verify cleanup
    print("\n🔍 Verifying cleanup...")
    remaining_runs = 0
    for workflow in workflows:
        runs = get_workflow_runs(workflow["id"])
        remaining_runs += len(runs)
        if runs:
            print(f"   ⚠️  {workflow['name']} still has {len(runs)} runs")
    
    if remaining_runs == 0:
        print("✅ All workflow runs have been successfully deleted!")
    else:
        print(f"⚠️  {remaining_runs} workflow runs still remain. You may need to run the script again.")

if __name__ == "__main__":
    main()
