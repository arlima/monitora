""" Endpoint implements the module that sends signals to the server"""
import time
import requests
from requests.auth import HTTPBasicAuth
import yaml

def main():
    """main is the main function"""
    config_file = open("/etc/monitora/endpoint.yml", 'r', encoding="utf8")
    config = yaml.safe_load(config_file)

    while True:
        try:
            auth = HTTPBasicAuth(config["USER"], config["PWD"])
            requests.post(config["SERVER"], data = {'host':config["HOST"]}, auth=auth)
        except Exception:
            print("Server error")
        time.sleep(config["INTERVAL"])

if __name__ == "__main__":
    main()
