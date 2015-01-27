#!/usr/bin/python
from __future__ import print_function
import os, sys, socket, flask, jinja_filters
from inspect import getmembers, isfunction
import json
import pymysql

def create_app(debug=True):
    app = flask.Flask(__name__)
    app.debug = debug

    app.platforms = ['Xbox 360', 'Xbox One', 'PS3', 'PS4', 'Wii', 'Wii U', 'PC', 'iPhone', 'Android', 'WinPhone']

    # Define custom filters into the Jinja2 environment.
    custom_filters = {name: function
                      for name, function in getmembers(jinja_filters)
                      if isfunction(function)}
    app.jinja_env.filters.update(custom_filters)

    if app.debug == False:
    	# ----------------------------------------------------------
        # Set up getsentry.com logging - only use when in production
        # ----------------------------------------------------------
        #from raven.contrib.flask import Sentry
        
        #dsn = ''
        #app.config['SENTRY_DSN'] = dsn
        #sentry = Sentry(app)
        # ----------------------------------------------------------
    
        # Configuration when running under uWSGI
        try:
            import uwsgi
            app.use_x_sendfile = True
        except ImportError:
            # not running under uWSGI (and presumably, nginx)
            pass

    # Determine which configuration file should be loaded based on which
    # server we are running on. This value is set in the uWSGI config file
    # for each server.
    if app.debug:
        server_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'configuration_files',
                                              'aws.cfg')
    else:
        try:
            import uwsgi
            server_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'configuration_files',
                                              uwsgi.opt['flask-config-file']) # to set
        except ImportError:
            sys.exit(1)

    print("Loading config file: {0}".format(server_config_file))
    app.config.from_pyfile(server_config_file)

    #print(app.config)
    print("Server_name = {0}".format(app.config["SERVER_NAME"]))
    
    
    # Create database connection (which will exist throughout the entire app)
    #with app.app_context():
    #    from .model.database import db
    
    db = pymysql.connect(user=app.config['DB_USER'], passwd=app.config['DB_PASS'], host=app.config['DB_HOST'], db=app.config['DB_NAME'])
    db.autocommit(1)
    session = db.cursor(pymysql.cursors.DictCursor)
    app.db = session

    # Register blueprints
    from .controllers.index import index_page
    from .controllers.slides import slides_page
    from .controllers.analysis import analysis_page
    from .controllers.recommendations import recommendations_page
    
    app.register_blueprint(index_page)
    app.register_blueprint(slides_page)
    app.register_blueprint(analysis_page)
    app.register_blueprint(recommendations_page)
    

    return app

# Perform early app setup here.
