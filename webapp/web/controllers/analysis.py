# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session
import pymysql


analysis_page = flask.Blueprint("analysis_page", __name__)
@analysis_page.route('/analysis.html')
def func_name():
	db = pymysql.connect(user=current_app.config['DB_USER'], passwd=current_app.config['DB_PASS'], host=current_app.config['DB_HOST'], db=current_app.config['DB_NAME'])
	session = db.cursor(pymysql.cursors.DictCursor)
	templateDict = {}
	# Build data for first chart
	session.execute('''SELECT games.name, games.ign_score, games.comm_score, genres.name FROM (games JOIN games_to_genres AS gm2gn ON (games.index = gm2gn.games_index)) JOIN genres ON (gm2gn.genres_index = genres.index)''')
	plotData = session.fetchall()
	templateDict['plotData'] = plotData

	return render_template("analysis.html", **templateDict)




