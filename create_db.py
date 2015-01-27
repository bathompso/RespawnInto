from __future__ import print_function, division
import json
import numpy as np
import pandas as pd
import pymysql
import unidecode
import os

if (os.path.dirname(os.path.realpath(__file__))).find('ubuntu') >= 0: cfg_file = 'aws.cfg'
else: cfg_file = 'bathompso.com.cfg'
cfg = {}
with open('webapp/web/configuration_files/' + cfg_file) as df:
    for l in df.read().splitlines():
        tmp = l.split(' = ')
        try: cfg[tmp[0]] = tmp[1].replace("'", "")
        except: pass

# Open DB
db = pymysql.connect(user=cfg['DB_USER'], passwd=cfg['DB_PASS'], host=cfg['DB_HOST'], db=cfg['DB_NAME'])
db.autocommit(1)
session = db.cursor(pymysql.cursors.DictCursor)

# Read in all data
ignData = pd.read_json('data/ignStrip.json')
imageData = pd.read_json('data/ignImages.json')

# Match boxart images to games
ignImages = []
for i in range(ignData.shape[0]):
    imageTable = imageData[imageData['reviewLink'] == ignData.loc[i, 'reviewLink']]
    if imageTable.shape[0] == 0:
        ignImages.append('')
        continue
    ignImages.append(imageTable['boxart'].values[0])
ignImages = np.array(ignImages)

# Save all platforms to database
allPlatforms = []
for i in range(ignData.shape[0]):
    for p in ignData.loc[ignData.index[i], 'platforms']:
        allPlatforms.append(p)
allPlatforms = pd.DataFrame({'name': np.unique(allPlatforms)})
allPlatforms.to_sql('platforms', db, flavor='mysql')

# Save all publishers to database
allPublishers = np.unique([ignData.loc[ignData.index[x], 'publisher'] for x in range(ignData.shape[0])])
allPublishers = pd.DataFrame({'name': np.unique(allPublishers)})
allPublishers.to_sql('publishers', db, flavor='mysql')

# Save all developers to database
allDevelopers = np.unique([ignData.loc[ignData.index[x], 'developer'] for x in range(ignData.shape[0])])
allDevelopers = pd.DataFrame({'name': np.unique(allDevelopers)})
allDevelopers.to_sql('developers', db, flavor='mysql')

# Save all genres to database
allGenres = np.unique([ignData.loc[ignData.index[x], 'genre'] for x in range(ignData.shape[0])])
allGenres = pd.DataFrame({'name': np.unique(allGenres)})
allGenres.to_sql('genres', db, flavor='mysql')

# Save all game information to database
gameTable = pd.DataFrame({'name': ignData['name'].values, 
                          'ign_score': ignData['ignScore'].values, 
                          'comm_score': ignData['commScore'].values,
                          'release_date': ignData['releaseDate'].values,
                          'review_date': ignData['reviewDate'].values,
                          'review_link': ignData['reviewLink'].values,
                          'box_art': ignImages })
session.execute('''CREATE TABLE games ( 
                    `index` int AUTO_INCREMENT NOT NULL PRIMARY KEY, 
                    comm_score float,
                    ign_score float,
                    name varchar(100),
                    release_date varchar(100), 
                    review_date varchar(100), 
                    review_link text,
                    box_art varchar(200) );''')
for i in range(gameTable.shape[0]):
    column_name, values = [], []
    if not np.isnan(gameTable.loc[i, 'comm_score']):
        column_name.append('comm_score'); values.append(gameTable.loc[i, 'comm_score'])
    if not np.isnan(gameTable.loc[i, 'ign_score']):
        column_name.append('ign_score'); values.append(gameTable.loc[i, 'ign_score'])
    column_name.append('name'); values.append('"'+unidecode.unidecode(gameTable.loc[i, 'name']).replace('"',"'")+'"')
    column_name.append('release_date'); values.append('"'+gameTable.loc[i, 'release_date']+'"')
    column_name.append('review_date'); values.append('"'+gameTable.loc[i, 'review_date']+'"')
    column_name.append('review_link'); values.append('"'+gameTable.loc[i, 'review_link']+'"')
    column_name.append('box_art'); values.append('"'+gameTable.loc[i, 'box_art']+'"')
    qstr = 'INSERT INTO games (%s) VALUES (%s);' % (', '.join([str(x) for x in column_name]), ', '.join([str(x) for x in values]))
    session.execute(qstr)

# Connect games to genres
session.execute('SELECT * from genres')
genreSQL = session.fetchall()
session.execute('''CREATE TABLE games_to_genres (
                    `index` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    games_index int, 
                    genres_index int);''')
for i in range(ignData.shape[0]):
    thisgenre = ignData.loc[ignData.index[i], 'genre']
    genreKey = [x['index'] for x in genreSQL if x['name'] == thisgenre]
    if len(genreKey) == 0: continue
    session.execute('INSERT INTO games_to_genres (games_index, genres_index) VALUES (%d, %d);' % (i+1, genreKey[0]))

# Connect games to platforms
session.execute('SELECT * from platforms')
platformSQL = session.fetchall()
session.execute('''CREATE TABLE games_to_platforms (
                    `index` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    games_index int, 
                    platforms_index int);''')
for i in range(ignData.shape[0]):
    thisplatform = ignData.loc[ignData.index[i], 'platforms']
    for p in thisplatform:
        platformKey = [x['index'] for x in platformSQL if x['name'] == p]
        if len(platformKey) == 0: continue
        session.execute('INSERT INTO games_to_platforms (games_index, platforms_index) VALUES (%d, %d);' % (i+1, platformKey[0]))

# Connect games to publishers
session.execute('SELECT * from publishers')
publisherSQL = session.fetchall()
session.execute('''CREATE TABLE games_to_publishers (
                    `index` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    games_index int, 
                    publishers_index int);''')
for i in range(ignData.shape[0]):
    thispublisher = ignData.loc[ignData.index[i], 'publisher']
    publisherKey = [x['index'] for x in publisherSQL if x['name'] == thispublisher]
    if len(publisherKey) == 0: continue
    session.execute('INSERT INTO games_to_publishers (games_index, publishers_index) VALUES (%d, %d);' % (i+1, publisherKey[0]))

# Connect games to developers
session.execute('SELECT * from developers')
developerSQL = session.fetchall()
session.execute('''CREATE TABLE games_to_developers (
                    `index` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    games_index int, 
                    developers_index int);''')
for i in range(ignData.shape[0]):
    thisdeveloper = ignData.loc[ignData.index[i], 'developer']
    developerKey = [x['index'] for x in developerSQL if x['name'] == thisdeveloper]
    if len(developerKey) == 0: continue
    session.execute('INSERT INTO games_to_developers (games_index, developers_index) VALUES (%d, %d);' % (i+1, developerKey[0]))

# Save reviews to database
session.execute('''CREATE TABLE ign_reviews (
                    `index` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    games_index int, 
                    review text );''')
for i in range(ignData.shape[0]):
    try:
        if str(ignData.loc[i, 'reviewText']) == 'nan': continue
    except:
        pass
    goodreview = unidecode.unidecode(ignData.loc[i, 'reviewText']).replace('"', "'")
    session.execute('''INSERT INTO ign_reviews (games_index, review) VALUES (%d, "%s");''' % (i+1, goodreview))

# Save comments to DB
ignComments = json.load(open('data/ignComments.json'))
games_idx = []
for c in ignComments:
    if len(c['comments']) == 0:
        games_idx.append(-1)
        continue
    gameMatch = ignData[ignData['reviewLink'] == c['reviewLink']]
    if gameMatch.shape[0] > 0:
        games_idx.append(gameMatch.index[0])
    else:
        gameMatch = ignData[ignData['reviewLink'].str.contains(c['reviewLink'].split('/')[-1])]
        if gameMatch.shape[0] > 0:
            games_idx.append(gameMatch.index[0])
        else:
            games_idx.append(-1)
games_idx = np.array(games_idx)

session.execute('''CREATE TABLE ign_comments (
                    `index` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    games_index int, 
                    contributors text );''')
for i in range(len(games_idx)):
    if games_idx[i] < 0: continue
    session.execute('''INSERT INTO ign_comments (games_index, contributors) VALUES (%d, "%s")''' % (games_idx[i]+1, ', '.join([unidecode.unidecode(x).replace('"', "'") for x in ignComments[i]['contributors']])))


# Save gamespot data to database
gsData = json.load(open('json/gamespot.json'))
for g in gsData:
    gsGame = gameTable[gameTable['name'] == g['name']]
    if gsGame.shape[0] > 0:
        g['games_index'] = gsGame.index[0]
    else:
        gsGame = gameTable[gameTable['name'].str.contains(g['name'])]
        if gsGame.shape[0] > 0:
            g['games_index'] = gsGame.index[0]

session.execute('''CREATE TABLE gamespot (
                    `index` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    games_index int,
                    review text,
                    gs_score float,
                    comm_score float,
                    nratings int,
                    contributors text );''')
for g in gsData:
    if 'games_index' not in g.keys(): continue
    session.execute('''INSERT INTO gamespot (games_index, review, gs_score, comm_score, nratings, contributors)  VALUES (%d, "%s", %s, %s, %s, "%s")''' % (g['games_index']+1, unidecode.unidecode(g['review']).replace('"', "'"), g['gsScore'], g['commScore'], g['nRatings'], unidecode.unidecode(', '.join(g['contributors'])).replace('"', "'")))



