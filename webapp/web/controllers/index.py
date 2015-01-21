# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session


index_page = flask.Blueprint("index_page", __name__)
@index_page.route('/')
def func_name():
	templateDict = {}

	return render_template("index.html", **templateDict)




