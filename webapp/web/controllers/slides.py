# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session


slides_page = flask.Blueprint("slides_page", __name__)
@slides_page.route('/slides.html')
def func_name():
	templateDict = {}

	return render_template("slides.html", **templateDict)




