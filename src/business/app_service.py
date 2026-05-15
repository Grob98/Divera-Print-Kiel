from api.alarm_data import AlarmData
from api.divera_connector import DiveraConnector
from business.app_state import AppStore
from business.pdf.pdf_generator import PDFGenerator
from business.printer.doc_printer import PrinterService
import business.app.server
from business.app_updater import AppUpdater
import os
import threading
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class AppService:
    def __init__(self, global_path: str):
        self._store = AppStore()
        self._pdf_generator = PDFGenerator(global_path)
        self._printer_service = PrinterService(global_path)
        self._connector = DiveraConnector(self)
        self._global_path = global_path

    def get_printer_service(self) -> PrinterService:
        return self._printer_service
    
    def get_divera_connector(self) -> DiveraConnector:
        return self._connector
    
    def _start_api_job(self):
        if self._store.divera_active:
            print("Starting API connector job...")
            asyncio.run(self._connector.start())

    def _get_store(self) -> AppStore:
        return self._store

    def _run_api_connector(self):
        #detect if flask reloaded the process and only start connector if not already started
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            print("API connector already started, skipping.")
            return
        
        print("Starting API connector...")
        thread = threading.Thread(target=self._start_api_job, name="APIConnectorThread")
        thread.daemon = True
        thread.start()

    def _run_updater(self):
        app_updater = AppUpdater()
        thread = threading.Thread(target=app_updater.start_updater, name="AppUpdaterThread")
        thread.daemon = True
        thread.start()
    
    def start(self):
        self._run_updater()
        self._run_api_connector()
        business.app.server.run_server(self._global_path, self)
        pass

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def generate_pdf(self, alarm_data: AlarmData):
        self._pdf_generator.generate_pdf(alarm_data, self)

    async def alarm_data_updated(self, alarm_data: AlarmData):
        if alarm_data.is_closed():
            _LOGGER.warning("AlarmData ignored for operation %s as it is closed or deleted.", alarm_data.get_operation_no())
            return
        
        if alarm_data.get_operation_no() == self._store.ignore_operation:
            _LOGGER.warning("AlarmData ignored for operation %s as it is set to be ignored in the settings.", alarm_data.get_operation_no())
            return
        
        self._store.set_ignore_operation(alarm_data.get_operation_no())
        await self.get_divera_connector().async_fill_alarm_data(alarm_data)
        self.generate_pdf(alarm_data)
        self.get_printer_service().print("output.pdf")