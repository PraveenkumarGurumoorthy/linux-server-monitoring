Linux Server Monitoring

A lightweight automated Linux server monitoring application built using Bash and Python.

The project monitors CPU, RAM, and disk utilization, detects threshold violations, sends email notifications through Gmail SMTP, and generates daily server health reports.

Features
CPU utilization monitoring.
RAM utilization monitoring using MemAvailable.
Disk utilization monitoring.
Configurable monitoring thresholds.
Identification of the top five CPU-consuming processes.
Python process availability check.
Timestamped monitoring logs.
Automated warning and recovery alerts.
Duplicate alert prevention.
Gmail email notifications.
Retry handling for failed email notifications.
Daily server health reports.
Automated execution using Cron.
Automated unit tests.
Technologies Used
Ubuntu 24.04 LTS
Bash
Python 3.12
Git
Docker
Cron
Gmail SMTP
Python libraries: smtplib, email, python-dotenv, unittest
Project Structure
text
linux-server-monitoring/
│
├── config/
│   └── email.env
│
├── logs/
│   ├── monitor.log
│   └── cron.log
│
├── reports/
│
├── scripts/
│   ├── server_monitor.sh
│   ├── generate_report.py
│   ├── alert_manager.py
│   └── email_notifier.py
│
├── tests/
│   ├── test_alert_manager.py
│   └── test_real_email.py
│
├── .gitignore
└── README.md

Monitoring Thresholds
Resource	Warning Threshold
CPU	80%
RAM	80%
Disk	80%

Threshold violations generate warning alerts. Recovery notifications are generated when monitored resources return to normal conditions.

Installation

Clone the repository:

bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd linux-server-monitoring


Create a Python virtual environment:

bash
python3 -m venv .venv
source .venv/bin/activate


Install dependencies:

bash
pip install python-dotenv


Install Cron:

bash
sudo apt update
sudo apt install cron -y

Email Configuration

Create the configuration file:

bash
mkdir -p config
nano config/email.env


Configure the required Gmail SMTP environment variables according to scripts/email_notifier.py.

Use a Gmail App Password instead of your regular Gmail password.

Never commit config/email.env or expose email credentials publicly.

Running the Application

Run the monitoring script:

bash
bash scripts/server_monitor.sh


Run alert management:

bash
python scripts/alert_manager.py


Generate a daily health report:

bash
python scripts/generate_report.py


Run automated tests:

bash
python -m unittest discover -s tests -v

Cron Automation

The application uses Cron for automatic execution.

Monitoring and alert management run every five minutes:

cron
*/5 * * * * cd /root/linux-server-monitoring && bash scripts/server_monitor.sh >> logs/cron.log 2>&1 && /root/linux-server-monitoring/.venv/bin/python scripts/alert_manager.py >> logs/cron.log 2>&1


Daily health reports are generated at 11:55 PM:

cron
55 23 * * * cd /root/linux-server-monitoring && /root/linux-server-monitoring/.venv/bin/python scripts/generate_report.py >> logs/cron.log 2>&1


Check scheduled jobs:

bash
crontab -l

Output

Monitoring logs:

text
logs/monitor.log


Cron execution logs:

text
logs/cron.log


Alert history:

text
logs/alerts.log


Daily health reports:

text
reports/health_report_YYYY-MM-DD.txt

Testing

The project includes automated tests covering:

CPU, RAM and disk warning notifications.
Duplicate warning prevention.
Recovery notifications.
Failed email notification retries.
Prevention of repeated successful notifications.

All five previously executed automated tests passed.

A controlled Gmail SMTP integration test was also successful.

Security
Email credentials are stored outside the source code.
Gmail App Passwords are excluded using .gitignore.
Virtual environments are excluded.
Generated logs and reports are excluded.
Test-generated temporary logs are excluded.
Project Status

Stages 1–7 completed:

Linux environment setup.
Bash server monitoring.
Python health reporting.
Alert management.
Gmail email notifications.
Automated testing.
Cron scheduling.

GitHub documentation and publishing are the remaining project activities.
