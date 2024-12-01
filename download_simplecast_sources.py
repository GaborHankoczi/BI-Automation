import codecs
import json
import requests

with open("simplecast_api_key.txt", "r") as f:
    api_key = f.read()


url = "https://api.simplecast.com/podcasts?limit=200"

payload={}
headers = {"authorization": "Bearer " + api_key}

response = requests.request("GET", url, headers=headers, data=payload)


podcasts = json.loads(response.text)

data_items = []

anonimize = True

for podcast in podcasts['collection']:
    # get episodes for each podcast
    url = "https://api.simplecast.com/analytics/episodes?limit=200&podcast=" + podcast['id']
    
    response = requests.request("GET", url, headers=headers, data=payload)
    analytics = json.loads(response.text)
    for episode in analytics['collection']:
        data_items.append({'podcast': podcast['title'], 'season': episode['season']['number'], 'episode': episode['number'], 'title': episode['title'], 'downloads': episode['downloads']['total'], 'publishedAt': episode['published_at']})

with codecs.open("simplecast_analytics.csv", "w", "utf-8") as file:
    file.write("podcast|season|episode|title|downloads|publishedAt\n")
    for item in data_items:
        podcast = str(hash(str(item['podcast']))) if anonimize else str(item['podcast'])
        title = str(hash(str(item['title']))) if anonimize else str(item['title'])
        file.write(podcast + "|" + str(item['season']) + "|" + str(item['episode']) + "|" + title + "|" + str(item['downloads']) + "|" + str(item['publishedAt']).split('T')[0] + "\n")

