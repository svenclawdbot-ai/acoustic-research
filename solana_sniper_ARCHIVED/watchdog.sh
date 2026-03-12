#!/bin/bash
# Watchdog script to keep dashboard running for 48h trial

LOG_FILE="/home/james/.openclaw/workspace/solana_sniper/logs/watchdog.log"
DASHBOARD_PID_FILE="/home/james/.openclaw/workspace/solana_sniper/dashboard.pid"

echo "$(date): Watchdog started" >> "$LOG_FILE"

while true; do
    # Check if dashboard is running
    if ! pgrep -f "dashboard_real.py" > /dev/null; then
        echo "$(date): Dashboard not running, restarting..." >> "$LOG_FILE"
        
        cd /home/james/.openclaw/workspace/solana_sniper
        nohup python3 dashboard_real.py >> logs/dashboard_real.log 2>&1 &
        echo $! > "$DASHBOARD_PID_FILE"
        
        # Send notification
        echo "Dashboard restarted at $(date)" >> "$LOG_FILE"
    fi
    
    # Check if dashboard is responding
    if ! curl -s http://localhost:8080 > /dev/null; then
        echo "$(date): Dashboard not responding, killing and restarting..." >> "$LOG_FILE"
        pkill -f dashboard_real.py
        sleep 2
        
        cd /home/james/.openclaw/workspace/solana_sniper
        nohup python3 dashboard_real.py >> logs/dashboard_real.log 2>&1 &
        echo $! > "$DASHBOARD_PID_FILE"
    fi
    
    # Log status every 10 minutes
    if [ $(($(date +%s) % 600)) -lt 10 ]; then
        UPTIME=$(ps -o etime= -p $(pgrep -f "dashboard_real.py") 2>/dev/null || echo "N/A")
        echo "$(date): Dashboard healthy - Uptime: $UPTIME" >> "$LOG_FILE"
    fi
    
    sleep 30
done
