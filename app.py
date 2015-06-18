import random
import time
import logging

import soundcloud
import requests
import redis
from rq import Queue

import os

from flask import Flask, url_for, render_template, redirect
app = Flask(__name__)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

client = soundcloud.Client(client_id=os.environ['SOUNDCLOUD_CLIENT_ID'])

def make_redis(conn_str):
    if conn_str == 'localhost':
        return redis.StrictRedis()
    return redis.from_url(conn_str)

redis_addr = os.environ.get('REDIS_URL', 'localhost')
r = make_redis(redis_addr)
q = Queue(connection=r)

def fetch_a_lonely_track(sc_client):
    logging.info("starting track finding job...")
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
        try:
            if sads.playback_count > 0:
                r.sadd("lc:seen_tracks", random_track)
        except AttributeError:
            logging.warning('no playbackcount on %s' % sads.permalink_url)
            r.sadd("lc:seen_tracks", random_track)
            continue
        count = sads.playback_count
    r.lpush("lc:tries", tries)
    r.lpush("lc:lonelytracks", sads.id)
    logging.info("finished track finding job...")
    return True

upcoming = q.enqueue(fetch_a_lonely_track, client)
another = q.enqueue(fetch_a_lonely_track, client)
onemore = q.enqueue(fetch_a_lonely_track, client)

@app.route('/')
def index():
    return render_template('index.html', lonely=url_for('find_lonely'))

@app.route('/all')
def find_lonely():
    while r.llen("lc:lonelytracks") < 1:
        #wait for queue to catchup
        time.sleep(1)
    sad_id = r.lpop("lc:lonelytracks")
    upcoming = q.enqueue(fetch_a_lonely_track, client)
    return redirect(url_for('lonely_track', trackid=sad_id), code=307)

@app.route('/track/<trackid>')
def lonely_track(trackid):
    sad = client.get('/tracks/%s'%trackid)
    return render_template("track.html", lonely=url_for('find_lonely'), sad=sad)

if __name__ == '__main__':
    app.run(debug=True)