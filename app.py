import random

import soundcloud
import requests
import redis

from flask import Flask
from keys import * #stick the api keys here
app = Flask(__name__)

client = soundcloud.Client(client_id=SOUNDCLOUD_CLIENT_ID)
r = redis.StrictRedis()

def fetch_a_lonely_track(sc_client):
    count = 1
    tries = 0
    while count>0:
        random_track = random.randint(100, 210900699)
        if r.sismember("lc:seen_tracks", random_track):
            continue
        try:
            tries += 1
            sads = client.get('/tracks/%s'%random_track)
        except requests.HTTPError:
            r.sadd("lc:seen_tracks", random_track)
            continue
        if sads.playback_count > 0:
            r.sadd("lc:seen_tracks", random_track)
        count = sads.playback_count
    r.lpush("lc:tries", tries)
    return sads

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/track/<trackid>')
def lonely_track(trackid):
    return "track %s" % trackid

if __name__ == '__main__':
    app.run()