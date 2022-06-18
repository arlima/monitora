import telebot
import yaml
import psutil
    
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
    if checkIfProcessRunning("monitora/checker"):
        msg = "Checker is running."
    else:
        msg = "PROBLEM: Checker is not running."
    if checkIfProcessRunning("monitora/server"):
        msg = msg + "\nServer is running."
    else:
        msg = msg + "\nPROBLEM: Server is not running."
    bot.reply_to(message, msg)

def main():
    bot.polling()

if __name__ == '__main__':
    main()
