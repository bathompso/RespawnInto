# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session
import pymysql
import numpy as np

analysis_page = flask.Blueprint("analysis_page", __name__)
@analysis_page.route('/analysis.html')
def func_name():
	db = pymysql.connect(user=current_app.config['DB_USER'], passwd=current_app.config['DB_PASS'], host=current_app.config['DB_HOST'], db=current_app.config['DB_NAME'])
	session = db.cursor(pymysql.cursors.DictCursor)
	templateDict = {}

	# Genre score difference data
	session.execute('''SELECT games.name, games.ign_score, games.comm_score, genres.name FROM (games JOIN games_to_genres AS gm2gn ON (games.index = gm2gn.games_index)) JOIN genres ON (gm2gn.genres_index = genres.index) WHERE games.ign_score >= 0 AND games.comm_score >= 0''')
	plotData = session.fetchall()

        # Create histogram
        scoreDiff = np.array([x['comm_score'] - x['ign_score'] for x in plotData])
        scoreHist = []
        for b in np.arange(-4, 6.4, 0.4):
                if b % 1 < 0.05 or b % 1 > 0.95: 
                        labelText = '%d' % round(b)
                else: 
                        labelText = ''
                scoreHist.append([labelText, len(scoreDiff[(scoreDiff >= b) & (scoreDiff < b+0.4)])])
        templateDict['scoreHist'] = scoreHist

        # Select out specific interesting genres
        plotDataWeb = {}
        for g in ['Sports', 'RPG', 'Shooter', 'Action']:
                plotDataWeb[g] = [x for x in plotData if x['genres.name'] == g]
	templateDict['plotData'] = plotDataWeb

        # Review length data
        session.execute('''SELECT * FROM ign_reviews''')
        reviewData = session.fetchall()
        reviewLengths = np.array([len(x['review']) for x in reviewData])
        reviewHist = []
        for b in np.arange(0, 18000, 500):
                if b % 2000 == 0:
                        labelText = '%d' % (int(b)/1000)
                else:
                        labelText = ''
                reviewHist.append([labelText, len(reviewLengths[(reviewLengths >= b) & (reviewLengths < b+500)])])
        templateDict['reviewHist'] = reviewHist

	return render_template("analysis.html", **templateDict)




