"""Checker is the module that reads the .hosts files and notify, via telegram, when the endpoints
are not sending signals
"""

import time
import datetime
import yaml
import requests

def send_message(token, chatid, message):
    """ send a message to a telegram group"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text={message}"
        requests.get(url)
    except requests.exceptions.RequestException:
        print("Telegram server error!")

def main():
    """ main is the main function"""
    with open("/etc/monitora/checker.yml", 'r', encoding="utf8") as config_file:
        config = yaml.safe_load(config_file)

    alert_time = {}

    while True:
        time.sleep(10)
        now = datetime.datetime.now()
        for host in config["HOSTS"]:
            try:
                with open(config["PATH"]+host+".host", 'r', encoding="utf8") as a_reader:
                    last_signal_ts = a_reader.read()
                last_signal_dt = datetime.datetime.fromtimestamp(int(last_signal_ts))
                interval = (now - last_signal_dt).total_seconds()
            except FileNotFoundError:
                interval = 0

            last_dt = alert_time.get(host, 0)
            if last_dt != 0:
                interval_last_alert = (now - last_dt).total_seconds()
            else:
                interval_last_alert = 0

            if interval_last_alert >= config["INTERVAL_RETRY_MESSAGE"]:
                alert_time[host] = now
                msg = f"RETRY: {host} não manda mensagens faz mais de {int(interval/60)} minutos. "
                msg = msg + "Possível problema de rede ou na máquina !"
                send_message(config["TOKEN"], config["CHATID"], msg)
                continue

            if interval >= config["INTERVAL_PROBLEM"] and last_dt == 0:
                alert_time[host] = now
                msg = f"{host} não manda mensagens faz mais de {int(interval/60)} minutos. "
                msg = msg + "Possível problema de rede ou na máquina !"
                send_message(config["TOKEN"], config["CHATID"], msg)
                continue

            if interval < config["INTERVAL_PROBLEM"] and last_dt != 0:
                alert_time[host] = 0
                send_message(config["TOKEN"], config["CHATID"], f"{host} normalizado.")
                continue

if __name__ == "__main__":
    main()
