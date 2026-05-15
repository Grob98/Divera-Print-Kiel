
import asyncio
import requests
import subprocess
import sys
import logging
from version import __version__, __build_date__

_LOGGER = logging.getLogger(__name__)

class AppUpdater:
    def __init__(self):
        self._poll_task = None

    def start_updater(self) -> None:
        asyncio.run(self._updater_main())

    async def _updater_main(self) -> None:
        """Starts the polling loop."""
        if self._poll_task and not self._poll_task.done():
            return
        self._poll_task = asyncio.create_task(self._poll_loop())

    async def _poll_loop(self) -> None:
        while True:
            url = "https://api.github.com/repos/Grob98/Divera-Print-Kiel/releases/latest"
            response = requests.get(url).json()

            latest = response["tag_name"]

            if latest != __version__:
                _LOGGER.info("Update available: %s (current: %s)", latest, __version__)
            await asyncio.sleep(12*60*60) # check every 12 hours

    def _start_update(self):
        _LOGGER.info("Update started, launching updater process...")
        subprocess.Popen([
            sys.executable,
            "updater.py"
        ])

        sys.exit(0)