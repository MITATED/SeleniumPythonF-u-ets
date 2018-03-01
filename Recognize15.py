# -*- coding: utf-8 -*-
import os
import time
from rusos import *
import psutil,traceback, sys
def Recognize15(img):
    path = "c:\\Program Files (x86)\\Miner Monitor\\Watcher\\Questions\\15_img%s.png"%time.strftime("_%d.%m.%y_%H.%M.%S_")
    with open(path, 'wb') as file:
        file.write(img[22:].decode('base64'))
    Write("Ищем файл ответа")
    for i in xrange(100):
        if os.path.exists(path.replace("Questions", "Answers").replace(".png", ".txt")):
            break
        elif i == 10 and os.path.exists(path):
            for proc in psutil.process_iter():
                if proc.name() == "Watcher.exe":
                    proc.kill()
            os.startfile(r'c:/Program Files (x86)/Miner Monitor/Watcher/Watcher.exe')
        Write("Ищем...")
        time.sleep(0.5)
    else:
        Write("Файл ответа не найден!")
        return "Файл ответа не найден!"
    with open(path.replace("Questions", "Answers").replace(".png", ".txt"), 'r') as file:
        Write(file.read())
def Write(Alert):
    try:
        print ru(Alert)
    except:
        pass
def WriteFile(nameFile, line):
    with open(nameFile + ".txt", "a") as file:
        file.write((line + "\n").encode('utf8'))
Recognize15("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJYAAAAQCAIAAAB7ihFwAAAABnRSTlMAAAAAAABupgeRAAAA10lEQVRYhe2X0Q7DIAhFwe3/f5k9mDgiiizVVpd7XtpQlBtBpUQAAADAGpiZmZ9WMSblxylygeWVH8jfuTCZ/IlIMfbetedv8VrDrTEevSl+oqTKYiU9TiIlRUR8WUV6c/mGNIfH53Q850qibdITId0ZrCphvUzxy3jute1I6nlutQWJ6O1/ji9WsH57B1E1SkR0qhzPdZJOod6FS1vTqoRtoPv34lCS9qQLJ/Y6vjqaF3iR67Qe2j6s4mA705sz3vhckWTTk0+FXqB/YMPfyg0lAQAA2JMPaG7MM2pgLCAAAAAASUVORK5CYII=")
# data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJYAAAAQCAIAAAB7ihFwAAAABnRSTlMAAAAAAABupgeRAAAAlUlEQVRYhe2XQQrAIAwEk+L/v2wPioRSRBNrD85chMoq7JpoRQAAAM5G66DaPuWc/cupOlZYtfuZXGJ8L/ZZQ6fwCVftfixJFh18rP+LVIZgK2uV5AiSzhnk6bjjMrMS310o5gyR6CypPz3u7Gv9DcrdwYOUCIMOWqGjkZJfkPqcUdVOxQT9HZHzX/EJNtf9cgAAgD3cR55OJZ7VuEYAAAAASUVORK5CYII=
