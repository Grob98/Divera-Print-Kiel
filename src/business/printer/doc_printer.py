import logging
import subprocess
import os
import platform

_LOGGER = logging.getLogger(__name__)
SYSTEM = platform.system().lower()
if SYSTEM == "windows":
    import win32print # type: ignore

class PrinterService:
    def __init__(self, global_path: str):
        self._tmp_dir = os.path.join(global_path, "tmp")
        self._init_printer(os.environ.get('PRINTER_NAME', None))

    def get_printer_name(self):
        return os.environ.get('PRINTER_NAME', "Default printer")

    # ------------------------------------------------------------------
    # Initialization and printer setup
    # ------------------------------------------------------------------

    def _init_printer(self, printer_name: str|None):
        if SYSTEM == "windows":
            return self._init_printer_windows(printer_name)
        else:  # Unix/Linux
            return self._init_printer_unix(printer_name)

    def _init_printer_unix(self, printer_name: str|None):
        result = subprocess.run(
            ["lpstat", "-p"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            _LOGGER.error("Error occurred while initializing the printer: %s", result.stderr)
            return False
        
        if printer_name and printer_name not in result.stdout:
            _LOGGER.error("Printer not found: %s", printer_name)
            _LOGGER.info("Available printers:\n%s", result.stdout)
            return False
        
        _LOGGER.info("Printer selected: %s", printer_name if printer_name else "Default printer")

        return True
    
    def _init_printer_windows(self, printer_name: str|None):
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        _LOGGER.debug("Available printers: %s", printers)

        if printer_name and printer_name not in printers:
            _LOGGER.error("Printer not found: %s", printer_name)
            return False

        _LOGGER.info("Printer selected: %s", printer_name if printer_name else "Default printer")
        return True
    
    # ------------------------------------------------------------------
    # Printing
    # ------------------------------------------------------------------
    def print(self, file_path: str|None = None):
        if SYSTEM == "windows":
            return self._print_windows(file_path)
        else:  # Unix/Linux
            return self._print_unix(file_path)
        
    def _print_unix(self, file_path: str|None):
        if not file_path:
            file_path = os.path.join(self._tmp_dir, "output.pdf")  # Default file path for testing
        _LOGGER.debug("Printing file: %s", file_path)

        cmd = [
            "/usr/bin/lp",
            "-o sides=one-sided",
            "-o media=a4",
        ]

        #printer_name = os.environ.get("PRINTER_NAME")
        #if printer_name:
        #    cmd.append(f"-d \"{printer_name}\"")

        cmd.append(file_path)

        print(cmd)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            _LOGGER.error("Error occurred while printing: %s", result.stderr)
            raise Exception(f"Error occurred while printing: {result.stderr}")
        _LOGGER.debug("Print command output: %s", result.stdout)

    def _print_windows(self, file_path: str|None):
        if not file_path:
            file_path = os.path.join(self._tmp_dir, "output.pdf")  # Default file path for testing

        try:
            win32print.ShellExecute(
                0,
                "print",
                file_path,
                None,
                ".",
                0
            )
        except Exception as e:
            _LOGGER.error("Error occurred while printing: %s", str(e))
            raise Exception(f"Error occurred while printing: {str(e)}")