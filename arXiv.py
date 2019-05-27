import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

cred = credentials.Certificate('./serviceAccount.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

SLACK_API_URL = os.environ.get('SLACK_API_URL')
ARXIV_API_URL = os.environ.get('ARXIV_API_URL')

def parse(data, tag):

    pattern = "<" + tag + ">([\s\S]*?)<\/" + tag + ">"
    if all:
        obj = re.findall(pattern, data)
    return obj

query = '((abs:medicine)+OR+(abs:medical)+OR+(abs:doctor))+AND+((abs:machine\ learning)+OR+(abs:deep\ learning)+OR+(abs:neural\ network))'

papers = db.collection('papers').stream()
id_list = []
for paper in papers:
    id_list.append(paper.id)

url = 'http://export.arxiv.org/api/query?search_query=' + query + '&start=0&max_results=100&sortBy=lastUpdatedDate&sortOrder=descending'
data = requests.get(url).text
entries = parse(data, "entry")

counter = 0

for entry in entries:
    url = parse(entry, 'id')[0]
    if not(url.split('/')[-1] in id_list):
        title = parse(entry, "title")[0]
        date = parse(entry, "published")[0]
        abstract = parse(entry, "summary")[0]
        message = "\n".join(["=" * 10, "Title:  " + title, "URL: " + url, "Published: " + date])
        requests.post(SLACK_API_URL, json={"text": message})
        db.collection('papers').document(url.split('/')[-1]).set({
            'title': title,
            'url': url,
            'date': date,
            'abstract': abstract
        })
        counter += 1
        if counter == 10:
            break

if counter == 0 and len(entries) == 0:
    requests.post(SLACK_API_URL, json={"text": "There is no papers today..."})

requests.post(SLACK_API_URL, json={"text": "Hello! Today's papers!!"})
