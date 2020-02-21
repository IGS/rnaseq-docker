# auth.py

import os, sys
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask import current_app as app
from flask_login import login_user, logout_user, current_user, login_required
from kerberos import checkPassword
from .models import User
from . import login_manager, sess

# Blueprint Configuration
auth_bp = Blueprint('auth_bp', __name__,
                    template_folder='templates',
                    static_folder='static')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """ Handles the login process. Also removes tmp files """

    # Bypass Login screen if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.sample_info_file'))

    # Bypass login if running in Docker
    if app.config["DOCKER"]:
        login_docker()

    # POST
    if request.method == 'POST':
        username = str(request.form['username'])
        password = str(request.form['password'])
        app.logger.debug('Checking credentials for: ' + username)

        service = app.config['LDAP_SERVICE']
        realm = app.config['LDAP_REALM']
        valid_credentials = False

        valid_credentials = checkPassword(username, password, service, realm)
        if valid_credentials:
            user = User(username, password)
            login_user(user)
            return redirect(url_for('main_bp.sample_info_file'))

        flash('Please check your username and password.')
        return redirect(url_for('auth_bp.login'))

    # GET - Serve login page
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    #remove_temp_files(CURRENT_DIR)
    logout_user()
    #session.clear()
    return redirect(url_for('auth_bp.login'))

@login_manager.user_loader
def load_user(user_id):
    """Retrieves a User, specified by user ID."""
    if user_id is not None:
        return User.get(user_id)
    return None

def login_docker():
    """Special login when Grotto is running in Docker."""
    # Docker instances should not have a logged in user
    app.logger.debug('Spoofing login in Docker container')
    username = 'user'
    password = 'pass'
    user = User(username, password)
    login_user(user)
    return redirect(url_for('main_bp.sample_info_file'))

@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))