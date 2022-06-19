import time
import datetime
import yaml
import telebot

def main():
    config_file = open("/etc/monitora/checker.yml", 'r')
    config = yaml.safe_load(config_file)
    bot = telebot.TeleBot(config["TOKEN"])
    alertTime = {}

    while True:
        time.sleep(10)
        now = datetime.datetime.now()
        for host in config["HOSTS"]:
            try:
                with open(config["PATH"]+host+".host", 'r') as a_reader:
                    ts = a_reader.read()
                dt = datetime.datetime.fromtimestamp(int(ts))
                interval = (now - dt).total_seconds()
            except:
                interval = 0
            
            lastDt = alertTime.get(host, 0)
            if lastDt != 0:
                intervalLastAlert = (now - lastDt).total_seconds()
            else:
                intervalLastAlert = 0

            if intervalLastAlert >= config["INTERVAL_RETRY_MESSAGE"]:
                alertTime[host] = now
                bot.send_message(config["CHATID"], "RETRY: {} não manda mensagens faz mais de {} minutos. Possível problema de rede ou na máquina !".format(host, int(interval/60)))
                continue
            
            if interval >= config["INTERVAL_PROBLEM"] and lastDt == 0:
                alertTime[host] = now
                bot.send_message(config["CHATID"], "{} não manda mensagens faz mais de {} minutos. Possível problema de rede ou na máquina !".format(host, int(interval/60)))
                continue
              
            if interval < config["INTERVAL_PROBLEM"] and lastDt != 0:
                alertTime[host] = 0
                bot.send_message(config["CHATID"], " {} normalizado.".format(host))
                continue

if __name__ == "__main__":
    main()