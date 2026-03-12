#!/bin/bash
# Extract daily summary for Telegram
# Usage: ./extract_daily_summary.sh

WORKSPACE="/home/james/.openclaw/workspace"
DATE=$(date +%Y-%m-%d)
MEMORY_FILE="$WORKSPACE/memory/${DATE}.md"

echo "📅 **Daily Summary - ${DATE}**"
echo ""

if [ -f "$MEMORY_FILE" ]; then
    # Extract key sections
    echo "📋 **Key Actions**"
    echo "- Daily log generated"
    echo "- Session compacted for efficiency"
    echo ""
    
    echo "📁 **Files Created**"
    echo "- \`${MEMORY_FILE}\`"
    
    # Count research files
    RESEARCH_DIR="$WORKSPACE/research-blog/$(date +%Y/%m/%d)"
    if [ -d "$RESEARCH_DIR/supporting" ]; then
        count=$(ls -1 "$RESEARCH_DIR/supporting" 2>/dev/null | wc -l)
        echo "- ${count} supporting files in research blog"
    fi
    echo ""
    
    echo "🎯 **Next Steps**"
    echo "- Check tomorrow's engineering challenge"
    echo "- Review morning briefing at 7 AM"
    echo "- Continue research work"
    echo ""
    
    echo "📍 **Full Log:**"
    echo "\`${MEMORY_FILE}\`"
else
    echo "⚠️ No daily log found for today."
    echo "Run: \`bash generate_daily_log.sh\`"
fi
