from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
import yaml

config_file = open("/etc/monitora/monitora.yml", 'r')
config = yaml.safe_load(config_file)

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return config["USER_DATA"].get(username) == password

# --- classic api endpoint ---
@app.route("/signal", methods = ['POST'])
@auth.login_required
def signal():
    data = request.form
    host = data.get('host')
    if host == None:
        response = {"message" : "No host"}
        return response, 400

    ts = int(datetime.now().timestamp())
    with open(config["PATH"]+host+".host", 'w') as a_writer:
        a_writer.write(f"{ts}")

    response = {"message" : "Signal Registered"}
    return response, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1234, debug=False)
