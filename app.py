import random

import soundcloud
import requests
import redis
import os

from flask import Flask, url_for, render_template, redirect
app = Flask(__name__)

client = soundcloud.Client(client_id=os.environ['SOUNDCLOUD_CLIENT_ID'])

def breakup_connect_str(conn_str):
    if conn_str == 'localhost':
        return {"host":"localhost",
                "port":6379,
                "password":None}
    parsed = requests.utils.urlparse(conn_str).netloc
    _, host, port = parsed.split(':')
    password, host = host.split('@')
    return {"host":host, "port":port, "password":password}

redis_addr = os.environ.get('REDIS_URL', 'localhost')
redis_conn = breakup_connect_str(redis_addr)
r = redis.StrictRedis(host=redis_conn['host'], port=redis_conn['port'], password=redis_conn['password'])

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
    return render_template('index.html', lonely=url_for('find_lonely'))

@app.route('/all')
def find_lonely():
    sad = fetch_a_lonely_track(client)
    return redirect(url_for('lonely_track', trackid=sad.id), code=307)

@app.route('/track/<trackid>')
def lonely_track(trackid):
    sad = client.get('/tracks/%s'%trackid)
    return render_template("track.html", lonely=url_for('find_lonely'), sad=sad)

if __name__ == '__main__':
    app.run(debug=True)