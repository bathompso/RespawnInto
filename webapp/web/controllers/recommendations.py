# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pymysql

def ign_comment_similarity(session, name, platforms):
	# Get selected game
	session.execute('SELECT games.index, games.name, ign_comments.contributors FROM games JOIN ign_comments ON (games.index = ign_comments.games_index) WHERE games.name = "%s"' % name)
	gameData = session.fetchall()
	if len(gameData) == 0: return [], []
	# Get all games and commenters
	session.execute('SELECT games.index, games.name, ign_comments.contributors FROM ((games JOIN ign_comments ON (games.index = ign_comments.games_index)) JOIN games_to_platforms as g2p ON (games.index = g2p.games_index)) JOIN platforms ON (g2p.platforms_index = platforms.index) WHERE platforms.name = "%s" GROUP BY games.name' % ('" OR platforms.name = "'.join(platforms)))
	commentData = session.fetchall()
	# Compute jaccard coefficients
	jaccard = []
	for i in range(len(commentData)):
		union = len(np.unique(commentData[i]['contributors'].split(', ') + gameData[0]['contributors'].split(', ')))
		total = len(np.unique(commentData[i]['contributors'].split(', '))) + len(np.unique(gameData[0]['contributors'].split(', ')))
		if union >= 10: jaccard.append(2 * (1 - union / total))
		else: jaccard.append(0)
	sortScore = np.argsort(jaccard)
	bestIndex = [commentData[sortScore[-x-1]]['index'] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	bestScore = [jaccard[sortScore[-x-1]] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	return bestIndex, bestScore

def ign_review_similarity(session, name, platforms):
	# Get selected game
	session.execute('SELECT games.index, games.name, ign_reviews.review FROM games JOIN ign_reviews ON (games.index = ign_reviews.games_index) WHERE games.name = "%s"' % name)
	gameData = session.fetchall()
	if len(gameData) == 0: return [], []
	# Get all games and review text
	session.execute('SELECT games.index, games.name, ign_reviews.review FROM ((games JOIN ign_reviews ON (games.index = ign_reviews.games_index)) JOIN games_to_platforms as g2p ON (games.index = g2p.games_index)) JOIN platforms ON (g2p.platforms_index = platforms.index) WHERE platforms.name = "%s" GROUP BY games.name' % ('" OR platforms.name = "'.join(platforms)))
	reviewData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(reviewData)) if reviewData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Compute TF-IDF similarities between reviews
	reviewList = [x['review'] for x in reviewData]
	reviewList.append(gameData[0]['review'])
	tfidf = TfidfVectorizer().fit_transform(reviewList)
	similarity = (tfidf * tfidf.T)
	tfidfscore = [similarity[-1, x] for x in range(similarity.shape[1]-1)]
	sortScore = np.argsort(tfidfscore)
	bestIndex = [reviewData[sortScore[-x-1]]['index'] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0][1:]
	bestScore = [tfidfscore[sortScore[-x-1]] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0][1:]
	return bestIndex, bestScore


recommendations_page = flask.Blueprint("recommendations_page", __name__)
@recommendations_page.route('/recommendations.html', methods=['GET'])
def func_name():
	try:
		current_app.db.execute('SHOW TABLES')
		current_app.db.fetchall()
	except Exception as e:
		print('DB ERROR:', e)
		db = pymysql.connect(user=current_app.config['DB_USER'], passwd=current_app.config['DB_PASS'], host=current_app.config['DB_HOST'], db=current_app.config['DB_NAME'])
		session = db.cursor(pymysql.cursors.DictCursor)
		current_app.db = session
	templateDict = {}

	# Read in all parameters from request
	gameTitle = request.args.get('gameTitle', None)
	usablePlatforms = []
	for p in current_app.platforms:
		thisplat = request.args.get(p, False)
		if thisplat: usablePlatforms.append(p)

	# Prep some easy output to the recommendations page
	templateDict['name'] = gameTitle
	templateDict['linkName'] = '+'.join(gameTitle.split())
	if len(usablePlatforms) < 2: platformString = ''.join(usablePlatforms)
	elif len(usablePlatforms) < 3: platformString = ' and '.join(usablePlatforms)
	else: platformString = ', '.join(usablePlatforms[:-1]) + ', and %s' % usablePlatforms[-1]
	templateDict['usablePlatforms'] = platformString

	# Get recommended games from database
	recommendations = []
	bestIndex, bestScore = ign_comment_similarity(current_app.db, gameTitle, usablePlatforms)
	if len(bestIndex) == 0:
		bestIndex, bestScore = ign_review_similarity(current_app.db, gameTitle, usablePlatforms)

	for i in bestIndex[:12]:
		current_app.db.execute('SELECT * FROM games WHERE games.index = %s' % i)
		gameData = current_app.db.fetchall()
		current_app.db.execute('SELECT platforms.name FROM (games JOIN games_to_platforms AS g2p ON (games.index = g2p.games_index)) JOIN platforms ON (g2p.platforms_index = platforms.index) WHERE games.index = %s AND (platforms.name = "%s")' % (i, '" OR platforms.name = "'.join(usablePlatforms)))
		platformData = current_app.db.fetchall()
		gameData[0]['searchName'] = '+'.join(gameData[0]['name'].split())
		gameData[0]['platform'] = platformData[0]['name']
		recommendations.append(gameData[0])
	templateDict['recommendations'] = recommendations


	return render_template("recommendations.html", **templateDict)



