#!/bin/bash
# Morning Brief Backup Check Script
# Checks if morning briefing was delivered today

TODAY=$(date +%Y-%m-%d)
LOG_FILE="/home/james/.openclaw/workspace/memory/${TODAY}.md"

# Check if today's memory file exists and contains morning brief
if [ -f "$LOG_FILE" ]; then
    if grep -q "Morning Brief" "$LOG_FILE" 2>/dev/null || \
       grep -q "📰" "$LOG_FILE" 2>/dev/null || \
       grep -q "RSS" "$LOG_FILE" 2>/dev/null; then
        echo "✅ Morning briefing found for today"
        exit 0
    fi
fi

# Also check if briefing was sent via message log
# If we reach here, no briefing found
echo "🚨 Morning briefing didn't arrive at 7 AM. The RSS feed fetcher may have failed. Shall I generate a quick version now using web search backup?"
exit 1
