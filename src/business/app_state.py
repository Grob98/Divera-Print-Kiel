from dotenv import load_dotenv, set_key
from version import __version__, __build_date__
import os

class AppStore:
    def __init__(self):
        load_dotenv()
        self.operation_info_copies = int(os.getenv("COPIES_OPERATION_INFO", 0))
        self.hydrant_info_copies = int(os.getenv("COPIES_HYDRANT_INFO", 0))
        self.app_info = [
            "DIVERA Print - Kiel",
            f"Version  {__version__} - {__build_date__}",
        ]

    def set_operation_info_copies(self, copies: int):
        self.operation_info_copies = int(copies)
        set_key(".env", "COPIES_OPERATION_INFO", self.operation_info_copies, quote_mode="never")

    def set_hydrant_info_copies(self, copies: int):
        self.hydrant_info_copies = int(copies)
        set_key(".env", "COPIES_HYDRANT_INFO", self.hydrant_info_copies, quote_mode="never")