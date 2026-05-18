from __future__ import annotations
from typing import TYPE_CHECKING
from fpdf import FPDF # type: ignore
from api.alarm_data import AlarmData
import os

if TYPE_CHECKING:
    from business.app_service import AppService
from business.pdf.pages.page_hydrant_map import PageHydrantMap
from business.pdf.pages.page_overview import PageOverview

class PDFGenerator:
    def __init__(self, global_path: str):
        #Update only on reload
        self._tmp_dir = os.path.join(global_path, "tmp")
        self._app_port = int(os.environ.get('APP_PORT', 80))
        pass

    def generate_pdf(self, alarm_data: AlarmData, app_service: AppService):
        self._alarm_data = alarm_data
        
        print("Starting PDF generation...")

        pdf = FPDF(format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(left=15, top=15, right=15)

        for _ in range(app_service._get_store().operation_info_copies):
            PageOverview(pdf, self._alarm_data).draw()

        for _ in range(app_service._get_store().hydrant_info_copies):
            PageHydrantMap(pdf, self._alarm_data, app_port=self._app_port, tmp_dir=self._tmp_dir).draw()
        
        pdf.output(self._tmp_dir + "/output.pdf")
