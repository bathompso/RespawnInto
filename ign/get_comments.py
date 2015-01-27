import json, urllib2

apiKey = 'fUL0LOndkWY27POmnXGnK9jLJ8sAc1rJr385JjQl0yL6KuDRu5yJa1sjHFNTExLe'
#apiKey = 'NxsrfDm7ylqvsAnSv1R64Qo7Za8TR0XviB8XRCF3ExPl4zL8CNK54JeqtECHvLCt'

reviewsData = json.load(open('../json/ignReviews.json'))

try:
	commentData = json.load(open('../json/ignComments.json'))
except:
	commentData = []

for r in reviewsData:
	if r['reviewURL'] in [x['reviewLink'] for x in commentData]: continue
	if 'reviewText' not in r.keys(): continue
	print('Querying "%s"' % r['reviewURL'])
	threads = json.load(urllib2.urlopen('http://disqus.com/api/3.0/threads/list.json?api_key=%s&forum=ign-articles&thread=link:%s' % (apiKey, r['reviewURL'])))
	print('    Found %d Threads' % len(threads['response']))
	if len(threads['response']) != 1: 
		commentData.append({'reviewLink': r['reviewURL'], 'comments': [], 'contributors': []})
		json.dump(commentData, open('ignComments.json', 'w'))
		continue

	commentText, commentAuthors, nlast, offset = [], [], 100, 0
	while nlast == 100 and len(commentAuthors) < 500:
		posts = json.load(urllib2.urlopen('https://disqus.com/api/3.0/posts/list.json?api_key=%s&forum=ign-articles&limit=100&offset=%d&thread=%s' % (apiKey, offset, threads['response'][0]['id'])))
		if len(posts['response']) == 0:
			nlast = 0
			continue
		if posts['response'][0]['raw_message'] in commentText: 
			nlast = 0
			continue
		for p in posts['response']:
			if p['parent'] is None:
				commentAuthors.append(p['author']['name'])
				commentText.append(p['raw_message'])
		nlast = len(posts['response'])
		offset += nlast
	print('    Found %d Comments' % len(commentText))

	commentData.append({'reviewLink': r['reviewURL'], 'comments': commentText, 'contributors': commentAuthors})

	json.dump(commentData, open('ignComments.json', 'w'))


