# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session

import numpy as np
from datetime import datetime

data_page = flask.Blueprint("data_page", __name__)
@data_page.route('/data.html')
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

	current_app.db.execute('''SELECT ign_reviews.review FROM ign_reviews''')
	reviewList = current_app.db.fetchall()
	reviewLengths = np.array([len(x['review']) for x in reviewList])
	reviewData = []
	for l in np.arange(0, 18000, 500):
		if l % 2000 == 0: reviewData.append(['%d' % (l/1000), len(reviewLengths[(reviewLengths >= l) & (reviewLengths < l+500)])])
		else: reviewData.append(['', len(reviewLengths[(reviewLengths >= l) & (reviewLengths < l+500)])])
	templateDict['reviewHist'] = reviewData

	# Log something to show somebody hit this page
	print('!!! DATA: %s %s' % (datetime.strftime(datetime.now(), "%Y%m%d.%H%M"), request.remote_addr))

	return render_template("data.html", **templateDict)




