from __future__ import print_function, division
from similarity_db import *
import pymysql

db = pymysql.connect(user='root', host='localhost', db='games')
db.autocommit(1)
session = db.cursor(pymysql.cursors.DictCursor)

# Find all games to use
session.execute('SELECT games.index, games.name FROM games')
allGames = session.fetchall()

# Create table to store matches
session.execute('DROP TABLE IF EXISTS suggestions')
session.execute('''CREATE TABLE suggestions (
					`index` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
					games_index int,
					list text,
					score text);''')

for g in allGames:
	# Look at overlapping comments
	simIdx, simScore = ign_comment_similarity(session, g['name'])
	if len(simIdx) == 0:
		# Look at similar gamespot reviews
		simIdx, simScore = gs_review_similarity(session, g['name'])
		if len(simIdx) == 0:
			# Look at similar IGN reviews
			simIdx, simScore = ign_review_similarity(session, g['name'])
			if len(simIdx) == 0:
				continue
	print('Inserting %s' % (g['name']))
	session.execute('''INSERT INTO suggestions (games_index, list, score) VALUES (%d, "%s", "%s");''' % (g['index'], ','.join([str(x) for x in simIdx]), ','.join([str(x) for x in simScore])))

