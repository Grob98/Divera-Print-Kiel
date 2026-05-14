from api.divera_connector import DiveraConnector
from business.app_state import AppStore
from business.pdf.pdf_generator import PDFGenerator
from business.printer.doc_printer import PrinterService
import business.app.server
import business.pdf.pdf_generator

import threading

class AppService:
    def __init__(self, global_path: str):
        self._pdf_generator = PDFGenerator(global_path)
        self._printer_service = PrinterService(global_path)
        self._connector = DiveraConnector()
        self._store = AppStore()
        self._global_path = global_path

    def get_printer_service(self) -> PrinterService:
        return self._printer_service
    
    def get_divera_connector(self) -> DiveraConnector:
        return self._connector
    
    def _start_api_job(self):
        #await connector.start_polling()
        pass

    def _get_store(self) -> AppStore:
        return self._store

    def _run_api_connector(self):
        thread = threading.Thread(target=self._start_api_job)
        thread.daemon = True
        thread.start()
        pass
    
    def start(self):
        self._run_api_connector()
        business.app.server.run_server(self._global_path, self)
        pass

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def generate_pdf(self, alarm_data):
        self._pdf_generator.generate_pdf(alarm_data, self)