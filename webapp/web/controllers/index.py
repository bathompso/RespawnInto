# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session
import pymysql


index_page = flask.Blueprint("index_page", __name__)
@index_page.route('/')
def func_name():
	db = pymysql.connect(user=current_app.config['DB_USER'], passwd=current_app.config['DB_PASS'], host=current_app.config['DB_HOST'], db=current_app.config['DB_NAME'])
	session = db.cursor(pymysql.cursors.DictCursor)

	templateDict = {}
	session.execute('SELECT games.name from (games LEFT JOIN ign_comments ON (games.index = ign_comments.games_index)) LEFT JOIN ign_reviews ON (games.index = ign_reviews.games_index) WHERE ign_comments.games_index > -1 OR ign_reviews.games_index > -1')
	gameNames = session.fetchall()
	print(len(gameNames))
	templateDict['gameNames'] = [x['name'] for x in gameNames]
	templateDict['platforms'] = current_app.platforms

	return render_template("index.html", **templateDict)




