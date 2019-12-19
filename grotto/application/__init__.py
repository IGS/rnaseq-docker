#!/usr/bin/env python3

#__init__.py
# Create the Grotto application here to serve as the app gateway.

# Module Imports

import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_login import LoginManager
from flask_session import Session

login_manager = LoginManager()
sess = Session()

def create_app():
    """Initialize the core Grotto application."""
    # Initialize application
    app = Flask(__name__, instance_relative_config=False)

    # change ENV by running "export FLASK_ENV=development/production"
    if app.config["ENV"] == "production":
        app.config.from_object('config.DockerProdConfig')
    else:
        app.config.from_object('config.DockerDevConfig')
    app.secret_key = app.config['SECRET_KEY']

    #print(app.config)

    # Initialize logger
    handler = RotatingFileHandler(app.config['LOG_FILE'], backupCount=30)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    # Initialize the login manager
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = ""

    # Intiialize sessions
    sess.init_app(app)

    with app.app_context():
        # Include routes
        from . import routes
        from . import auth

        # Register blueprints
        app.register_blueprint(routes.main_bp)
        app.register_blueprint(auth.auth_bp)

        return app