# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session

import numpy as np

about_page = flask.Blueprint("about_page", __name__)
@about_page.route('/about.html')
def func_name():
	templateDict = {}


	return render_template("about.html", **templateDict)




