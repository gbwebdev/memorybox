from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from memorybox.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
  return render_template('index.html')

@bp.route('/settings', methods=('GET', 'POST'))
def settings():
  return render_template('settings.html')

