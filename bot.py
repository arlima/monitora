import telebot
import yaml
import psutil
import datetime
    
config_file = open("/etc/monitora/checker.yml", 'r')
config = yaml.safe_load(config_file)
bot = telebot.TeleBot(config["TOKEN"])

#https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            try:
                proc_name = proc.cmdline()[1]
            except IndexError:
                proc_name = 'null'
            if processName.lower() in proc_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

@bot.message_handler(commands = ['start'])
def start(message):
    msg = "Hello !"
    bot.reply_to(message, msg)

@bot.message_handler(commands = ['status'])
def status(message):
    msg = "-------- PROCESSES -----------"
    if checkIfProcessRunning("monitora/checker"):
        msg = msg + "\nChecker process: Running."
    else:
        msg = msg + "\nPROBLEM: Checker process: Not running."
    if checkIfProcessRunning("monitora/server"):
        msg = msg + "\nServer process: Running."
    else:
        msg = msg + "\nPROBLEM: Server process: Not running."
    
    msg = msg + "\n-------- ENDPOINTS -----------"

    now = datetime.datetime.now()
    for host in config["HOSTS"]:
        try:
            with open(config["PATH"]+host+".host", 'r') as a_reader:
                ts = a_reader.read()
            dt = datetime.datetime.fromtimestamp(int(ts))
            interval = (now - dt).total_seconds()
        except:
            interval = 'null'
        if interval == 'null':
            msg = msg + "\n" + host + " endpoint: never sent a signal."
        else:
            msg = msg + "\n" + host + " endpoint: sent a message {0} seconds ago.".format(int(interval))
            
    #bot.reply_to(message, msg)
    bot.send_message(message.chat.id, msg)

def main():
    bot.polling()

if __name__ == '__main__':
    main()
