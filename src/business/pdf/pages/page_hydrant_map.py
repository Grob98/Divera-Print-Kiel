from PIL import Image
from fpdf import FPDF
import requests
from staticmap import StaticMap, Line, CircleMarker

from api.alarm_data import AlarmData
from business.pdf.map import TransparentStaticMap
import os

from business.pdf.pages.pdf_page import PdfBasePage

class PageHydrantMap(PdfBasePage):
    def __init__(self, pdf, alarm_data, app_port: int = 80, tmp_dir: str = None):
        self._app_port = app_port
        self._tmp_dir = tmp_dir
        self._home_coordinates = os.environ.get('HOME_COORDINATES', "54.286169486342224,10.168732342354703")
        self._zoom_level = int(os.environ.get('ZOOM_LEVEL', 17))
        self._alarm_data = alarm_data
        super().__init__(pdf)

    def draw(self):
        self._draw_map()
        self._draw_footer()

    def _draw_footer(self):
        self._pdf.set_y(-15)
        self._pdf.set_font('Arial', 'I', 8)
        self._pdf.cell(0, 0, 'Hydranten im Einsatzgebiet - Alle Angaben ohne Gewähr', 0, 0, 'C')

    def _draw_map(self):
        width, height = 794, 1123
        center = (self._alarm_data.get_longitude(), self._alarm_data.get_latitude())

        route_coords = self._get_route(self._home_coordinates, (self._alarm_data.get_latitude(), self._alarm_data.get_longitude()))

        # Base
        m_base = StaticMap(width, height, url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png")

        marker_outline = CircleMarker(center, "blue", 25)
        marker_inner = CircleMarker(center, "white", 17)
        m_base.add_marker(marker_outline)
        m_base.add_marker(marker_inner)
        m_base.add_line(Line([(lon, lat) for lat, lon in route_coords], "blue", 6))

        img_base = m_base.render(zoom=self._zoom_level, center=center)

        # Ovleray
        m_overlay = TransparentStaticMap(width, height, url_template=f"http://localhost:{self._app_port}/tiles/{{z}}/{{x}}/{{y}}.png")
        img_overlay = m_overlay.render(zoom=m_base.zoom, center=center)

        img_base = img_base.convert("RGBA")
        combined = Image.alpha_composite(img_base, img_overlay)
        combined.save(self._tmp_dir + "/hydrants.png")

        #print in landscape
        self._pdf.image(self._tmp_dir + "/hydrants.png", x=self._pdf.l_margin, y=self._pdf.get_y(), w=self._pdf.w - 2*self._pdf.l_margin)

    def _get_route(self, origin_str: str, destination: tuple) -> list:
        origin = tuple(map(float, origin_str.split(",")))

        url = "https://router.project-osrm.org/route/v1/driving/{},{};{},{}".format(
            origin[1], origin[0],      # lon, lat
            destination[1], destination[0]
        )
        resp = requests.get(url, params={"overview": "full", "geometries": "geojson"}).json()
        coords = resp["routes"][0]["geometry"]["coordinates"]
        return [(lat, lon) for lon, lat in coords]