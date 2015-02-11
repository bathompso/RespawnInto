# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session

from datetime import datetime

about_page = flask.Blueprint("about_page", __name__)
@about_page.route('/about.html')
def func_name():
	templateDict = {}

	# Log something to show somebody hit this page
	print('!!! ABOUT: %s %s' % (datetime.strftime(datetime.now(), "%Y%m%d.%H%M"), request.remote_addr))


	return render_template("about.html", **templateDict)




