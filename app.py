import soundcloud
from flask import Flask
from keys import * #stick the api keys here
app = Flask(__name__)

client = soundcloud.Client(client_id=SOUNDCLOUD_CLIENT_ID)

def fetch_a_lonely_track(sc_client):
    pass

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/track/<trackid>')
def lonely_track(trackid):
    return "track %s" % trackid

if __name__ == '__main__':
    app.run()