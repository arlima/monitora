import requests
from requests.auth import HTTPBasicAuth
import time
import yaml

def main():
    config_file = open("/etc/monitora/endpoint.yml", 'r')
    config = yaml.safe_load(config_file)

    while True:
        try:
            response = requests.post(config["SERVER"], data = {'host':config["HOST"]}, auth=HTTPBasicAuth(config["USER"], config["PWD"]))
        except:
            print("Erro no servidor")
        time.sleep(config["INTERVAL"])

if __name__ == "__main__":
    main()