#!/usr/bin/python
from __future__ import print_function
import os, sys, socket, flask, jinja_filters
from inspect import getmembers, isfunction
import json

def create_app(debug=True):
    app = flask.Flask(__name__)
    app.debug = debug
    # Import the necessary static data at runtime
    app.ignData = json.load(open(os.path.dirname(os.path.abspath(__file__))+'/data/ignStrip.json'))
    app.ignComments = json.load(open(os.path.dirname(os.path.abspath(__file__))+'/data/ignComments.json'))
    app.ignReviews = json.load(open(os.path.dirname(os.path.abspath(__file__))+'/data/ignReviews.json'))


    print("{0}App '{1}' created.{2}".format('\033[92m', __name__, '\033[0m')) # to remove later

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
                                              'bathompso.com.cfg')
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
