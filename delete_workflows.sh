#!/bin/bash
echo "🗑️ STARTING WORKFLOW DELETION PROCESS..."
echo "========================================"

TOTAL=$(wc -l < workflow_ids.txt)
COUNT=0

while IFS= read -r RUN_ID; do
    ((COUNT++))
    echo "[$COUNT/$TOTAL] Deleting workflow run ID: $RUN_ID"
    if gh run delete $RUN_ID --repo TechTyphoon/smartcloudops-ai; then
        echo "✅ Successfully deleted workflow run $RUN_ID"
    else
        echo "❌ Failed to delete workflow run $RUN_ID"
    fi
    
    # Small delay to avoid rate limiting
    sleep 0.5
done < workflow_ids.txt

echo ""
echo "🎉 WORKFLOW CLEANUP COMPLETE!"
echo "============================"
echo "Deleted $COUNT workflow runs"
