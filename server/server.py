""" Server implements an API to receive signals from the endpoints """
import re
from datetime import datetime
from flask import Flask, request
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth
import yaml

with open("/etc/monitora/monitora.yml", 'r', encoding="utf8") as config_file:
    config = yaml.safe_load(config_file)

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
        response = {"message" : "No host"}
        return response, 400

    if not re.match(r'^[a-zA-Z0-9_\-]+$', host):
        return {"message": "Invalid host name"}, 400

    now_ts = int(datetime.now().timestamp())
    with open(config["PATH"]+host+".host", 'w', encoding="utf8") as a_writer:
        a_writer.write(f"{now_ts}")

    response = {"message" : "Signal Registered"}
    return response, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config["PORT"], debug=False)
