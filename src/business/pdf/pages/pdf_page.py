from fpdf import FPDF
from fpdf.enums import CellBordersLayout

class PdfBasePage():
    def __init__(self, pdf: FPDF):
        self._pdf = pdf
        pdf.add_page()
        self._reset_font()

    def _reset_font(self):
        self._pdf.set_font('arial', size=12, style='')

    def _draw_underlined_table(self, pdf: FPDF, table_data: list, first_row_as_headings: bool = True):
        with pdf.table(line_height=pdf.font_size, padding=2, first_row_as_headings=first_row_as_headings, col_widths=(2,1,5)) as table:
            for data_row in table_data:
                is_last_row = (data_row == table_data[-1])
                row = table.row()
                border = CellBordersLayout.BOTTOM if is_last_row else CellBordersLayout.NONE

                if len(data_row) == 2:
                    row.cell(data_row[0], border=border, v_align="TOP")
                    row.cell(":", border=border, v_align="TOP")
                    row.cell(data_row[1], border=border, v_align="TOP")
                else:
                    row.cell(data_row[0], border=border, v_align="TOP")