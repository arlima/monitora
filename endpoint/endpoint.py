""" Endpoint implements the module that sends signals to the server"""
import time
import requests
from requests.auth import HTTPBasicAuth
import yaml

with open("/etc/monitora/endpoint.yml", 'r', encoding="utf8") as config_file:
    config = yaml.safe_load(config_file)

def main():
    """ main is the main function """
    auth = HTTPBasicAuth(config["USER"], config["PWD"])
    while True:
        try:
            requests.post(config["SERVER"], data={'host': config["HOST"]}, auth=auth, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Server error: {e}")
        time.sleep(config["INTERVAL"])

if __name__ == "__main__":
    main()
