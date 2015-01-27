from __future__ import print_function, division
import numpy as np
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer

def ign_comment_similarity(session, name):
	# Get all games and commenters
	session.execute('SELECT games.index, games.name, ign_comments.contributors FROM (games JOIN ign_comments ON (games.index = ign_comments.games_index)) JOIN gamespot ON (games.index = gamespot.games_index)')
	commentData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(commentData)) if commentData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Compute jaccard coefficients
	jaccard = []
	for i in range(len(commentData)):
		union = len(np.unique(commentData[i]['contributors'].split(', ') + commentData[gloc]['contributors'].split(', ')))
		total = len(np.unique(commentData[i]['contributors'].split(', '))) + len(np.unique(commentData[gloc]['contributors'].split(', ')))
		if union >= 10: jaccard.append(2 * (1 - union / total))
		else: jaccard.append(0)
	sortScore = np.argsort(jaccard)
	bestIndex = [commentData[sortScore[-x-1]]['index'] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	bestScore = [jaccard[sortScore[-x-1]] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	return bestIndex, bestScore

def ign_comment_random(session, name):
	# Get all games and commenters
	session.execute('SELECT games.index, games.name, ign_comments.contributors FROM (games JOIN ign_comments ON (games.index = ign_comments.games_index)) JOIN gamespot ON (games.index = gamespot.games_index)')
	commentData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(commentData)) if commentData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Randomly sort returned games
	randomScore = np.random.rand(len(commentData))
	sortScore = np.argsort(randomScore)
	bestIndex = [commentData[sortScore[-x-1]]['index'] for x in range(len(sortScore)) if sortScore[-x-1] != gloc]
	return bestIndex

def gs_comment_similarity(session, name):
	# Get all games and commenters
	session.execute('SELECT games.index, games.name, gamespot.contributors FROM games JOIN gamespot ON (games.index = gamespot.games_index)')
	commentData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(commentData)) if commentData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Compute jaccard coefficients
	jaccard = []
	for i in range(len(commentData)):
		union = len(np.unique(commentData[i]['contributors'].split(', ') + commentData[gloc]['contributors'].split(', ')))
		total = len(np.unique(commentData[i]['contributors'].split(', '))) + len(np.unique(commentData[gloc]['contributors'].split(', ')))
		if union >= 10: jaccard.append(2 * (1 - union / total))
		else: jaccard.append(0)
	sortScore = np.argsort(jaccard)
	bestIndex = [commentData[sortScore[-x-1]]['index'] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	bestScore = [jaccard[sortScore[-x-1]] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	return bestIndex, bestScore

def ign_review_similarity(session, name):
	# Get all games and review text
	session.execute('SELECT games.index, games.name, ign_reviews.review FROM (games JOIN ign_reviews ON (games.index = ign_reviews.games_index)) JOIN gamespot ON (games.index = gamespot.games_index)')
	reviewData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(reviewData)) if reviewData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Compute TF-IDF similarities between reviews
	tfidf = TfidfVectorizer(norm='l2').fit_transform([x['review'] for x in reviewData])
	similarity = (tfidf * tfidf.T)
	tfidfscore = [similarity[gloc,x] for x in range(similarity.shape[1])]
	sortScore = np.argsort(tfidfscore)
	bestIndex = [reviewData[sortScore[-x-1]]['index'] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0]
	bestScore = [tfidfscore[sortScore[-x-1]] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0]
	return bestIndex, bestScore

def gs_review_similarity(session, name):
	# Get all games and review text
	session.execute('SELECT games.index, games.name, gamespot.review FROM games JOIN gamespot ON (games.index = gamespot.games_index)')
	reviewData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(reviewData)) if reviewData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Compute TF-IDF similarities between reviews
	tfidf = TfidfVectorizer(norm='l2').fit_transform([x['review'] for x in reviewData])
	similarity = (tfidf * tfidf.T)
	tfidfscore = [similarity[gloc,x] for x in range(similarity.shape[1])]
	sortScore = np.argsort(tfidfscore)
	bestIndex = [reviewData[sortScore[-x-1]]['index'] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0]
	bestScore = [tfidfscore[sortScore[-x-1]] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0]
	return bestIndex, bestScore

def gs_genre_similarity(session, name):
	# Get selected game and all associated subgenres
	session.execute('SELECT games.index, genres_gamespot.name FROM (games JOIN games_to_genres_gamespot ON (games.index = games_to_genres_gamespot.games_index)) JOIN genres_gamespot ON (genres_gamespot.index = games_to_genres_gamespot.genres_gamespot_index) WHERE games.name = "%s"' % name)
	gameGenres = session.fetchall()
	if len([x['name'] for x in gameGenres]) == 0: return [], []
	# Find games with the most overlapping subgenres
	qstr = 'SELECT games.index, games.ign_score, COUNT(genres_gamespot.name) FROM (games JOIN games_to_genres_gamespot ON (games.index = games_to_genres_gamespot.games_index)) JOIN genres_gamespot ON (genres_gamespot.index = games_to_genres_gamespot.genres_gamespot_index) WHERE genres_gamespot.name = "%s" AND games.name != "%s" GROUP BY games.index' % ('" OR genres_gamespot.name = "'.join([x['name'] for x in gameGenres]), name)
	#print(qstr)
	session.execute(qstr)
	genreData = session.fetchall()
	genreScore = [x['COUNT(genres_gamespot.name)'] + x['ign_score'] / 10 for x in genreData]
	sortScore = np.argsort(genreScore)
	bestIndex = [genreData[sortScore[-x-1]]['index'] for x in range(len(sortScore)) if genreScore[sortScore[-x-1]] > 1]
	bestScore = [genreScore[sortScore[-x-1]] for x in range(len(sortScore)) if genreScore[sortScore[-x-1]] > 1]
	return bestIndex, bestScore

def ign_genre_similarity(session, name):
	session.execute('SELECT games.index, genres.name FROM (games JOIN games_to_genres ON (games.index = games_to_genres.games_index)) JOIN genres ON (games_to_genres.genres_index = genres.index) WHERE games.name = "%s"' % name)
	gameGenres = session.fetchall()
	if len(gameGenres) == 0: return [], []
	# Find games within the same genre
	session.execute('SELECT games.index, games.ign_score, genres.name FROM (games JOIN games_to_genres ON (games.index = games_to_genres.games_index)) JOIN genres ON (games_to_genres.genres_index = genres.index) WHERE genres.name = "%s"' % gameGenres[0]['name'])
	genreData = session.fetchall()
	genreScore = [x['ign_score'] / 10 for x in genreData]
	sortScore = np.argsort(genreScore)
	bestIndex = [genreData[sortScore[-x-1]]['index'] for x in range(len(sortScore))]
	bestScore = [genreScore[sortScore[-x-1]] for x in range(len(sortScore))]
	return bestIndex, bestScore

def test_similarity(name):
	db = pymysql.connect(user='root', host='localhost', db='games')
	session = db.cursor(pymysql.cursors.DictCursor)
	bestIdx, bestScore = ign_comment_similarity(session, name)
	for i in range(12):
		session.execute('SELECT games.name FROM games WHERE games.index = %s' % bestIdx[i])
		gameName = session.fetchall()
		print(gameName, bestIdx[i], bestScore[i])


if __name__ == "__main__":
	db = pymysql.connect(user='root', host='localhost', db='games')
	session = db.cursor(pymysql.cursors.DictCursor)
	
	session.execute('SELECT games.name FROM (games JOIN ign_comments ON (games.index = ign_comments.games_index)) JOIN gamespot ON (games.index = gamespot.games_index);')
	overlapGames = session.fetchall()
	novrCommentsIGN, novrIGN, novrCommentsGS, novrGS, novrGenreGS, novrGenreIGN, novrRandom = [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
	noGenreGS, noGenreIGN = 0, 0
	for g in range(len(overlapGames)):
		if g % 20 == 0: print('Working on game %3d / %3d...' % (g, len(overlapGames)))
	
		ignCommentIdx, ignCommentScore = ign_comment_similarity(session, overlapGames[g]['name'])
		ignReviewIdx, ignReviewScore = ign_review_similarity(session, overlapGames[g]['name'])
	
		gsCommentIdx, gsCommentScore = gs_comment_similarity(session, overlapGames[g]['name'])
		gsReviewIdx, gsReviewScore = gs_review_similarity(session, overlapGames[g]['name'])
	
		gsGenreIdx, gsGenreScore = gs_genre_similarity(session, overlapGames[g]['name'])
		ignGenreIdx, ignGenreScore = ign_genre_similarity(session, overlapGames[g]['name'])
	
		ignRandomIdx = ign_comment_random(session, overlapGames[g]['name'])
	
		for i in range(4):
			topRank = [6, 12, 18, 24][i]
			testIdx = gsCommentIdx
			if 2*topRank - len(np.unique(ignCommentIdx[:topRank] + testIdx[:topRank])) > 0: novrCommentsIGN[i] += 1
			if 2*topRank - len(np.unique(ignReviewIdx[:topRank]  + testIdx[:topRank])) > 0: novrIGN[i] += 1
			if 2*topRank - len(np.unique(gsCommentIdx[:topRank]  + testIdx[:topRank])) > 0: novrCommentsGS[i] += 1
			if 2*topRank - len(np.unique(gsReviewIdx[:topRank]   + testIdx[:topRank])) > 0: novrGS[i] += 1
			if 2*topRank - len(np.unique(gsGenreIdx[:topRank]    + testIdx[:topRank])) > 0: novrGenreGS[i] += 1
			if 2*topRank - len(np.unique(ignGenreIdx[:topRank]   + testIdx[:topRank])) > 0: novrGenreIGN[i] += 1
			if 2*topRank - len(np.unique(ignRandomIdx[:topRank]  + testIdx[:topRank])) > 0: novrRandom[i] += 1
	
		if len(gsGenreIdx) < 24: noGenreGS += 1
		if len(ignGenreIdx) < 24: noGenreIGN += 1
		
	print('Total:', len(overlapGames))
	print('IGN Comments:', novrCommentsIGN)
	print('IGN Reviews:', novrIGN)
	print('GS Comments:', novrCommentsGS)
	print('GS Reviews:', novrGS)
	print('GS Genres:', novrGenreGS, noGenreGS)
	print('IGN Genres:', novrGenreIGN, noGenreIGN)
	print('Random:', novrRandom)




