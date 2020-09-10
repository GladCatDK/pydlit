from datetime import datetime, timedelta
import threading
import pytz


def now():
    return datetime.now(tz=pytz.utc)


class BaseSyncManager:
    def __init__(self):
        self._thread = None
        self._last_sync_run = datetime.now()

    def start_background_sync(self):
        self._thread = threading.Thread(target=self._sync_thread)
        self._thread.start()

    def is_sync_running(self):
        return datetime.now() - self._last_sync_run <= timedelta(minutes=5)

    def _sync_thread(self):
        raise Exception("Must be implemented in subclass")
