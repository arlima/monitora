"""bot implements a telegram bot to control our monitoring services"""

import datetime
import os
import yaml
import psutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext

with open("/etc/monitora/bot.yml", 'r', encoding="utf8") as config_file:
    config = yaml.safe_load(config_file)

app = ApplicationBuilder().token(config["TOKEN"]).build()

alert_time = {}

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

async def checker(context: CallbackContext):
    """ checker if the function that verify if the endpoints are alive"""
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
            await context.bot.send_message(config["CHATID"], msg)
            continue

        if interval >= config["INTERVAL_PROBLEM"] and last_dt == 0:
            alert_time[host] = now
            msg = f"{host} não manda mensagens faz mais de {int(interval/60)} minutos. "
            msg = msg + "Possível problema de rede ou na máquina !"
            await context.bot.send_message(config["CHATID"], msg)
            continue

        if interval < config["INTERVAL_PROBLEM"] and last_dt != 0:
            alert_time[host] = 0
            await context.bot.send_message(config["CHATID"], f"{host} normalizado.")
            continue

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Start: sends a Hello message """
    if update.effective_chat.id == config['CHATID']:
        msg = "Hello !"
        await context.bot.send_message(update.effective_chat.id, msg)

async def restart_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Restart_all : Restarts all system services """
    if update.effective_chat.id == config['CHATID']:
        await context.bot.send_message(update.effective_chat.id, "Restarting Services...")
        os.system("/usr/bin/systemctl restart server.service")
        await context.bot.send_message(update.effective_chat.id,
            "Checker and Server services restarted.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Status: sends a message with the status of the services and endpoints"""
    if update.effective_chat.id == config['CHATID']:
        msg = "-------- PROCESSES -----------"
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

        await context.bot.send_message(update.effective_chat.id, msg)

def main():
    """ main is the main function"""
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('restart_all', restart_all))
    app.add_handler(CommandHandler('status', status))
    job_queue = app.job_queue
    job_queue.run_repeating(checker, interval=10, first=10)
    app.run_polling()

if __name__ == '__main__':
    main()
