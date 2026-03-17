""" Endpoint implements the module that sends signals to the server"""
import time
import requests
from requests.auth import HTTPBasicAuth
import yaml

with open("/etc/monitora/endpoint.yml", 'r', encoding="utf8") as config_file:
    config = yaml.safe_load(config_file)

def main():
    """ main is the main function """
    while True:
        try:
            auth = HTTPBasicAuth(config["USER"], config["PWD"])
            requests.post(config["SERVER"], data = {'host':config["HOST"]}, auth=auth)
        except requests.exceptions.RequestException:
            print("Server error")
        time.sleep(config["INTERVAL"])

if __name__ == "__main__":
    main()
