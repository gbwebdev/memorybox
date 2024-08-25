import logging
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from datetime import datetime
from peripage import PrinterType

# from memorybox.db import get_db
from memorybox.config import Config, MemoriesSourceType


logger = logging.getLogger("memorybox")

bp = Blueprint('main', __name__)

# @bp.route('/manifest.json')
# def serve_manifest():
#     """Serve PWA manifest
#     """
#     return send_static_file('manifest.json', mimetype='application/manifest+json')

@bp.route('/', methods=['GET'])
def index():
    """Main (home) page
    """
    return render_template('index.html')

@bp.route('/settings', methods=('GET', 'POST'))
def settings():
    """Settings page
    """

    config = Config()

    if request.method == 'POST':
        data = request.form
        config.memories_source_type = MemoriesSourceType[data.get('memoriesSourceType')]
        config.memories_local_path = data.get('memoriesLocalPath')
        config.memories_repository = data.get('memoriesRepoAddress')
        config.memories_repository_ignore_certificate = data.get('memoriesRepoIgnoreCertificate', 'false') == 'true'

        config.enable_daily_printing = data.get('enablePrinting', 'false') == 'true'
        config.printer_model = PrinterType[data.get('printerType')]
        config.printer_mac_address = data.get('printerMacAddress')

        config.workday_print_time = datetime.strptime(data.get('workdayPrintTime')[:5], '%H:%M').time()
        config.holiday_print_time = datetime.strptime(data.get('holidayPrintTime')[:5], '%H:%M').time()
        config.enable_holiday_mode = data.get('enableHolidayMode', 'false') == 'true'

        config.save_conf()

    # Get PrinterType values :
    return render_template('settings.html', settings=config, source_types=MemoriesSourceType, printer_types=PrinterType)
