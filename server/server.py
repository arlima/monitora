""" Server implements an API to receive signals from the endpoints """
import re
import sqlite3
from datetime import datetime
from flask import Flask, request
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth
import yaml

with open("/etc/monitora/monitora.yml", 'r', encoding="utf8") as config_file:
    config = yaml.safe_load(config_file)

DB_PATH = config["PATH"] + "monitora.db"

def init_db():
    """ init_db creates the hosts table if it does not exist """
    with sqlite3.connect(DB_PATH) as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("""
            CREATE TABLE IF NOT EXISTS hosts (
                name TEXT PRIMARY KEY,
                last_signal INTEGER NOT NULL
            )
        """)

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

@auth.verify_password
def verify(username, password):
    """ Verify: Check username and password to allow access to the API"""
    if not (username and password):
        return False
    return config["USER"] == username and config["PWD"] == password

# --- classic api endpoint ---
@app.route("/signal", methods = ['POST'])
@auth.login_required
def signal():
    """ Signal: implements the API to receive signals from the endpoints"""
    data = request.form
    host = data.get('host')
    if host is None:
        return {"message": "No host"}, 400

    if not re.match(r'^[a-zA-Z0-9_\-]+$', host):
        return {"message": "Invalid host name"}, 400

    now_ts = int(datetime.now().timestamp())
    with sqlite3.connect(DB_PATH) as con:
        con.execute("INSERT OR REPLACE INTO hosts (name, last_signal) VALUES (?, ?)", (host, now_ts))

    return {"message": "Signal Registered"}, 200

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=config["PORT"], debug=False)
