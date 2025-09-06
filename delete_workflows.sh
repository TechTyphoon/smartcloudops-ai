#!/bin/bash

# Script to delete all GitHub Actions workflow runs
# This script provides multiple methods to delete workflow runs

echo "🚀 GitHub Actions Workflow Cleanup Script"
echo "=========================================="

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found"
    
    # Check if user is authenticated
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI authenticated"
        
        echo "🔍 Getting all workflows..."
        gh api repos/TechTyphoon/smartcloudops-ai/actions/workflows --jq '.workflows[] | {id: .id, name: .name}' > workflows.json
        
        echo "📋 Found workflows:"
        cat workflows.json
        
        echo ""
        echo "🗑️  Starting deletion process..."
        
        # Delete runs from each workflow
        while IFS= read -r workflow; do
            workflow_id=$(echo "$workflow" | jq -r '.id')
            workflow_name=$(echo "$workflow" | jq -r '.name')
            
            echo "Processing workflow: $workflow_name (ID: $workflow_id)"
            
            # Get all runs for this workflow
            runs=$(gh api "repos/TechTyphoon/smartcloudops-ai/actions/workflows/$workflow_id/runs" --jq '.workflow_runs[] | .id')
            
            if [ -n "$runs" ]; then
                echo "  Found runs: $runs"
                
                # Delete each run
                for run_id in $runs; do
                    echo "  Deleting run $run_id..."
                    if gh api -X DELETE "repos/TechTyphoon/smartcloudops-ai/actions/runs/$run_id"; then
                        echo "  ✅ Deleted run $run_id"
                    else
                        echo "  ❌ Failed to delete run $run_id"
                    fi
                    sleep 0.5  # Rate limiting
                done
            else
                echo "  No runs found for this workflow"
            fi
            
            sleep 1  # Rate limiting between workflows
        done < workflows.json
        
        # Cleanup
        rm -f workflows.json
        
        echo ""
        echo "🎉 Cleanup process completed!"
        
    else
        echo "❌ GitHub CLI not authenticated. Please run: gh auth login"
        exit 1
    fi
    
else
    echo "❌ GitHub CLI not found. Please install it first:"
    echo "   - Ubuntu/Debian: sudo apt install gh"
    echo "   - macOS: brew install gh"
    echo "   - Windows: winget install GitHub.cli"
    echo ""
    echo "Alternative: Use the Python script with a personal access token"
    echo "1. Create a GitHub Personal Access Token with 'delete_repo' scope"
    echo "2. Edit delete_workflows.py and replace the GITHUB_TOKEN"
    echo "3. Run: python3 delete_workflows.py"
fi

echo ""
echo "🔍 Verifying cleanup..."
if command -v gh &> /dev/null && gh auth status &> /dev/null; then
    total_remaining=0
    gh api repos/TechTyphoon/smartcloudops-ai/actions/workflows --jq '.workflows[] | .id' | while read -r workflow_id; do
        remaining=$(gh api "repos/TechTyphoon/smartcloudops-ai/actions/workflows/$workflow_id/runs" --jq '.total_count')
        if [ "$remaining" -gt 0 ]; then
            echo "⚠️  Workflow $workflow_id still has $remaining runs"
            total_remaining=$((total_remaining + remaining))
        fi
    done
    
    if [ "$total_remaining" -eq 0 ]; then
        echo "✅ All workflow runs have been successfully deleted!"
    else
        echo "⚠️  $total_remaining workflow runs still remain"
    fi
fi