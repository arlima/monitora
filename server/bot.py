"""bot implements a telegram bot that allows users to interact with the monitoring system and
that checks if the endpoints are sending the signals """

import datetime
import os
import sqlite3
import subprocess
import yaml
import psutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext

with open("/etc/monitora/monitora.yml", 'r', encoding="utf8") as config_file:
    config = yaml.safe_load(config_file)

DB_PATH = config["PATH"] + "monitora.db"

app = ApplicationBuilder().token(config["TOKEN"]).build()

alert_times = {}

def init_db():
    """ init_db creates the hosts table if it does not exist """
    with sqlite3.connect(DB_PATH) as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("""
            CREATE TABLE IF NOT EXISTS hosts (
                name TEXT PRIMARY KEY,
                last_signal INTEGER NOT NULL
            )
        """)

# Inspired by
# https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
def check_process(process_name):
    """ Check if there is any running process that contains process_name in the command line. """
    for proc in psutil.process_iter():
        try:
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
    """ get_hosts returns the list of hosts from the database """
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute("SELECT name FROM hosts").fetchall()
    return [row[0] for row in rows]

def read_interval(host):
    """ read_interval returns the seconds since the last signal from host """
    with sqlite3.connect(DB_PATH) as con:
        row = con.execute("SELECT last_signal FROM hosts WHERE name = ?", (host,)).fetchone()
    if row is None:
        return None
    last_signal_dt = datetime.datetime.fromtimestamp(row[0])
    return (datetime.datetime.now() - last_signal_dt).total_seconds()

async def checker(context: CallbackContext):
    """ checker is the function that verifies if the endpoints are alive """
    global alert_times

    for host in get_hosts():
        interval = read_interval(host)
        if interval is None:
            continue

        times = alert_times.get(host, 0)

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

        if interval >= config["INTERVAL_RETRY_MESSAGE"] * times and times >= 1:
            alert_times[host] = times + 1
            msg = f"RETRY: {host} has not sent a signal for more than {int(interval/60)} minutes. "
            msg = msg + "Possible network or machine issue!"
            await context.bot.send_message(config["CHATID"], msg)
            continue

async def remove_host(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ remove_host removes a host from the database """
    if update.effective_chat.id == config['CHATID']:
        if not context.args:
            await context.bot.send_message(update.effective_chat.id, "Usage: /remove_host <hostname>")
            return
        hostname = context.args[0]
        with sqlite3.connect(DB_PATH) as con:
            deleted = con.execute("DELETE FROM hosts WHERE name = ?", (hostname,)).rowcount
        if deleted == 0:
            await context.bot.send_message(update.effective_chat.id, f"Host '{hostname}' not found.")
            return
        alert_times.pop(hostname, None)
        await context.bot.send_message(update.effective_chat.id, f"Host '{hostname}' removed.")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ restart restarts the server service """
    if update.effective_chat.id == config['CHATID']:
        await context.bot.send_message(update.effective_chat.id, "Restarting Server service...")
        for proc in psutil.process_iter():
            try:
                if 'gunicorn' in ' '.join(proc.cmdline()):
                    proc.kill()
                    proc.wait(timeout=5)
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
        subprocess.Popen([
            "gunicorn",
            "--bind", f"0.0.0.0:{config['PORT']}",
            "--workers", "2",
            "server:app"
        ])
        await context.bot.send_message(update.effective_chat.id, "Server service restarted.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ status sends a message with the status of the services and endpoints """
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
    init_db()
    app.add_handler(CommandHandler('remove_host', remove_host))
    app.add_handler(CommandHandler('restart', restart))
    app.add_handler(CommandHandler('status', status))
    job_queue = app.job_queue
    job_queue.run_repeating(checker, interval=config["INTERVAL_CHECKER"], first=config["INTERVAL_CHECKER"])
    app.run_polling()

if __name__ == '__main__':
    main()
