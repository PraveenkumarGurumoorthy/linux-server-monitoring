
#!/bin/bash

# ==========================================
# Automated Linux Server Monitoring
# Main Monitoring Script
# ==========================================

# Project directories
PROJECT_DIR="/root/linux-server-monitoring"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/monitor.log"

# Monitoring thresholds
CPU_THRESHOLD=80
RAM_THRESHOLD=80
DISK_THRESHOLD=80

# Create log directory
mkdir -p "$LOG_DIR" || {
    echo "ERROR: Cannot create log directory"
    exit 1
}

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Alert function
check_threshold() {
    local name="$1"
    local usage="$2"
    local threshold="$3"

    if ! [[ "$usage" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
        log_message "ERROR: Invalid $name reading"
        return 1
    fi

    if awk -v u="$usage" -v t="$threshold" \
        'BEGIN {exit !(u >= t)}'; then
        log_message "WARNING: High $name utilization: ${usage}% (Threshold: ${threshold}%)"
    else
        log_message "$name utilization is NORMAL"
    fi
}

log_message "===== Monitoring Started ====="

# ==========================================
# CPU Monitoring
# ==========================================

log_message "Checking CPU utilization..."

CPU_USAGE=$(top -bn1 | awk -F'[, ]+' '/Cpu\(s\)/ {
    for (i=1; i<=NF; i++) {
        if ($i == "id") {
            printf "%.2f", 100 - $(i-1)
            exit
        }
    }
}')

if [[ -n "$CPU_USAGE" ]]; then
    log_message "CPU Usage: ${CPU_USAGE}%"
    check_threshold "CPU" "$CPU_USAGE" "$CPU_THRESHOLD"
else
    log_message "ERROR: Unable to retrieve CPU usage"
fi

# ==========================================
# RAM Monitoring
# ==========================================

log_message "Checking RAM utilization..."

RAM_USAGE=$(free | awk '/Mem:/ {
    if ($2 > 0) {
        printf "%.2f", ($2-$7)/$2*100
    }
}')

if [[ -n "$RAM_USAGE" ]]; then
    log_message "RAM Usage: ${RAM_USAGE}%"
    check_threshold "RAM" "$RAM_USAGE" "$RAM_THRESHOLD"
else
    log_message "ERROR: Unable to retrieve RAM usage"
fi

# ==========================================
# Disk Monitoring
# ==========================================

log_message "Checking Disk utilization..."

DISK_USAGE=$(df -P / | awk 'NR==2 {
    gsub("%","",$5)
    print $5
}')

if [[ "$DISK_USAGE" =~ ^[0-9]+$ ]]; then
    log_message "Disk Usage: ${DISK_USAGE}%"
    check_threshold "Disk" "$DISK_USAGE" "$DISK_THRESHOLD"
else
    log_message "ERROR: Unable to retrieve disk usage"
fi

# ==========================================
# Process Monitoring
# ==========================================

log_message "Checking top CPU-consuming processes..."

ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -6 |
while IFS= read -r PROCESS_INFO; do
    log_message "PROCESS: $PROCESS_INFO"
done

# ==========================================
# Application Process Check
# ==========================================

log_message "Checking Python process availability..."

if pgrep -x python3 > /dev/null; then
    log_message "Python process: RUNNING"
else
    log_message "Python process: NOT RUNNING"
fi

# ==========================================
# Monitoring Complete
# ==========================================

log_message "===== Monitoring Completed ====="
