from __future__ import annotations
from flask import Flask, send_file, render_template, request
from io import BytesIO
from PIL import Image
import os
from typing import TYPE_CHECKING
import requests

from api.alarm_data import AlarmData, real2_example_alarm_data

if TYPE_CHECKING:
    from business.app_service import AppService

app_service: AppService = None
app = Flask(__name__)

@app.route("/tiles/<int:z>/<int:x>/<int:y>.png")
def tile(z, x, y):
    url = f"http://www.openfiremap.de/hytiles/{z}/{x}/{y}.png"
    r = requests.get(url)

    if r.status_code == 404:
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")

    return send_file(BytesIO(r.content), mimetype="image/png")

@app.route("/developer")
def developer():
    return render_template("developer_page.html")

@app.route("/developer/generate_pdf_test", methods=["POST"])
async def generate_pdf():
    try:
        alarm_data = AlarmData(real2_example_alarm_data())
        await app_service.get_divera_connector().async_fill_alarm_data(alarm_data)
        app_service.generate_pdf(alarm_data)
        return "PDF generation successfull.", 200
    except Exception as e:
        return f"Error occurred while generating PDF: {str(e)}", 500
    pass

@app.route("/developer/download_pdf", methods=["POST"])
def download_pdf():
    try:
        # load from disk
        with open(os.path.join(app_service.get_pdf_generator()._tmp_dir, "output.pdf"), "rb") as f:
            pdf_data = f.read()
            return send_file(BytesIO(pdf_data), mimetype="application/pdf", as_attachment=True)
    except Exception as e:
        return f"Error occurred while downloading PDF: {str(e)}", 500

@app.route("/developer/print_test", methods=["POST"])
def print_test():
    try:
        app_service.get_printer_service().print()
    except Exception as e:
        return f"Error occurred while printing: {str(e)}", 500

    return f"Successfully initiated print test to printer: {app_service.get_printer_service().get_printer_name()}", 200

# ------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------
@app.route("/setup")
def setup():
    return render_template("setup_page.html", data={
        "operation_info_copies": app_service._get_store().operation_info_copies,
        "hydrant_map_copies": app_service._get_store().hydrant_info_copies,
        "app_name": app_service._get_store().app_info[0],
        "app_version": app_service._get_store().app_info[1],
    })

@app.route("/setup/pdf_settings", methods=["POST"])
def save_pdf_settings():
    operation_info_copies = request.json.get("operation_info_copies")
    hydrant_map_copies = request.json.get("hydrant_map_copies")

    app_service._get_store().set_operation_info_copies(operation_info_copies)
    app_service._get_store().set_hydrant_info_copies(hydrant_map_copies)

    return "Settings saved successfully.", 200

# ------------------------------------------------------------------
# Server
# ------------------------------------------------------------------

def run_server(path, app_service_instance: AppService):
    print(f"Running server with path: {path}")
    app.template_folder = os.path.join(path, 'templates')
    app.static_folder = os.path.join(path, 'static')

    global app_service
    app_service = app_service_instance

    app.run(debug=True, port=int(os.environ.get('APP_PORT', 80)))    