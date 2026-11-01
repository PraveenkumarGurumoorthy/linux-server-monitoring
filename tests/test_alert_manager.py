
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "scripts")
)

import alert_manager as am


class AlertManagerTests(unittest.TestCase):

    def setUp(self):

        self.temp_dir = tempfile.TemporaryDirectory()

        self.test_dir = Path(self.temp_dir.name)

        self.monitor_file = self.test_dir / "monitor.log"
        self.alert_file = self.test_dir / "alerts.log"
        self.notification_file = (
            self.test_dir / "notification_status.log"
        )
        self.error_file = (
            self.test_dir / "notification_errors.log"
        )

        self.patcher = patch.multiple(
            am,
            LOG_FILE=self.monitor_file,
            ALERT_FILE=self.alert_file,
            NOTIFICATION_LOG=self.notification_file,
            ERROR_LOG=self.error_file
        )

        self.patcher.start()

        self.email_mock = patch.object(
            am,
            "send_email"
        )

        self.mock_send_email = self.email_mock.start()

    def tearDown(self):

        self.email_mock.stop()
        self.patcher.stop()
        self.temp_dir.cleanup()

    def write_metrics(self, cpu, ram, disk):

        timestamp = "2026-11-01 15:00:00"

        content = (
            f"{timestamp} - CPU Usage: {cpu}%\n"
            f"{timestamp} - RAM Usage: {ram}%\n"
            f"{timestamp} - Disk Usage: {disk}%\n"
        )

        self.monitor_file.write_text(
            content,
            encoding="utf-8"
        )

    def test_all_three_warning_emails(self):

        self.write_metrics(90, 85, 95)

        am.process_alerts()

        self.assertEqual(
            self.mock_send_email.call_count,
            3
        )

        alerts = self.alert_file.read_text()

        self.assertEqual(
            alerts.count("WARNING"),
            3
        )

    def test_duplicate_warnings_prevented(self):

        self.write_metrics(90, 85, 95)

        am.process_alerts()
        am.process_alerts()

        self.assertEqual(
            self.mock_send_email.call_count,
            3
        )

        alerts = self.alert_file.read_text()

        self.assertEqual(
            alerts.count("WARNING"),
            3
        )

    def test_recovery_email(self):

        self.write_metrics(90, 50, 40)

        am.process_alerts()

        self.write_metrics(30, 50, 40)

        am.process_alerts()

        self.assertEqual(
            self.mock_send_email.call_count,
            2
        )

        alerts = self.alert_file.read_text()

        self.assertIn("WARNING", alerts)
        self.assertIn("RECOVERY", alerts)

    def test_failed_email_is_retried(self):

        self.write_metrics(90, 50, 40)

        self.mock_send_email.side_effect = [
            ConnectionError("SMTP unavailable"),
            None
        ]

        am.process_alerts()

        self.assertTrue(
            self.error_file.exists()
        )

        self.assertIn(
            "SMTP unavailable",
            self.error_file.read_text()
        )

        am.process_alerts()

        self.assertEqual(
            self.mock_send_email.call_count,
            2
        )

        status = self.notification_file.read_text()

        self.assertIn("FAILED", status)
        self.assertIn("SENT", status)

    def test_successful_email_is_not_resent(self):

        self.write_metrics(90, 50, 40)

        am.process_alerts()
        am.process_alerts()
        am.process_alerts()

        self.assertEqual(
            self.mock_send_email.call_count,
            1
        )


if __name__ == "__main__":

    unittest.main(verbosity=2)
