
#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import re
import sys

# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_DIR = Path("/root/linux-server-monitoring")

LOG_FILE = PROJECT_DIR / "logs" / "monitor.log"
REPORT_DIR = PROJECT_DIR / "reports"

CPU_THRESHOLD = 80
RAM_THRESHOLD = 80
DISK_THRESHOLD = 80

THRESHOLDS = {
    "CPU": CPU_THRESHOLD,
    "RAM": RAM_THRESHOLD,
    "Disk": DISK_THRESHOLD,
}

# --------------------------------------------------
# LOG PARSING
# --------------------------------------------------

TIMESTAMP_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2})\s+-\s+(?P<message>.*)$"
)

METRIC_PATTERN = re.compile(
    r"\b(CPU|RAM|Disk) Usage:\s*([\d.]+)%"
)


def extract_daily_metrics(log_content, target_date):
    """Extract metric readings belonging to a specific date."""

    metrics = {
        "CPU": [],
        "RAM": [],
        "Disk": [],
    }

    monitoring_runs = 0

    for line in log_content.splitlines():

        timestamp_match = TIMESTAMP_PATTERN.match(line)

        if not timestamp_match:
            continue

        timestamp = timestamp_match.group("timestamp")
        message = timestamp_match.group("message")

        try:
            log_date = datetime.strptime(
                timestamp, "%Y-%m-%d %H:%M:%S"
            ).date()
        except ValueError:
            continue

        if log_date != target_date:
            continue

        if "Monitoring Started" in message:
            monitoring_runs += 1

        metric_match = METRIC_PATTERN.search(message)

        if metric_match:
            metric_name = metric_match.group(1)
            metric_value = float(metric_match.group(2))

            metrics[metric_name].append(metric_value)

    return metrics, monitoring_runs


# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

def calculate_statistics(values):
    """Calculate daily minimum, maximum and average."""

    if not values:
        return None

    return {
        "minimum": min(values),
        "maximum": max(values),
        "average": sum(values) / len(values),
        "latest": values[-1],
        "count": len(values),
    }


# --------------------------------------------------
# HEALTH EVALUATION
# --------------------------------------------------

def check_health(statistics, threshold):
    """Evaluate health using maximum daily utilization."""

    if statistics is None:
        return "UNKNOWN"

    if statistics["maximum"] >= threshold:
        return "WARNING"

    return "NORMAL"


# --------------------------------------------------
# REPORT GENERATION
# --------------------------------------------------

def generate_report():

    print("Starting daily health report generation...")

    if not LOG_FILE.exists():
        print(f"ERROR: Monitoring log not found: {LOG_FILE}")
        sys.exit(1)

    try:
        log_content = LOG_FILE.read_text(encoding="utf-8")
    except OSError as error:
        print(f"ERROR: Cannot read monitoring log: {error}")
        sys.exit(1)

    report_date = datetime.now().date()

    # Extract readings for today only
    metrics, monitoring_runs = extract_daily_metrics(
        log_content, report_date
    )

    # Calculate statistics
    statistics = {}

    for metric_name, values in metrics.items():
        statistics[metric_name] = calculate_statistics(values)

    # Evaluate health
    statuses = {}

    for metric_name, stats in statistics.items():
        statuses[metric_name] = check_health(
            stats, THRESHOLDS[metric_name]
        )

    # Determine overall health
    if "WARNING" in statuses.values():
        overall_health = "WARNING"
    elif "UNKNOWN" in statuses.values():
        overall_health = "INCOMPLETE"
    else:
        overall_health = "HEALTHY"

    # Prepare report directory
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report_file = REPORT_DIR / (
        f"health_report_{report_date}.txt"
    )

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Build report
    lines = [
        "=" * 55,
        "          LINUX SERVER DAILY HEALTH REPORT",
        "=" * 55,
        "",
        f"Report Date: {report_date}",
        f"Generated At: {generated_at}",
        f"Monitoring Executions: {monitoring_runs}",
        "",
        "--------------- DAILY METRICS ----------------",
        "",
    ]

    for metric_name in ["CPU", "RAM", "Disk"]:

        stats = statistics[metric_name]
        threshold = THRESHOLDS[metric_name]
        status = statuses[metric_name]

        lines.append(f"{metric_name} UTILIZATION")
        lines.append("-" * 35)

        if stats is None:
            lines.append("Minimum:       N/A")
            lines.append("Maximum:       N/A")
            lines.append("Average:       N/A")
            lines.append("Latest:        N/A")
            lines.append("Readings:      0")
        else:
            lines.append(
                f"Minimum:       {stats['minimum']:.2f}%"
            )
            lines.append(
                f"Maximum:       {stats['maximum']:.2f}%"
            )
            lines.append(
                f"Average:       {stats['average']:.2f}%"
            )
            lines.append(
                f"Latest:        {stats['latest']:.2f}%"
            )
            lines.append(
                f"Readings:      {stats['count']}"
            )

        lines.append(f"Threshold:     {threshold}%")
        lines.append(f"Status:        {status}")
        lines.append("")

    lines.extend([
        "--------------- OVERALL HEALTH ---------------",
        "",
        f"Overall Server Health: {overall_health}",
        "",
        "=" * 55,
        "                 END OF REPORT",
        "=" * 55,
    ])

    # Save report
    report_content = "\n".join(lines) + "\n"

    try:
        report_file.write_text(
            report_content,
            encoding="utf-8"
        )
    except OSError as error:
        print(f"ERROR: Cannot save report: {error}")
        sys.exit(1)

    print("Daily report generated successfully!")
    print(f"Report location: {report_file}")
    print(f"Monitoring executions: {monitoring_runs}")
    print(f"Overall health: {overall_health}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    generate_report()
