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
        file.write(str(item['podcast']) + "|" + str(item['season']) + "|" + str(item['episode']) + "|" + str(item['title']) + "|" + str(item['downloads']) + "|" + str(item['publishedAt']) + "\n")

