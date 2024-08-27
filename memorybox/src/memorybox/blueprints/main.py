import logging
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, send_from_directory
)
from flask_login import login_required
from sqlalchemy import desc
from datetime import date, timedelta
from peripage import PrinterType

# from memorybox.db import get_db
from memorybox.config import Config, MemoriesSourceType
from memorybox.db import db
from memorybox.model.memory import Memory

logger = logging.getLogger("memorybox")

bp = Blueprint('main', __name__)

def get_memory_by_id(id_value: int):
    res = Memory.query.filter_by(id=id_value).first()
    return res

def get_memory_by_date(date_value: date):

    res = Memory.query.filter_by(release_date=date_value).first()
    if not res :
        if date_value >= current_app.config['APP_RELEASE_DATE'] and date_value <= date.today():
            first_candidate = Memory.query.filter_by(release_date=None).first()
            if first_candidate:
                first_candidate.release_date = date_value
                db.session.commit()
                return first_candidate
            else:
                return Memory.query.order_by("release_date").first()
        else:
            return None
    else:
        return res

# @bp.route('/manifest.json')
# def serve_manifest():
#     """Serve PWA manifest
#     """
#     return send_static_file('manifest.json', mimetype='application/manifest+json')

@bp.route('/memory-fullres/<filename>')
@login_required
def memory_fullres(filename):
    # Send a file from the instance directory's images folder
    return send_from_directory(current_app.instance_path, f'memories/{filename}')


@bp.route('/memory-thumb/<filename>')
@login_required
def memory_thumb(filename):
    # Send a file from the instance directory's images folder
    return send_from_directory(current_app.instance_path, f'memories/thumbs/{filename}')

@bp.route('/', methods=['GET'])
@login_required
def index():
    """Main (home) page
    """
    todays_memory = get_memory_by_date(date.today())
    return memory(todays_memory.id)

@bp.route('/memory/<int:id>', methods=['GET'])
@login_required
def memory(id):
    """Memory page
    """
    memory = get_memory_by_id(id)
    previous_day_memory = get_memory_by_date(memory.release_date - timedelta(days=1))
    next_day_memory = get_memory_by_date(memory.release_date + timedelta(days=1))
    thumbnail_path = f"memories/thumbs/{memory.filename}"
    return render_template('memory.html',
                           memory=memory,
                           previous_day_memory=previous_day_memory,
                           next_day_memory=next_day_memory,
                           thumbnail_path=thumbnail_path)

@bp.route('/settings', methods=('GET', 'POST'))
@login_required
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
