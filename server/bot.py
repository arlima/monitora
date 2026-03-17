"""bot implements a telegram bot that allows users to interact with the monitoring system and
that checks if the endpoints are sending the signals """

import datetime
import glob
import os
import subprocess
import yaml
import psutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext

with open("/etc/monitora/monitora.yml", 'r', encoding="utf8") as config_file:
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

def get_hosts():
    """ get_hosts returns the list of hosts discovered from .host files in the data directory """
    files = glob.glob(config["PATH"] + "*.host")
    return [os.path.splitext(os.path.basename(f))[0] for f in files]

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

    for host in get_hosts():
        interval = read_interval(host)
        if interval is None:
            continue

        times = alert_times.get(host,0)

        if interval < config["INTERVAL_PROBLEM"] and times != 0:
            alert_times[host] = 0
            await context.bot.send_message(config["CHATID"], f"{host} is back to normal.")
            continue

        if interval >= config["INTERVAL_PROBLEM"] and times == 0:
            alert_times[host] = 1
            msg = f"{host} has not sent a signal for more than {int(interval/60)} minutes. "
            msg = msg + "Possible network or machine issue!"
            await context.bot.send_message(config["CHATID"], msg)
            continue

        if interval >= config["INTERVAL_RETRY_MESSAGE"]*times and times>=1:
            alert_times[host] = times + 1
            msg = f"RETRY: {host} has not sent a signal for more than {int(interval/60)} minutes. "
            msg = msg + "Possible network or machine issue!"
            await context.bot.send_message(config["CHATID"], msg)
            continue

async def remove_host(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ remove_host removes a host by deleting its .host file """
    if update.effective_chat.id == config['CHATID']:
        if not context.args:
            await context.bot.send_message(update.effective_chat.id, "Usage: /remove_host <hostname>")
            return
        hostname = context.args[0]
        host_file = config["PATH"] + hostname + ".host"
        if not os.path.exists(host_file):
            await context.bot.send_message(update.effective_chat.id, f"Host '{hostname}' not found.")
            return
        os.remove(host_file)
        alert_times.pop(hostname, None)
        await context.bot.send_message(update.effective_chat.id, f"Host '{hostname}' removed.")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Restart_all : Restarts all system services """
    if update.effective_chat.id == config['CHATID']:
        await context.bot.send_message(update.effective_chat.id, "Restarting Server service...")
        for proc in psutil.process_iter():
            try:
                if 'server.py' in ' '.join(proc.cmdline()):
                    proc.kill()
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        subprocess.Popen(['python3', '/app/server.py'])
        await context.bot.send_message(update.effective_chat.id, "Server service restarted.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Status: sends a message with the status of the services and endpoints"""
    if update.effective_chat.id == config['CHATID']:
        msg = "-------- PROCESSES -----------"
        if check_process("server.py"):
            msg = msg + "\nServer process: Running."
        else:
            msg = msg + "\nPROBLEM: Server process: Not running."

        msg = msg + "\n-------- ENDPOINTS -----------"

        for host in get_hosts():
            interval = read_interval(host)
            if interval is None:
                msg = msg + "\n" + host + " endpoint: never sent a signal."
            else:
                msg = msg + f"\n{host} endpoint: sent a message {int(interval)} seconds ago."

        await context.bot.send_message(update.effective_chat.id, msg)

def main():
    """ main is the main function"""
    app.add_handler(CommandHandler('remove_host', remove_host))
    app.add_handler(CommandHandler('restart', restart))
    app.add_handler(CommandHandler('status', status))
    job_queue = app.job_queue
    job_queue.run_repeating(checker, interval=config["INTERVAL_CHECKER"], first=config["INTERVAL_CHECKER"])
    app.run_polling()

if __name__ == '__main__':
    main()
