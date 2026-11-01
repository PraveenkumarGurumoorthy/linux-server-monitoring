
#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import re
import sys

from email_notifier import send_email


PROJECT_DIR = Path("/root/linux-server-monitoring")

LOG_FILE = PROJECT_DIR / "logs" / "monitor.log"
ALERT_FILE = PROJECT_DIR / "logs" / "alerts.log"

NOTIFICATION_LOG = (
    PROJECT_DIR / "logs" / "notification_status.log"
)

ERROR_LOG = (
    PROJECT_DIR / "logs" / "notification_errors.log"
)

THRESHOLDS = {
    "CPU": 80,
    "RAM": 80,
    "Disk": 80,
}

LOG_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (.*)$"
)

METRIC_PATTERN = re.compile(
    r"\b(CPU|RAM|Disk) Usage:\s*([\d.]+)%"
)


def get_latest_metrics():

    if not LOG_FILE.exists():
        raise FileNotFoundError(
            f"Monitoring log not found: {LOG_FILE}"
        )

    metrics = {}

    with LOG_FILE.open(encoding="utf-8") as log:

        for line in log:

            match = LOG_PATTERN.match(line.strip())

            if not match:
                continue

            timestamp, message = match.groups()

            metric_match = METRIC_PATTERN.search(message)

            if metric_match:

                metric, value = metric_match.groups()
                value = float(value)

                if not 0 <= value <= 100:
                    raise ValueError(
                        f"Invalid {metric} utilization: {value}"
                    )

                metrics[metric] = {
                    "value": value,
                    "timestamp": timestamp,
                }

    return metrics


def load_previous_states():

    states = {}

    if not ALERT_FILE.exists():
        return states

    with ALERT_FILE.open(encoding="utf-8") as log:

        for line in log:

            parts = line.strip().split("|")

            if len(parts) < 4:
                continue

            event = parts[1].strip()
            metric = parts[2].strip()

            if event == "WARNING":
                states[metric] = "WARNING"

            elif event == "RECOVERY":
                states[metric] = "NORMAL"

    return states


def write_alert(event, metric, value, threshold):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    message = (
        f"{timestamp} | {event} | {metric} | "
        f"Value: {value:.2f}% | Threshold: {threshold}%"
    )

    ALERT_FILE.parent.mkdir(
        parents=True, exist_ok=True
    )

    with ALERT_FILE.open("a", encoding="utf-8") as log:
        log.write(message + "\n")

    print(message)

    return timestamp


def load_notification_status():

    statuses = {}

    if not NOTIFICATION_LOG.exists():
        return statuses

    with NOTIFICATION_LOG.open(encoding="utf-8") as log:

        for line in log:

            parts = line.strip().split("|", 4)

            if len(parts) < 4:
                continue

            status = parts[0].strip()
            timestamp = parts[1].strip()
            event = parts[2].strip()
            metric = parts[3].strip()

            key = (timestamp, event, metric)

            statuses[key] = status

    return statuses


def record_notification_status(
    status, timestamp, event, metric, detail=""
):

    NOTIFICATION_LOG.parent.mkdir(
        parents=True, exist_ok=True
    )

    safe_detail = str(detail).replace("|", "/").replace(
        "\n", " "
    )

    message = (
        f"{status} | {timestamp} | {event} | "
        f"{metric} | {safe_detail}"
    )

    with NOTIFICATION_LOG.open(
        "a", encoding="utf-8"
    ) as log:

        log.write(message + "\n")


def record_notification_error(
    timestamp, event, metric, error
):

    ERROR_LOG.parent.mkdir(
        parents=True, exist_ok=True
    )

    message = (
        f"{datetime.now():%Y-%m-%d %H:%M:%S} | "
        f"{event} | {metric} | "
        f"Alert timestamp: {timestamp} | "
        f"Email failure: {str(error).replace('|', '/')}"
    )

    with ERROR_LOG.open(
        "a", encoding="utf-8"
    ) as log:

        log.write(message + "\n")

    print(f"EMAIL ERROR: {error}")


def send_alert_email(timestamp, event, metric, details):

    subject = (
        f"Linux Server Monitoring - {event}: {metric}"
    )

    body = f"""
Linux Server Monitoring Notification

Event: {event}
Metric: {metric}
Alert timestamp: {timestamp}

{details}

This notification was generated automatically
by the Linux Server Monitoring System.
"""

    send_email(subject, body)


def deliver_pending_notifications():

    if not ALERT_FILE.exists():
        return

    statuses = load_notification_status()

    with ALERT_FILE.open(encoding="utf-8") as log:
        alert_lines = log.readlines()

    for line in alert_lines:

        parts = line.strip().split("|")

        if len(parts) < 5:
            continue

        timestamp = parts[0].strip()
        event = parts[1].strip()
        metric = parts[2].strip()

        details = " | ".join(
            part.strip() for part in parts[3:]
        )

        key = (timestamp, event, metric)

        if statuses.get(key) == "SENT":
            continue

        try:

            send_alert_email(
                timestamp, event, metric, details
            )

            record_notification_status(
                "SENT",
                timestamp,
                event,
                metric,
                "Email delivered successfully"
            )

            statuses[key] = "SENT"

            print(f"EMAIL SENT: {event} - {metric}")

        except Exception as error:

            record_notification_status(
                "FAILED",
                timestamp,
                event,
                metric,
                str(error)
            )

            record_notification_error(
                timestamp, event, metric, error
            )

            statuses[key] = "FAILED"


def process_alerts():

    print("Starting alert management...")

    metrics = get_latest_metrics()
    previous_states = load_previous_states()

    if not metrics:

        print("WARNING: No monitoring metrics found.")

    else:

        for metric, threshold in THRESHOLDS.items():

            if metric not in metrics:

                print(
                    f"WARNING: Missing {metric} reading."
                )
                continue

            value = metrics[metric]["value"]

            current_state = (
                "WARNING" if value >= threshold else "NORMAL"
            )

            previous_state = previous_states.get(
                metric, "NORMAL"
            )

            if current_state == "WARNING":

                if previous_state != "WARNING":

                    write_alert(
                        "WARNING", metric, value, threshold
                    )

                else:

                    print(
                        f"{metric}: WARNING remains active "
                        f"({value:.2f}%)"
                    )

            elif current_state == "NORMAL":

                if previous_state == "WARNING":

                    write_alert(
                        "RECOVERY", metric, value, threshold
                    )

                else:

                    print(
                        f"{metric}: NORMAL ({value:.2f}%)"
                    )

    deliver_pending_notifications()

    print("Alert management completed.")


if __name__ == "__main__":

    try:
        process_alerts()

    except (OSError, ValueError) as error:

        print(f"ERROR: {error}")
        sys.exit(1)
