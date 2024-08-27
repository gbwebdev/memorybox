import logging
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, send_from_directory, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from datetime import date, timedelta

# from memorybox.db import get_db
from memorybox.db import db
from memorybox.tools.misc import url_has_allowed_host_and_scheme
from memorybox.model.user import User

logger = logging.getLogger("memorybox")

bp = Blueprint('auth',  __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user, remember=remember)

        _next = request.args.get('next')
        # url_has_allowed_host_and_scheme should check if the url is safe
        # for redirects, meaning it matches the request host.
        # See Django's url_has_allowed_host_and_scheme for an example.
        if not url_has_allowed_host_and_scheme(_next):
            return abort(400)

        return redirect(_next or url_for('index'))
    return render_template('login.html')


@bp.route('/logout')
def logout():
    return 'Logout'