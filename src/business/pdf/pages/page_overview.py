from fpdf import FPDF

from api.alarm_data import AlarmData
from business.pdf.building_data import BuildingData
from business.pdf.pages.pdf_page import PdfBasePage


class PageOverview(PdfBasePage):
    def __init__(self, pdf: FPDF, alarm_data: AlarmData):
        self._alarm_data = alarm_data
        super().__init__(pdf)

    def draw(self):
        self._draw_header()
        self._draw_operation_info()
        self._draw_info()
        self._draw_address()
        self._draw_own_vehicles()
        self._draw_foreign_vehicles()
        self._draw_end()

    def _draw_header(self):
        title = "Alarmdruck - IRLS Mitte"

        self._pdf.set_font(style="B", size=16)
        self._pdf.cell(0, 10, text=title, new_x="LMARGIN", new_y="NEXT", align='C')
        self._reset_font()

    def _draw_operation_info(self):
        table_data = [
            ["Einsatz Nr.", self._alarm_data.get_operation_no()],
            ["Datum/Uhrzeit", self._alarm_data.get_formatted_creation_date()],
        ]
        self._draw_underlined_table(self._pdf, table_data)

    def _draw_end(self):
        title = "ENDE Alarmdruck - IRLS Mitte"

        self._pdf.set_font(style="B", size=16)
        self._pdf.cell(0, 30, text=title, new_x="LMARGIN", new_y="NEXT", align='C')
        self._reset_font()

    def _draw_operation_info(self):
        table_data = [
            ["Einsatz Nr.", self._alarm_data.get_operation_no()],
            ["Datum/Uhrzeit", self._alarm_data.get_formatted_creation_date()],
        ]
        self._draw_underlined_table(self._pdf, table_data)

    def _draw_info(self):
        table_data = [
            ["Alarmstichwort", self._alarm_data.get_keyword()],
            ["Meldung", self._alarm_data.get_message()],
        ]
        self._draw_underlined_table(self._pdf, table_data)

    def _draw_address(self):
        building_data = BuildingData(coordinates=(self._alarm_data.get_latitude(), self._alarm_data.get_longitude()), address=self._alarm_data.get_address())
        #building_data = BuildingData(coordinates=(54.29287223026022, 10.157457179351065), address=self._alarm_data.get_address())
        building_data.load_from_api()

        table_data = [
            ["Einsatzort", self._alarm_data.get_address()],
            ["Objektinformationen", building_data.get_info_data_str()],
            ["Koordinaten", f"Länge: {self._alarm_data.get_longitude():.6f}, Breite: {self._alarm_data.get_latitude():.6f}"],
            ["Erweiterter Druck", "Nein"],
        ]

        self._draw_underlined_table(self._pdf, table_data)

    def _draw_own_vehicles(self):
        table_data = [
            ["Einsatzmittel", self._alarm_data.get_own_vehicles()]
        ]
        self._draw_underlined_table(self._pdf, table_data)

    def _draw_foreign_vehicles(self):
        table_data = [
            ["Fremd Alarmierungen", self._alarm_data.get_foreign_vehicles()]
        ]
        self._draw_underlined_table(self._pdf, table_data, first_row_as_headings=False)