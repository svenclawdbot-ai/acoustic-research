#!/bin/bash
# Daily Session Log Generator
# Creates end-of-day summary at 22:00

WORKSPACE="/home/james/.openclaw/workspace"
DATE=$(date +%Y-%m-%d)
YEAR=$(date +%Y)
MONTH=$(date +%m)
DAY=$(date +%d)
TIME=$(date +"%H:%M")
MEMORY_FILE="$WORKSPACE/memory/${DATE}.md"
RESEARCH_DIR="$WORKSPACE/research-blog/$YEAR/$MONTH/$DAY"

# Create memory directory if needed
mkdir -p "$WORKSPACE/memory"

# Generate summary
cat > "$MEMORY_FILE" << EOF
# ${DATE} — Daily Session Log

**Generated:** ${TIME} GMT  
**Day:** $(date +%A)

---

## 📋 Key Actions Today

### Research & Engineering
*To be filled during evening summary*

### Sniper Bot Operations
- Solana dashboard status
- Base dashboard status
- Grass rewards update

### Files & Code
*Git commits and file changes*

---

## 💡 Findings & Insights

### Engineering Research
*Key discoveries from today's challenge*

### Other Notes
*Miscellaneous insights*

---

## 📁 Files Created/Modified

### Research Blog (${YEAR}/${MONTH}/${DAY})
EOF

# List research blog files for today
if [ -d "$RESEARCH_DIR" ]; then
    echo "" >> "$MEMORY_FILE"
    for file in "$RESEARCH_DIR"/*; do
        [ -f "$file" ] || continue
        echo "- $(basename "$file")" >> "$MEMORY_FILE"
    done
    
    if [ -d "$RESEARCH_DIR/supporting" ]; then
        echo "" >> "$MEMORY_FILE"
        echo "**Supporting Files:**" >> "$MEMORY_FILE"
        for file in "$RESEARCH_DIR/supporting"/*; do
            [ -f "$file" ] || continue
            echo "- $(basename "$file")" >> "$MEMORY_FILE"
        done
    fi
else
    echo "- (No research blog entry today)" >> "$MEMORY_FILE"
fi

# Add workspace date folder files
echo "" >> "$MEMORY_FILE"
echo "### Workspace Folder (${DATE})" >> "$MEMORY_FILE"
if [ -d "$WORKSPACE/$DATE" ]; then
    echo "" >> "$MEMORY_FILE"
    for file in "$WORKSPACE/$DATE"/*; do
        [ -f "$file" ] || continue
        filename=$(basename "$file")
        # Skip system files
        case "$filename" in
            SOUL.md|IDENTITY.md|TOOLS.md|USER.md|AGENTS.md|HEARTBEAT.md|BOOTSTRAP.md)
                continue
                ;;
        esac
        echo "- $filename" >> "$MEMORY_FILE"
    done
else
    echo "- (No workspace folder for today)" >> "$MEMORY_FILE"
fi

# Add git commits from today
echo "" >> "$MEMORY_FILE"
echo "---" >> "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
echo "## 🔄 Git Commits" >> "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
cd "$WORKSPACE/research-blog" 2>/dev/null && {
    commits=$(git log --oneline --since="${DATE}T00:00:00" --until="${DATE}T23:59:59" 2>/dev/null)
    if [ -n "$commits" ]; then
        echo "### Research Blog" >> "$MEMORY_FILE"
        echo "\`\`\`" >> "$MEMORY_FILE"
        echo "$commits" >> "$MEMORY_FILE"
        echo "\`\`\`" >> "$MEMORY_FILE"
    else
        echo "- No commits today" >> "$MEMORY_FILE"
    fi
} || echo "- No git commits today" >> "$MEMORY_FILE"

# Add sniper status
echo "" >> "$MEMORY_FILE"
echo "---" >> "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
echo "## 📊 Sniper Bot Status" >> "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
echo "*To be updated manually or via dashboard check*" >> "$MEMORY_FILE"

# Add next steps section
echo "" >> "$MEMORY_FILE"
echo "---" >> "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
echo "## 🎯 Next Steps" 㸀3e "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
echo "### Tomorrow's Priorities" >> "$MEMORY_FILE"
echo "1. *To be filled during evening review*" >> "$MEMORY_FILE"
echo "2. " >> "$MEMORY_FILE"
echo "3. " >> "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
echo "### Upcoming Deadlines" >> "$MEMORY_FILE"
echo "- *Track important dates here*" >> "$MEMORY_FILE"

# Add session info
echo "" >> "$MEMORY_FILE"
echo "---" >> "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
echo "## 📈 Session Metrics" >> "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
echo "- **Session Log:** ${MEMORY_FILE}" >> "$MEMORY_FILE"
echo "- **Research Blog:** ${RESEARCH_DIR}/" >> "$MEMORY_FILE"
echo "" >> "$MEMORY_FILE"
echo "---" >> "$MEMORY_FILE"
echo "*End of daily log*" >> "$MEMORY_FILE"

echo "✅ Daily log created: $MEMORY_FILE"
echo "   Research blog: $RESEARCH_DIR/"
