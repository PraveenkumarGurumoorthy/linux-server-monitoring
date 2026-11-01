import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "scripts")
)

import alert_manager as am

TEST_DIR = Path(__file__).parent / "temp"

am.LOG_FILE = TEST_DIR / "monitor_test.log"
am.ALERT_FILE = TEST_DIR / "alerts_test.log"
am.NOTIFICATION_LOG = TEST_DIR / "notification_status_test.log"
am.ERROR_LOG = TEST_DIR / "notification_errors_test.log"

am.process_alerts()
