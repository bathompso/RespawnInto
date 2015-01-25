from __future__ import print_function, division
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from flask import current_app

# Determines whether similar games can be found using commenter similarity, and returns the index of the correct line in the comment file
def has_commenters(data, commentData):
	idx = [x for x in range(len(commentData)) if data['reviewLink'] == commentData[x]['reviewLink']]
	# Somehow cannot find in datafile, see if comment data already exists in original data
	if len(idx) == 0: 
		if 'contributors' not in data.keys(): return False
		else: return -1
	idx = idx[0]
	# Check to make sure the entry we located has comments
	if 'contributors' not in commentData[idx].keys():
		if 'contributors' not in data.keys(): return False
		else: return -1
	# Found a usable review entry
	return idx

# Determines whether similar games can be found using review similarity, and returns the index of the correct line in the review file
def has_review(data, reviewData):
	idx = [x for x in range(len(reviewData)) if data['reviewLink'] == reviewData[x]['reviewURL']]
	# Somehow cannot find in datafile, see if comment data already exists in original data
	if len(idx) == 0: 
		if 'reviewText' not in data.keys(): return False
		else: return -1
	idx = idx[0]
	# Check to make sure the entry we located has comments
	if 'reviewText' not in reviewData[idx].keys():
		if 'reviewText' not in data.keys(): return False
		else: return -1
	# Found a usable review entry
	return idx




# Returns most similar games (in reverse order), when measured by commenter similarity
def commenter_similarity(data, commentData):
	# Determine whether there are comments to compare
	idx = has_commenters(data, commentData)
	if not idx: return [], []
	else:
		if idx > 0: commenters = commentData[idx]['contributors']
		else: commenters = data['contributors']
	# Compute Jaccard Similarity Coefficient for commenters
	jaccard = [2*(1-len(np.unique(commenters + x['contributors'])) / len(list(np.unique(commenters)) + list(np.unique(x['contributors'])))) for x in commentData if 'contributors' in x.keys()]
	jaccard_idx = [commentData[x]['reviewLink'] for x in range(len(commentData)) if 'contributors' in commentData[x].keys()]
	# Sort results and return recommendations
	recommends = [x for x in np.argsort(jaccard) if jaccard[x] > 0 and jaccard[x] < 1]
	recommend_scores = [jaccard[x] for x in recommends]
	recommend_links = [jaccard_idx[x] for x in recommends]
	return recommend_links, recommend_scores

# Returns most similar games (in reverse order), when measured by review similarity
def review_similarity(data, reviewData):
	# Determine whether there is review text to compare for this game
	idx = has_review(data, reviewData)
	if not idx: return [], []
	else:
		if idx > 0: rText = reviewData[idx]['reviewText']
		else: rText = data['reviewText']
	# Create text list for TF-IDF routine
	reviewList = [x['reviewText'] for x in reviewData if 'reviewText' in x.keys()]
	reviewList.append(rText)
	reviewLinks = [x['reviewURL'] for x in reviewData if 'reviewText' in x.keys()]
	# Compute TF-IDF similarity between all available reviews
	tfidf = TfidfVectorizer(norm='l2').fit_transform(reviewList)
	similarity = (tfidf * tfidf.T)
	scores = [similarity[-1,x] for x in range(similarity.shape[1]-1)]
	# Sort results and return recommendations, but knock off the best option, because it is the game we are targeting
	recommends = [x for x in np.argsort(scores)[:-2] if scores[x] > 0 and scores[x] < 0.999]
	recommend_scores = [scores[x] for x in recommends]
	recommend_links = [reviewLinks[x] for x in recommends]
	return recommend_links, recommend_scores

# Returns most popular games (in reverse order) in the same genre
def category_similarity(idx, ignData):
	if 'genre' not in ignData[idx].keys(): return []
	genreGames = []
	for x in range(len(ignData)):
		if 'genre' not in ignData[x].keys(): continue
		if ignData[x]['genre'] == ignData[idx]['genre']: genreGames.append(x)
	genreRatings = [float(ignData[x]['ignScore']) + float(ignData[x]['commScore']) if 'commScore' in ignData[x].keys() else float(ignData[x]['ignScore']) for x in genreGames]
	bestInGenre = [genreGames[x] for x in np.argsort(genreRatings)]
	return bestInGenre




# Format commenter similarity returns into a usable format for flask
def comment_recommendations(gameIdx, usablePlatforms):
	commenter_recommends, commenter_scores = commenter_similarity(current_app.ignData[gameIdx], current_app.ignComments)
	if len(commenter_recommends) == 0:
		return None
	else:
		commenter_return, ctr = [], 0
		while len(commenter_return) < 6:
			# Check if we can find this game in the overall dataset (sometimes weird stuff happens)
			idx = [x for x in range(len(current_app.ignData)) if current_app.ignData[x]['reviewLink'].split('/')[-1] == commenter_recommends[-ctr-1].split('/')[-1]]
			if len(idx) == 0:
				ctr += 1
				continue
			idx = idx[0]
			# Check if this game is available for the selected platforms
			inPlatform = [x for x in current_app.ignData[idx]['platforms'] if x in usablePlatforms]
			if len(inPlatform) == 0:
				ctr += 1
				continue

			gameName = current_app.ignData[idx]['name']
			gamePlatforms = ', '.join(current_app.ignData[idx]['platforms'])
			gameRatingIGN = float(current_app.ignData[idx]['ignScore'])
			gameReview = current_app.ignData[idx]['reviewLink']
			if 'commScore' in current_app.ignData[idx].keys():
				gameRatingComm = float(current_app.ignData[idx]['commScore'])
			else:
				gameRatingComm = -1
			if 'boxart' in current_app.ignData[idx].keys():
				gameArt = current_app.ignData[idx]['boxart']
			else:
				gameArt = ''
			gameRatingSimilarity = commenter_scores[-ctr-1]

			commenter_return.append({'name': gameName, 'platforms': gamePlatforms, 'ign': gameRatingIGN, 'comm': gameRatingComm, 'art': gameArt, 'similarity': gameRatingSimilarity, 'link': gameReview})
			ctr += 1
			if ctr > len(commenter_recommends): break
		return commenter_return

# Format review similarity returns into a usable format for flask
def review_recommendations(gameIdx, usablePlatforms, usedTitles):
	review_recommends, review_scores = review_similarity(current_app.ignData[gameIdx], current_app.ignReviews)
	if len(review_recommends) == 0:
		return None
	else:
		review_return, ctr = [], 0
		while len(review_return) < 6:
			# Check if we can find this game in the overall dataset (sometimes weird stuff happens)
			idx = [x for x in range(len(current_app.ignData)) if current_app.ignData[x]['reviewLink'].split('/')[-1] == review_recommends[-ctr-1].split('/')[-1]]
			if len(idx) == 0:
				ctr += 1
				continue
			idx = idx[0]
			# Check if this game is available for the selected platforms
			inPlatform = [x for x in current_app.ignData[idx]['platforms'] if x in usablePlatforms]
			if len(inPlatform) == 0:
				ctr += 1
				continue
			# Check if this game has already been recommended
			if current_app.ignData[idx]['name'] in usedTitles:
				ctr += 1
				continue

			gameName = current_app.ignData[idx]['name']
			gamePlatforms = ', '.join(current_app.ignData[idx]['platforms'])
			gameRatingIGN = float(current_app.ignData[idx]['ignScore'])
			gameReview = current_app.ignData[idx]['reviewLink']
			if 'commScore' in current_app.ignData[idx].keys():
				gameRatingComm = float(current_app.ignData[idx]['commScore'])
			else:
				gameRatingComm = -1
			if 'boxart' in current_app.ignData[idx].keys():
				gameArt = current_app.ignData[idx]['boxart']
			else:
				gameArt = ''
			gameRatingSimilarity = review_scores[-ctr-1]

			review_return.append({'name': gameName, 'platforms': gamePlatforms, 'ign': gameRatingIGN, 'comm': gameRatingComm, 'art': gameArt, 'similarity': gameRatingSimilarity, 'link': gameReview})
			ctr += 1
		return review_return

# Format best-of returns into a usable format for flask
def genre_recommendations(gameIdx, usablePlatforms, usedTitles):
	genre_recommends = category_similarity(gameIdx, current_app.ignData)
	if len(genre_recommends) == 0:
		return None
	else:
		genre_return, ctr = [], 0
		while len(genre_return) < 6:
			idx = genre_recommends[-ctr-1]
			# Check if this game is available for the selected platforms
			inPlatform = [x for x in current_app.ignData[idx]['platforms'] if x in usablePlatforms]
			if len(inPlatform) == 0:
				ctr += 1
				continue
			# Check if this game has already been recommended
			if current_app.ignData[idx]['name'] in usedTitles:
				ctr += 1
				continue

			gameName = current_app.ignData[idx]['name']
			gamePlatforms = ', '.join(current_app.ignData[idx]['platforms'])
			gameRatingIGN = float(current_app.ignData[idx]['ignScore'])
			gameReview = current_app.ignData[idx]['reviewLink']
			if 'commScore' in current_app.ignData[idx].keys():
				gameRatingComm = float(current_app.ignData[idx]['commScore'])
			else:
				gameRatingComm = -1
			if 'boxart' in current_app.ignData[idx].keys():
				gameArt = current_app.ignData[idx]['boxart']
			else:
				gameArt = ''

			genre_return.append({'name': gameName, 'platforms': gamePlatforms, 'ign': gameRatingIGN, 'comm': gameRatingComm, 'art': gameArt, 'link': gameReview})
			ctr += 1
		return genre_return



