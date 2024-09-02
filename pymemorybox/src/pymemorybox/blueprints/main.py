import logging
import os
import uuid
from datetime import date, datetime, timedelta
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, send_from_directory
)
from flask_login import login_required
from flask_socketio import emit
from sqlalchemy import desc
from peripage import PrinterType

# from memorybox.db import get_db
from pymemorybox import socketio
from pymemorybox.config import Config, MemoriesSourceType
from pymemorybox.db import db
from pymemorybox.model.memory import Memory

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
                #return Memory.query.order_by("release_date").first()
                return None
        else:
            return None
    else:
        return res

# @bp.route('/manifest.json')
# def serve_manifest():
#     """Serve PWA manifest
#     """
#     return send_static_file('manifest.json', mimetype='application/manifest+json')

# Handle button click event from the client-side
@socketio.on('print')
def handle_print(id):
    uid = str(uuid.uuid4()).strip()
    the_memory = get_memory_by_id(id)
    if the_memory:
        image_path = os.path.join(current_app.instance_path, f'memories/thumbs/{the_memory.filename}')
        with open(image_path, 'rb') as f:
            image_data = f.read()
        emit('request_print',
             {
                'request_id': uid,
                'memory_id': id,
                'image_data': image_data,
                'printer': {
                    'mac_address': Config().printer_mac_address,
                    'model': Config().printer_model.name
                }
             },
             broadcast=True)
        return uid

@socketio.on('agent_response')
def handle_agent_response(data):
    current_app.logger.debug('agent_response :')
    current_app.logger.debug(data)
    if data.get('status', 0) == 200:
        if 'memory_id' in data:
            memory = get_memory_by_id(data['memory_id'])
            if memory:
                memory.printed = True
                db.session.commit()

    # Notify the agent
    emit('agent_response', data, broadcast=True)

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
    if todays_memory:
        return memory(todays_memory.id, True)
    else:
        latest_memory = Memory.query.order_by(desc("release_date")).first()
        if latest_memory:
            return redirect(url_for('main.memory', id=latest_memory.id))
        else:
            return redirect(url_for('main.nomemory'))

@bp.route('/memory/<int:id>', methods=['GET'])
@login_required
def memory(id, today = False):
    """Memory page
    """
    memory = get_memory_by_id(id)
    if today:
        title = "Today's memory"
    else:
        title = memory.release_date.strftime("%d. %B %Y's memory")
    previous_day_memory = get_memory_by_date(memory.release_date - timedelta(days=1))
    next_day_memory = get_memory_by_date(memory.release_date + timedelta(days=1))
    thumbnail_path = f"memories/thumbs/{memory.filename}"
    return render_template('memory.html',
                           memory=memory,
                           title=title,
                           previous_day_memory=previous_day_memory,
                           next_day_memory=next_day_memory,
                           thumbnail_path=thumbnail_path)

@bp.route('/nomemory', methods=['GET'])
@login_required
def nomemory():
    """No memory page
    """
    return render_template('nomemory.html')

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
