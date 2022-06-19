"""bot implements a telegram bot to control our monitoring services"""

import datetime
import os
import telebot
import yaml
import psutil

config_file = open("/etc/monitora/checker.yml", 'r', encoding="utf8")
config = yaml.safe_load(config_file)
bot = telebot.TeleBot(config["TOKEN"])

# Inspired by
# https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
def check_process(process_name):
    """ Check if there is any running process that contains the given name command line. """
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            try:
                proc_name = proc.cmdline()[1]
            except IndexError:
                proc_name = 'null'
            if process_name.lower() in proc_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

@bot.message_handler(commands = ['start'])
def start(message):
    """ Start: sends a Hello message """
    if message.chat.id == config['CHATID']:
        msg = "Hello !"
        bot.reply_to(message, msg)

@bot.message_handler(commands = ['restart_all'])
def restart_all(message):
    """ Restart_all : Restarts all system services """
    if message.chat.id == config['CHATID']:
        bot.send_message(message.chat.id, "Restarting Services...")
        os.popen("/usr/bin/supervisorctl restart checker")
        os.popen("/usr/bin/supervisorctl restart server")
        bot.send_message(message.chat.id, "Checker and Server services restarted.")

@bot.message_handler(commands = ['status'])
def status(message):
    """ Status: sends a message with the status of the services and endpoints"""
    if message.chat.id == config['CHATID']:
        msg = "-------- PROCESSES -----------"
        if check_process("monitora/checker"):
            msg = msg + "\nChecker process: Running."
        else:
            msg = msg + "\nPROBLEM: Checker process: Not running."
        if check_process("monitora/server"):
            msg = msg + "\nServer process: Running."
        else:
            msg = msg + "\nPROBLEM: Server process: Not running."

        msg = msg + "\n-------- ENDPOINTS -----------"

        now = datetime.datetime.now()
        for host in config["HOSTS"]:
            try:
                with open(config["PATH"]+host+".host", 'r', encoding="utf8") as a_reader:
                    last_signal_ts = a_reader.read()
                last_signal_dt = datetime.datetime.fromtimestamp(int(last_signal_ts))
                interval = (now - last_signal_dt).total_seconds()
            except FileNotFoundError:
                interval = 'null'
            if interval == 'null':
                msg = msg + "\n" + host + " endpoint: never sent a signal."
            else:
                msg = msg + f"\n {host} endpoint: sent a message {int(interval)} seconds ago."

        #bot.reply_to(message, msg)
        bot.send_message(message.chat.id, msg)

def main():
    """ main is the main function"""
    bot.polling()

if __name__ == '__main__':
    main()
