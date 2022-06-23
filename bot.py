"""bot implements a telegram bot that allow users to interact with the monitoring system and
that checks ig the endpoints are sending the signals """

import datetime
import os
import yaml
import psutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext

with open("/etc/monitora/bot.yml", 'r', encoding="utf8") as config_file:
    config = yaml.safe_load(config_file)

app = ApplicationBuilder().token(config["TOKEN"]).build()

alert_times = {}

# Inspired by
# https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
def check_process(process_name):
    """ Check if there is any running process that contains process_name in the command line. """
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            try:
                proc_name = proc.cmdline()[1]
            except IndexError:
                continue
            if process_name.lower() in proc_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def read_interval(host):
    """read_interval reads the last signal timestamp sent by the endpoint named host"""
    try:
        with open(config["PATH"]+host+".host", 'r', encoding="utf8") as a_reader:
            last_signal_ts = a_reader.read()
    except FileNotFoundError:
        return None
    last_signal_dt = datetime.datetime.fromtimestamp(int(last_signal_ts))
    interval = (datetime.datetime.now() - last_signal_dt).total_seconds()
    return interval

async def checker(context: CallbackContext):
    """ checker if the function that verify if the endpoints are alive"""

    global alert_times

    for host in config["HOSTS"]:
        interval = read_interval(host)
        if interval is None:
            continue

        times = alert_times.get(host,0)

        if interval < config["INTERVAL_PROBLEM"] and times != 0:
            alert_times[host] = 0
            await context.bot.send_message(config["CHATID"], f"{host} normalizado.")
            continue

        if interval >= config["INTERVAL_PROBLEM"] and times == 0:
            alert_times[host] = 1
            msg = f"{host} não manda mensagens faz mais de {int(interval/60)} minutos. "
            msg = msg + "Possível problema de rede ou na máquina !"
            await context.bot.send_message(config["CHATID"], msg)
            continue

        if interval >= config["INTERVAL_RETRY_MESSAGE"]*times and times>=1:
            alert_times[host] = times + 1
            msg = f"RETRY: {host} não manda mensagens faz mais de {int(interval/60)} minutos. "
            msg = msg + "Possível problema de rede ou na máquina !"
            await context.bot.send_message(config["CHATID"], msg)
            continue

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Restart_all : Restarts all system services """
    if update.effective_chat.id == config['CHATID']:
        await context.bot.send_message(update.effective_chat.id, "Restarting Server service...")
        os.system("/usr/bin/systemctl restart server.service")
        await context.bot.send_message(update.effective_chat.id,
            "Server service restarted.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Status: sends a message with the status of the services and endpoints"""
    if update.effective_chat.id == config['CHATID']:
        msg = "-------- PROCESSES -----------"
        if check_process("monitora/server"):
            msg = msg + "\nServer process: Running."
        else:
            msg = msg + "\nPROBLEM: Server process: Not running."

        msg = msg + "\n-------- ENDPOINTS -----------"

        for host in config["HOSTS"]:
            interval = read_interval(host)
            if interval is None:
                msg = msg + "\n" + host + " endpoint: never sent a signal."
            else:
                msg = msg + f"\n{host} endpoint: sent a message {int(interval)} seconds ago."

        await context.bot.send_message(update.effective_chat.id, msg)

def main():
    """ main is the main function"""
    app.add_handler(CommandHandler('restart', restart))
    app.add_handler(CommandHandler('status', status))
    job_queue = app.job_queue
    job_queue.run_repeating(checker, interval=10, first=10)
    app.run_polling()

if __name__ == '__main__':
    main()
