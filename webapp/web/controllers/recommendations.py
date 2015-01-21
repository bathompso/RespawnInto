# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session


recommendations_page = flask.Blueprint("recommendations_page", __name__)
@recommendations_page.route('/recommendations.html', methods=['GET'])
def func_name():
	templateDict = {}

	gameTitle = request.args.get('gameTitle', None)
	X360 = request.args.get('X360', False)
	XOne = request.args.get('XOne', False)
	PS3  = request.args.get('PS3', False)
	PS4  = request.args.get('PS4', False)
	Wii  = request.args.get('Wii', False)
	WiiU = request.args.get('WiiU', False)

	if gameTitle: templateDict['gameTitle'] = gameTitle
	platformBool, platformName = [X360, XOne, PS3, PS4, Wii, WiiU], ['Xbox 360', 'Xbox One', 'PS3', 'PS4', 'Wii', 'Wii U']
	usablePlatforms = [platformName[x] for x in range(len(platformName)) if platformBool[x]]
	if len(usablePlatforms) < 2:
		platformString = ''.join(usablePlatforms)
	else:
		platformString = ', '.join(usablePlatforms[:-1]) + ' and %s' % usablePlatforms[-1]
	print(platformString)
	templateDict['usablePlatforms'] = platformString

	return render_template("recommendations.html", **templateDict)




