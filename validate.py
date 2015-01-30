from __future__ import print_function, division
import pymysql
import numpy as np
from time import time

def ign_comment_similarity(session, name):
	# Get selected game
	session.execute('SELECT games.index, games.name, ign_comments.contributors FROM games JOIN ign_comments ON (games.index = ign_comments.games_index) WHERE games.index = %d' % name)
	gameData = session.fetchall()
	if len(gameData) == 0: return [], []
	# Get all games and commenters
	session.execute('SELECT games.index, games.name, ign_comments.contributors FROM games JOIN ign_comments ON (games.index = ign_comments.games_index)')
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

def genre_similarity(session, name):
	# Get selected game
	session.execute('SELECT games.index, games.name, genres.name FROM (games JOIN games_to_genres AS gm2gn ON (games.index = gm2gn.games_index)) JOIN genres ON (gm2gn.genres_index = genres.index) WHERE games.index = %d' % name)
	gameData = session.fetchall()
	if len(gameData) == 0: return [], []
	# Get all games and commenters
	session.execute('SELECT games.index, games.name, games.ign_score, genres.name FROM (games JOIN games_to_genres AS gm2gn ON (games.index = gm2gn.games_index)) JOIN genres ON (gm2gn.genres_index = genres.index) WHERE genres.name = "%s"' % gameData[0]['genres.name'])
	genreData = session.fetchall()
	# Compute jaccard coefficients
	genreScore = [x['ign_score'] for x in genreData]
	sortScore = np.argsort(genreScore)
	bestIndex = [genreData[sortScore[-x-1]]['index'] for x in range(len(genreScore)) if genreScore[sortScore[-x-1]] > 0]
	bestScore = [genreScore[sortScore[-x-1]] for x in range(len(genreScore)) if genreScore[sortScore[-x-1]] > 0]
	return bestIndex, bestScore


db = pymysql.connect(user='root', host='localhost', db='games')
db.autocommit(1)
session = db.cursor(pymysql.cursors.DictCursor)
	
session.execute('''SELECT gamespot.index, gamespot.contributors FROM gamespot''')
commenters = session.fetchall()
allCommenters = []
for c in commenters:
	for p in np.unique(c['contributors'].split(',')):
		allCommenters.append(p)
commenterCount = {k: allCommenters.count(k) for k in allCommenters}
multiCommenters = {k: v for k,v in commenterCount.iteritems() if v > 1}

commenterGames = {}
for k in multiCommenters.keys():
    session.execute('SELECT gamespot.games_index FROM gamespot WHERE gamespot.contributors LIKE "%'+k+'%"')
    thisGames = session.fetchall()
    commenterGames[k] = [x['games_index'] for x in thisGames]

minIndexes, cnt, t0 = [], 0, time()
for k,v in commenterGames.iteritems():
	if cnt % 50 == 0: print('Working on %d / %d...  ELAPSED: %.1f' % (cnt, len(commenterGames.keys()), time()-t0))
	cnt += 1
	thisminIndexes = []
	for g in v:
		bestIndex, bestScore = ign_comment_similarity(session, g)
		matchIdx = [x for x in range(len(bestIndex)) if bestIndex[x] in v]
		if len(matchIdx) > 0: thisminIndexes.append(min(matchIdx))
	if len(thisminIndexes) > 0: minIndexes.append(min(thisminIndexes))
minIndexes = np.array(minIndexes)
np.savetxt('validate.txt', minIndexes)

minIndexes, cnt, t0 = [], 0, time()
for k,v in commenterGames.iteritems():
	if cnt % 50 == 0: print('Working on %d / %d...  ELAPSED: %.1f' % (cnt, len(commenterGames.keys()), time()-t0))
	cnt += 1
	thisminIndexes = []
	for g in v:
		bestIndex, bestScore = genre_similarity(session, g)
		matchIdx = [x for x in range(len(bestIndex)) if bestIndex[x] in v]
		if len(matchIdx) > 0: thisminIndexes.append(min(matchIdx))
	if len(thisminIndexes) > 0: minIndexes.append(min(thisminIndexes))
minIndexes = np.array(minIndexes)
np.savetxt('validate_genre.txt', minIndexes)

print('Detected %d Gamespot Commenters (of total %d) and %d Games' % (len(minIndexes), len(commenterGames.keys()), 855))
for x in [6, 12, 18, 24, 30, 36, 42]:
	print('%2d: %4d %4d' % (x, len(minIndexes[minIndexes < x]), x / 855 * len(minIndexes)))
