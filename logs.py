from datetime import datetime
class logs():
    def log(importance, text):
        f = open("logs.txt", "a")
        if importance == 1 :
            f.write(datetime.now().isoformat(timespec='seconds') + "[ GAME ] : " + str(text) + "\n")
            print(datetime.now().isoformat(timespec='seconds') + "[ GAME ] : " + str(text))
        elif importance == 2 :
            f.write(datetime.now().isoformat(timespec='seconds') + "[ WARN ] : " + str(text) + "\n")
            print(datetime.now().isoformat(timespec='seconds') + "[ WARN ] : " + str(text))
        elif importance == 3 :
            f.write(datetime.now().isoformat(timespec='seconds') + "[ ERROR ] : " + str(text) + "\n")
            print(datetime.now().isoformat(timespec='seconds') + "[ ERROR ] : " + str(text))
        elif importance == 4 :
            f.write(datetime.now().isoformat(timespec='seconds') + "[ FATAL ] : " + str(text) + "\n")
            print(datetime.now().isoformat(timespec='seconds') + "[ FATAL ] : " + str(text))
        else :
            print("In Main.py, line 3 :\n   In class logs():\n      In def log(importance, text) importance isnt here.")
        f.close()

