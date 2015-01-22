# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session

import utils


recommendations_page = flask.Blueprint("recommendations_page", __name__)
@recommendations_page.route('/recommendations.html', methods=['GET'])
def func_name():
	templateDict = {}

	gameTitle = request.args.get('gameTitle', None)
	if gameTitle: 
		gameIdx = [x for x in range(len(current_app.ignData)) if current_app.ignData[x]['name'] == gameTitle]
		if len(gameIdx) == 0:
			return render_template("recommendations.html", **templateDict)
		gameIdx = gameIdx[0]
		templateDict['game'] = current_app.ignData[gameIdx]

	X360 = request.args.get('X360', False)
	XOne = request.args.get('XOne', False)
	PS3  = request.args.get('PS3', False)
	PS4  = request.args.get('PS4', False)
	Wii  = request.args.get('Wii', False)
	WiiU = request.args.get('WiiU', False)
	platformBool, platformName = [X360, XOne, PS3, PS4, Wii, WiiU], ['Xbox 360', 'Xbox One', 'PS3', 'PS4', 'Wii', 'Wii U']
	usablePlatforms = [platformName[x] for x in range(len(platformName)) if platformBool[x]]
	if len(usablePlatforms) < 2:
		platformString = ''.join(usablePlatforms)
	else:
		platformString = ', '.join(usablePlatforms[:-1]) + ' and %s' % usablePlatforms[-1]
	print(platformString)
	templateDict['usablePlatforms'] = platformString

	# Get recommendations based on commenter activity
	commenter_return = utils.comment_recommendations(gameIdx, usablePlatforms)
	templateDict['commenter_recommendations'] = commenter_return

	# Get recommendations based on review similarity
	if commenter_return:
		taken_games = [x['name'] for x in commenter_return]
	else:
		taken_games = []
	reviews_return = utils.review_recommendations(gameIdx, usablePlatforms, taken_games)
	templateDict['reviews_recommendations'] = reviews_return

	# Get best games in associated genre
	if commenter_return and reviews_return:
		taken_games = [x['name'] for x in commenter_return + reviews_return]
	elif commenter_return:
		taken_games = [x['name'] for x in commenter_return]
	elif reviews_return:
		taken_games = [x['name'] for x in reviews_return]
	else:
		taken_games = []
	genre_return = utils.genre_recommendations(gameIdx, usablePlatforms, taken_games)
	templateDict['genre_recommendations'] = genre_return



	return render_template("recommendations.html", **templateDict)



