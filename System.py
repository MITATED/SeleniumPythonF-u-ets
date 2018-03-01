# -*- coding: utf-8 -*-
from rusos import *
from selenium import webdriver
import traceback, sys
import time
import psutil
import shutil
import sqlite3
import os
import re
import urllib, urllib2
import random
import socket

def START(Inter):
    Kill()
    Inter.settings = OpenSettings()

    startTimeDriver = time.mktime(time.gmtime())
    Inter.driver = Driver()
    Write("Open Driver %s"%(time.mktime(time.gmtime()) - startTimeDriver))

    Inter.WinHand, Inter.ProcID = Initialisation(Inter)
    Inter.ids, Inter.sites = FousetsRead()

    Inter.site = SearchID(Inter, idINI(Inter)[0]) if idINI(Inter) != "not file" else SearchID(Inter, Inter.settings["START"])
    WriteSettings(Inter, {"lastRun": "%s"%time.mktime(time.gmtime())})

    Inter.timeLast = time.mktime(time.gmtime())
    Inter.driver.implicitly_wait(0)
    Write(str(Inter.site))

def WriteErr(ErrMessages):
    try:
        WriteFile("logErr", time.strftime("%H:%M:%S") + "          "  + ru(ErrMessages))
    except:
        Write("Ошибка при записи ошибки)")
def Write(Alert):
    try:
        print ru(Alert)
        WriteFile("log", time.strftime("%H:%M:%S") + "          "  + ru(Alert))
    except:
        for i in traceback.format_exception(*sys.exc_info()):
            WriteErr(i)
        print Alert
    x = raw_input("Next?")

def WriteFile(nameFile, line):
    with open(nameFile + ".txt", "a") as file:
        file.write((line + "\n").encode('utf8'))

def OpenSettings():
    with open("settings.ini", "r") as file:
        y = file.read().split("\n")
        dictionary = {}
        for i in y[:-1]:
            dictionary[i.split(":")[0]] = i.split(":")[1]
        return dictionary

def WriteSettings(Inter, diction):
    set = OpenSettings()
    for i in diction:
        set[i] = str(diction[i])
    text = ""
    for i in set:
        text += "%s:%s\n"%(i, set[i])
    with open("settings.ini", "w") as file:
        file.write(text)
    print 1
    Inter.settings = OpenSettings()



def Kill():
    for proc in psutil.process_iter():
        if proc.name() == "firefox.exe":
            proc.kill()

def Kills(Inter):
    for proc in psutil.process_iter():
        if (proc.ppid() != Inter.ProcID and proc.name() == "firefox.exe") or (proc.ppid() == Inter.ProcID and proc.name() != "firefox.exe") or proc.name() == "15.exe" or proc.name() == "17.exe":
            proc.kill()
        if proc.ppid() == Inter.ProcID:
            try:
                Write("Занимаемая память: %s МБ"%str(proc.memory_info_ex().rss/1024/1024))
            except:
                pass
    for i in Inter.driver.window_handles:
        if i != Inter.WinHand:
            Inter.driver.switch_to_window(i)
            Inter.driver.close()
            Write("Window close")
            Inter.driver.switch_to_window(Inter.WinHand)

def Parser(Inter):
    WriteSettings(Inter, {"ParseDate":time.strftime("%d.%m.%Y")})
    sites1 = []
    for i in DB("SELECT * FROM fussets"):
        sites1 += [hM(Inter, i[1])]
    Write("Количество сайтов в базе: %s"%len(sites1))
    GoTo(Inter, "faucetbox.com/en/list/BTC")
    while Inter.driver.execute_script("return document.readyState;") != "complete":
        Sleep(0.5)
    fousets = Inter.driver.find_elements_by_xpath("//tbody//td//a[@target='_blank']")
    Write("Фуссетов у нас: %s"%len(fousets))
    text = ""
    con = sqlite3.connect('fussets.db')
    cur = con.cursor()
    for i in fousets:
        fusset = hM(Inter, i.get_attribute("href")[i.get_attribute("href").rfind("http"):].replace("%3A", ":").replace("%2F", "/"))
        if not fusset in sites1:
            # text += "INSERT INTO fussets (fusset, cap) VALUES ('" + fusset + "', '');" + "\n"
            cur.execute("INSERT INTO fussets (fusset) VALUES ('" + fusset + "');" + "\n")
            con.commit()
    con.close()
    Inter.ids, Inter.sites = FousetsRead()
    Write(str(len(Inter.sites)))

def Driver(browse = "Firefox", proxy=False):
    if proxy:
        proxyIp = "%s:%s"%(proxy[0], proxy[1])
        proxyAdrr = "http://%s:%s@%s:%s"%(proxy["user"], urllib2.quote(proxy["password"]), proxy["ip"], proxy["port"])
        print proxyAdrr
    if browse == "Chrome":
        print webdriver.DesiredCapabilities.CHROME
        webdriver.DesiredCapabilities.CHROME["pageLoadStrategy"] = "eager"
        return webdriver.Chrome(desired_capabilities = webdriver.DesiredCapabilities.CHROME)
    elif browse == "Firefox":
        webdriver.DesiredCapabilities.FIREFOX["pageLoadStrategy"] = "eager"
        return webdriver.Firefox(capabilities = webdriver.DesiredCapabilities.FIREFOX)
    elif browse == "Phantom":
        webdriver.DesiredCapabilities.PHANTOMJS["pageLoadStrategy"] = "eager"
        return webdriver.PhantomJS(capabilities = webdriver.DesiredCapabilities.PHANTOMJS)

def Initialisation(Inter):
    for proc in psutil.process_iter():
        if proc.name() == "firefox.exe":
            return Inter.driver.current_window_handle, proc.ppid()

    
def GoTo(Inter, href, type = "http://"):
    Write(type + href)
    errC = 0
    try:
        Inter.driver.execute_script("window.stop();")
    except:
        for i in traceback.format_exception(*sys.exc_info()):
            WriteErr(i)
    try:
        Inter.driver.get(type + href)
    except:
        errC += 1
        if errC > 3:
            if not href in hM(Inter.driver.current_url):
                Write("Не могу перейти по адрессу: " + href)
        Sleep(1.5)
    x = "loading"
    i = 0
    for i in xrange(10):
        if Inter.driver.execute_script("return document.readyState;") != "loading":
            break
        Sleep(0.1)
    else:
        Write("loading")
        if Inter.isLoading == 0:
            Inter.isLoading = 1
            START(Inter)
            GoTo(Inter, href, type)
    Write(Inter.driver.execute_script("return document.readyState;"))


def Intermediate(Inter):
    GoTo(Inter, os.path.dirname(os.path.abspath(sys.argv[0])) + "/intermediate.html", type = "file:///")

def DB(query):#Выполнение запроса к базе данных
    con = sqlite3.connect('fussets.db')
    cur = con.cursor()
    cur.execute(query)
    try:
        answer = cur.fetchall()
        con.close()
        return answer
    except:
        con.commit()
        con.close()
        return

def FousetsRead():
    ids, sites = [], []
    for i in DB('SELECT id, fusset FROM fussets WHERE SKIP!="1"'):
    # for i in DB('SELECT * FROM fussets'):
        ids += [i[0]]
        sites += [i[1]]
    return ids, sites

def ToCap(id, cap, value, skip):
    con = sqlite3.connect('fussets.db')
    cur = con.cursor()
    cur.execute("UPDATE fussets SET %s='%s', SKIP='%s' WHERE id=%s;"%(cap, value, skip, id))
    # cur.execute("UPDATE fussets SET " + cap + "='" + value + "' WHERE id=" + str(id) + ";")
    con.commit()
    con.close()

def Captcha(Inter):
    cType = 0
    for i in xrange(5):
        try:
            IFrameCaptcha = Inter.driver.find_elements_by_xpath("//iframe[contains(@src,'/recaptcha/api2/anchor')]")
            if len(IFrameCaptcha) == 1:
                cType = 1
                ReCaptcha()
                return ""
        except:
            pass
        try:
            IFrameCaptcha = Inter.driver.find_elements_by_xpath("//div[@id='adcopy-outer']")
            if len(IFrameCaptcha) == 1:
                cType = 2
                SolveMedia()
                return ""
        except:
            pass
        try:
            IFrameCaptcha = Inter.driver.find_elements_by_xpath("//div[@id='FunCaptcha']")
            if len(IFrameCaptcha) == 1:
                cType = 3
                FunCaptcha()
                return ""
        except:
            pass
        Sleep(1)
    if cType == 0 and Inter.driver.execute_script("return document.readyState;") == "complete":
        Write("Not Captcha")



def Sleep(t):
    time.sleep(t)

def Forms1(Inter):
    t = time.mktime(time.gmtime())
    ToCap(Inter.ids[Inter.site], "NotCompete", 0, 1)
    while time.mktime(time.gmtime()) - t < 10:
        y = Inter.driver.execute_script("return document.readyState;")
        x = Inter.driver.find_elements_by_xpath("//form")
        if len(x) == 1:
            ToCap(Inter.ids[Inter.site], "Forms", 1)
            break
        elif len(x) >= 1:
            ToCap(Inter.ids[Inter.site], "Forms", len(x))
            break
        elif len(x) == 0:
            if y == "complete":
                ToCap(Inter.ids[Inter.site], "Forms", 0)
                break
        Sleep(1)
    else:
        ToCap(Inter.ids[Inter.site], "NotCompete", 1)

def Forms(Inter):
    t = time.mktime(time.gmtime())
    while time.mktime(time.gmtime()) - t < 10:
        r = Inter.driver.find_elements_by_xpath("//form//iframe[contains(@src,'/recaptcha/api2/anchor')]")
        s = Inter.driver.find_elements_by_xpath("//form//div[@id='adcopy-outer']")
        f = Inter.driver.find_elements_by_xpath("//form//div[@id='FunCaptcha']")
        if len(r) + len(s) + len(f) == 1:
            captchaDict = {"100":("ReCaptcha", ReCaptcha, "iframe[src *= \"/recaptcha/api2/anchor\"]"),
                "010":("SolveMedia", SolveMedia, ""),
                "001":("FunCaptcha", FunCaptcha, "")}
            Write("Капча найдена!")
            i = 1
            try:
                Inter.driver.execute_script("$('form:has(%s)').css('z-index', '154225812')"%captchaDict["%s%s%s"%(len(r), len(s), len(f))][2])
            except:
                ToCap(Inter.ids[Inter.site], "Forms", -1, 1)
            ToCap(Inter.ids[Inter.site], "Forms", 1, 0)
            returnCaptcha = captchaDict["%s%s%s"%(len(r), len(s), len(f))][1](Inter)
            Inter.driver.switch_to_default_content()
            return returnCaptcha
        elif len(r) + len(s) + len(f) > 1:
            ToCap(Inter.ids[Inter.site], "Captcha", len(r) + len(s) + len(f), 1)
            Write("Капча не одна!")
            return "continue"
    x = Inter.driver.find_elements_by_xpath("//form")
    if len(x) == 0:
        ToCap(Inter.ids[Inter.site], "Forms", 0, 1)
        Write("Формы нет!")
        return "continue"
    else:
        ToCap(Inter.ids[Inter.site], "Captcha", 0, 1)
        Write("Капчи нет!")
        return "continue"

def SolveMedia(Inter):
    ToCap(Inter.ids[Inter.site], "Captcha", "SolveMedia", 1)
    Write("SolveMedia")
    return "continue"
def FunCaptcha(Inter):
    ToCap(Inter.ids[Inter.site], "Captcha", "FunCaptcha", 1)
    Write("FunCaptcha")
    return "continue"

def SearchID(Inter, id):
    if id in Inter.ids:
        return Inter.ids.index(id)
    elif id == "-1":
        return -1
    else:
        n = 1
        for i in xrange(len(Inter.ids)):
            Inter.ids[i] = int(Inter.ids[i])
        while n < len(Inter.ids):
            for i in range(len(Inter.ids)-n):
                if Inter.ids[i] > Inter.ids[i+1]:
                    Inter.ids[i],Inter.ids[i+1] = Inter.ids[i+1],Inter.ids[i]
            n += 1
        for i in Inter.ids:
            if int(i) >= int(id):
                return Inter.ids.index(i)
        return -1

def hM(Inter, str):
    return re.match("^(https?://)?(www.)?(.*?)/?$", str.lower()).groups()[2]

def idINI(Inter, action = "read", id = 1):
    if action == "read":
        try:
            with open("id.ini", "r") as file:
                return file.read().split("/")
        except:
            return "not file"
    elif action == "write":
        with open("id.ini", "w") as file:
            file.write("%s/%s"%(id, time.mktime(time.gmtime())))


def Click(Inter):
    Inter.driver.switch_to_default_content()
    Inter.driver.execute_script("document.title = \"бла-бла-бла-бла-бла-бла-бла\";")
    title = Inter.driver.title
    purses = Inter.driver.find_elements_by_xpath("//form[contains(@style, 'z-index: 154225812;')]//input[@type='text'][not(contains(@style, 'display: none;'))][@value]")
    if len(purses) == 0:
        Write("Кошелька нету")
        ToCap(Inter.ids[Inter.site], "Click", '0', 1)
        return
    elif len(purses) != 1:
        Write("Кошелек не один")
        ToCap(Inter.ids[Inter.site], "Click", '0', 1)
        return
    Write("Вводим кошелек(%s)"%len(purses))
    purses[0].clear()
    purses[0].send_keys(Inter.settings["MONEY"])
    it = 0
    for i in xrange(4):
        if not Inter.driver.execute_script("return document.readyState;") == "loading":
            break
        it = 1
        Sleep(0.5)
    else:
        Write("Loading после ввода кошелька")
    Kills(Inter)
    purses[0].clear()
    purses[0].send_keys(Inter.settings["MONEY"])
    purses[0].submit()
    ToCap(Inter.ids[Inter.site], "Click", '1', 0)

def ReCaptcha(Inter):
    try:
        ToCap(Inter.ids[Inter.site], "Captcha", 'ReCaptcha', 0)
        counter = 0
        statAudio = 0
        statTable = 0
        statAudioFalse = 0
        statTableFalse = 0
        x = 0
        ok = 0
        try:
            Inter.driver.implicitly_wait(15)
            IFrameRes = Inter.driver.find_elements_by_xpath("//iframe[contains(@src,'/recaptcha/api2/anchor')]")
            if len(IFrameRes) == 0:
                Write("Find frame error(1)")
                return "continue"
            Inter.driver.switch_to_frame(IFrameRes[0])
            Write("Нашли капчу")
            checkboxs = Inter.driver.find_elements_by_id("recaptcha-anchor-label")
            if len(checkboxs) == 0:
                Write("checkbox error")
                return "continue"
            Inter.driver.execute_script("arguments[0].click(); ", checkboxs[0])

            Write("click headphones")
            Inter.driver.switch_to_default_content()
            # Inter.driver.execute_script("window.stop();")
            # Inter.driver.execute_script("window.document.execCommand('Stop');")
            # Inter.driver.execute_script("document.close();")
            IFrameRe = Inter.driver.find_element_by_xpath("//iframe[contains(@src,'recaptcha/api2/frame')]")
            try:
                Inter.driver.switch_to_frame(IFrameRe)
            except:
                try:
                    Sleep(1)
                    Inter.driver.switch_to_frame(IFrameRe)
                except:
                    Write("Ошибка при переходе на фрейм")
                    return "continue"
            try:
                Inter.driver.switch_to_frame(IFrameRe)
                nauch = Inter.driver.find_element_by_id("recaptcha-audio-button")
                nauch.click()
            except:
                pass
            try:
                Inter.driver.switch_to_default_content()
                IFrameRe = Inter.driver.find_element_by_xpath("//iframe[contains(@src,'recaptcha/api2/frame')]")
                Inter.driver.switch_to_frame(IFrameRe)
                nauch = Inter.driver.find_element_by_id("recaptcha-audio-button")
                nauch.click()
            except:
                pass
            Inter.driver.implicitly_wait(0)
        except:
            for i in traceback.format_exception(*sys.exc_info()):
                WriteErr(i)
            return "continue"
        Inter.driver.implicitly_wait(3)
        startTimeRe = time.time()
        altQuest = ""
        for KolvoK in xrange(30):
            crType = 0
            Write("Search table or audio")
            Inter.driver.switch_to_default_content()

            Sleep(2)

            IFrameRe = Inter.driver.find_element_by_xpath("//iframe[contains(@src,'recaptcha/api2/frame')]")
            Inter.driver.switch_to_frame(IFrameRe)

            Inter.driver.implicitly_wait(1)
            if counter == 1:
                stat = (statAudio, statTable, statAudioFalse, statTableFalse)
                x = 1

            try:
                IframeTA = Inter.driver.find_elements_by_xpath("//table[@class='rc-text-choices']")
                if len(IframeTA) != 0:
                    crType = 1
                    counter = 1
            except:
                pass
            try:
                IframeTA = Inter.driver.find_elements_by_xpath("//input[@id='audio-response']")
                if len(IframeTA) != 0:
                    crType = 2
                    counter = 1
            except:
                pass
            try:
                Inter.driver.switch_to_default_content()
                IframeCaptcha = Inter.driver.find_element_by_xpath("//iframe[contains(@src,'/recaptcha/api2/anchor')]")
                Inter.driver.switch_to_frame(IframeCaptcha)
                IframeTA = Inter.driver.find_elements_by_xpath("//span[@aria-checked='true']")
                if len(IframeTA) != 0:
                    crType = 3
                    counter = 1
                    ok = 1
            except:
                pass
            Inter.driver.switch_to_default_content()
            Inter.driver.switch_to_frame(IFrameRe)

            if x == 1:
                path1 = r'C:/Program Files (x86)/Miner Monitor/Watcher/Answers/%s_%s_%s_%s_%s_%s'%(ok, stat[0], stat[1], stat[2], stat[3], filename)
                shutil.move(path.replace("Questions", "Answers"), path1)
                x = 0
            if statTable + statAudio > 20:
                break
            Inter.driver.switch_to_default_content()
            IFrameRe = Inter.driver.find_element_by_xpath("//iframe[contains(@src,'recaptcha/api2/frame')]")
            Inter.driver.switch_to_frame(IFrameRe)

            # Ищем тип капчи
            if crType == 1:
                statTable += 1
                Write("Таблица")
                # Делаем имя для файла с вопросом (тот который будет в папке ../Watcher/Questions)=================
                Inter.driver.implicitly_wait(0)
                question = Inter.driver.find_element_by_xpath("//div[@class='rc-text-desc-wrapper']//span").text
                if question == altQuest:
                    try:
                        upload = Inter.driver.find_element_by_id("recaptcha-reload-button");
                        upload.click()
                        counter = 0
                        continue
                    except:
                        for i in traceback.format_exception(*sys.exc_info()):
                            WriteErr(i)                    
                altQuest = "%s"%question
                filename = "17_" + str(KolvoK) + time.strftime("_%d.%m.%y_%H.%M.%S_") + question + ".txt"
                path = r"C:/Program Files (x86)/Miner Monitor/Watcher/Questions/" + filename
                Write(path)
                text = "%s\n"%question
                tableVariant = Inter.driver.find_elements_by_xpath("//tr[@role='presentation']//td")
                for tableitem in tableVariant:
                    try:
                        text += tableitem.text + "\n"
                    except:
                        Write("Ошибка при чтении таблици")
                # Создаем файл с вопросом

                with open(path, "a") as file:
                    file.write(text)

                Write("Ищем файл ответа")
                for i in xrange(100):
                    if os.path.exists(path.replace("Questions", "Answers")):
                        break
                    elif i == 10 and os.path.exists(path):
                        for proc in psutil.process_iter():
                            if proc.name() == "Watcher.exe":
                                proc.kill()
                        os.startfile(r'c:/Program Files (x86)/Miner Monitor/Watcher/Watcher.exe')
                    Write("Ищем...")
                    Sleep(0.5)
                else:
                    Write("Файл ответа не найден!")
                    return "continue"
                # ===========Открываем файл==========
                Write("Открываем файл")
                with open(path.replace("Questions", "Answers"), 'r') as file:
                    answerText = file.readlines()
                if answerText[0][0] == "0":
                    statTableFalse += 1
                    Write("Капча не расспознана")
                    try:
                        upload = Inter.driver.find_element_by_id("recaptcha-reload-button");
                        upload.click()
                        counter = 0
                        continue
                    except:
                        for i in traceback.format_exception(*sys.exc_info()):
                            WriteErr(i)
                s = "\n".join(answerText[2:5])
                for tableitem in tableVariant:
                    if tableitem.text in s:
                        try:
                            tableitem.click()
                            if tableitem.get_attribute("aria-checked") == "false":
                                tableitem.click()
                        except:
                            for i in traceback.format_exception(*sys.exc_info()):
                                WriteErr(i)
                            Write("Ошибка при клике на ответ")
                stopTimeRe = time.time()
                randNum = int(startTimeRe + int(Inter.settings["sleepTime"]) - stopTimeRe) + random.randrange(0, 100)/10
                Write("Подтверждаем(%s)"%randNum)
                if randNum > stopTimeRe:
                    Sleep(randNum)
                startTimeRe = time.time()
                podt = Inter.driver.find_element_by_id("recaptcha-verify-button")
                podt.click()
            elif crType == 2:
                Write("Audio")
                statAudio += 1
                try:
                    downloadMp3 = Inter.driver.find_element_by_xpath("//a[@class='rc-audiochallenge-download-link']")
                except:
                    Write("Аудио капча не найдена!")
                    for i in traceback.format_exception(*sys.exc_info()):
                        WriteErr(i)
                    statAudioFalse += 1
                    Inter.driver.find_element_by_id("recaptcha-reload-button").click()
                    counter = 0
                    continue
                Write("Start download")
                filename = "3_" + str(KolvoK) + time.strftime("_%d.%m.%y_%H.%M.%S_") + ".mp3"
                path = r"C:/Program Files (x86)/Miner Monitor/Watcher/Questions/" + filename
                try:
                    urllib.urlretrieve(str(downloadMp3.get_attribute("href")), path.replace("Questions", r'Recognizers/3/'))
                except:
                    Write("Ошибка при скачивании аудио-файла")
                    for i in traceback.format_exception(*sys.exc_info()):
                        WriteErr(i)
                sizeAudio = float(os.path.getsize(path.replace("Questions", r'Recognizers/3/')))
                if sizeAudio == 58880 or sizeAudio == 470062:
                    Write("Ругань")
                    # Inter.driver.find_element_by_id("recaptcha-reload-button").click()
                    ToCap(Inter.ids[Inter.site], "Fuck", 1, 1)
                    return "continue"
                elif sizeAudio > 10000:
                    Write("move in folder")
                    shutil.move(path.replace("Questions", r'Recognizers/3/'), path)
                elif sizeAudio < 10000:
                    Write("Файл не докачался")
                    statAudioFalse += 1
                    Inter.driver.find_element_by_id("recaptcha-reload-button").click()
                    counter = 0
                    continue

                Write("Ищем файл ответа")
                exitNot = 0
                for i in xrange(100):
                    if os.path.exists(path.replace("Questions", "Answers").replace(".mp3", ".txt")):
                        break
                    elif os.path.exists(path.replace("Questions", "Answers").replace(".mp3", "_NotRecognized.txt")):
                        Write("Капча не распознана(Watcher)")
                        statAudioFalse += 1
                        exitNot = 1
                        break
                    elif i == 10 and os.path.exists(path):
                        for proc in psutil.process_iter():
                            if proc.name() == "Watcher.exe":
                                proc.kill()
                        os.startfile(r'c:/Program Files (x86)/Miner Monitor/Watcher/Watcher.exe')
                    Write("Ищем...")
                    Sleep(0.5)
                else:
                    Write("Файл ответа не найден!")
                    statAudioFalse += 1
                    exitNot = 1
                if exitNot:
                    Inter.driver.find_element_by_id("recaptcha-reload-button").click()
                    counter = 0
                    continue

                # ===========Открываем файл==========
                Write('Открываем файл ответа')
                with open(path.replace("Questions", "Answers").replace(".mp3", ".txt"), 'r') as file:
                    answerText = file.readlines()
                if answerText[0][0] == "0":
                    Write("Капча не распознана")
                    statAudioFalse += 1
                    Inter.driver.find_element_by_id("recaptcha-reload-button").click()
                    counter = 0
                    continue
                SendAnsw = Inter.driver.find_element_by_id("audio-response")
                SendAnsw.send_keys("1")
                SendAnsw.clear()
                SendAnsw.send_keys(answerText[1].strip())
                stopTimeRe = time.time()
                randNum = int(startTimeRe + int(Inter.settings["sleepTime"]) - stopTimeRe) + random.randrange(0, 100)/10
                Write("Подтверждаем(%s)"%randNum)
                if randNum > stopTimeRe:
                    Sleep(randNum)
                startTimeRe = time.time()
                podt = Inter.driver.find_element_by_id("recaptcha-verify-button")
                podt.click()
            elif crType == 3:
                Write("Птичка")
                return "bird"
            else:
                Write("Херня")
                return "continue"
    except:
        for i in traceback.format_exception(*sys.exc_info()):
            WriteErr(i)
        return "continue"


def Recognize15(img, length):
    answ = DB('SELECT txt FROM bases WHERE base="%s"'%img)
    if len(answ) == 1:
        return answ[0][0]
    path = "c:\\Program Files (x86)\\Miner Monitor\\Watcher\\Questions\\15_%s_%s_%s.png"%(length, socket.gethostbyname(socket.getfqdn()).replace('.', '_'), time.strftime("%H_%M_%S_%d_%m_%y"))
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
        retAnsw = file.readlines()[1] if file.readlines()[0].strip() != "0" else False
    return retAnsw



def Antibot(Inter):
    antibotlist = {}
    saveToBase = {}
    try:
        ToAntibot = Inter.driver.find_elements_by_xpath("//p[@class = 'alert alert-info']/img")
        if len(ToAntibot) == 0:
            Write("Антиботиков нету)")
            return "continue"
        ToAntibots = Inter.driver.find_elements_by_xpath("//a[@class = 'antibotlinks']")
        if len(ToAntibots) == 0:
            ToAntibots = Inter.driver.find_elements_by_xpath("//div[@class='antibotlinks']/*/img")
            for antibot in ToAntibots:
                Write(antibot.get_attribute("src"))
                r15 = Recognize15(antibot.get_attribute("src"), 1)
                saveToBase[r15] = antibot.get_attribute("src")
                antibotlist[r15] = antibot
        else:
            for antibot in ToAntibots:
                Write(antibot.text)
                antibotlist[antibot.text[antibot.text.find("(") + 1:antibot.text.find(")")].strip() if antibot.text.find("(") != 0 and antibot.text.find(")") != 0 else antibot.text.strip()] = antibot
        if len(antibotlist) == 0:
            return "continue"
        img = Recognize15(ToAntibot[0].get_attribute("src"), len(antibotlist))
        for i in antibotlist:
            Write(i)
        AddTableVar = AddTable([i.strip() for i in img.split(",")], antibotlist.keys())
        if AddTableVar == "continue":
            return "continue"
        for i in saveToBase:
            DB("INSERT INTO bases (base, txt) VALUES ('%s', '%s');\n"%(i, saveToBase[i]))
        for i in AddTableVar:
            Write(i)
            try:
                antibotlist[i].click()
            except:
                Inter.driver.execute_script("arguments[0].click(); ", antibotlist[i])
    except:
        for i in traceback.format_exception(*sys.exc_info()):
            WriteErr(i)
        return "continue"

def CorTableRead():
    value = []
    dic = []
    with open("CorTableNew.txt") as file:
        x = file.read().lower()
        y = x.split("\n")
        for i in y:
            dic += [i.split('|')[:-1]]
            # dic[i.split(":")[0]] = i.split(":")[1].split("|")[:-1]
    return dic
def lower(str1):
    return str1.replace(":", "S1S").replace("|", "S2S").replace("\n", "S3S").lower()

def CorTableWrite(str1, str2, dic = CorTableRead()):
    str1 = lower(str1)
    str2 = lower(str2)
    if CorTable(str1, str2) == 1:
        print u"Значение существует!"
        return
    for i in xrange(len(dic)):
        if str1 in dic[i]:
            dic[i] += [str2]
            break
    else:
        dic += [[str1, str2]]
    text = ""
    for i in dic:
        for ii in i:
            text += "%s|"%ii
        text += "\n"
    with open("CorTableNew.txt", "w") as file:
        file.write(text[:-1])

def CorTableNot(strM1, strM2):
    text = ""
    for i in strM1:
        text += "%s|"%lower(i)
    text += ":::"
    for i in strM2:
        text += "%s|"%lower(i)
    text += "\n"
    with open("NotCorTable.txt", "a") as file:
        file.write(text)
    return "continue"

def isSimilar(str1, str2):
    str1, str2, isEnd = str1.replace("..", u"Ψ"), str2.replace("..", u"Ψ"), 0
    if str1[-3:] == "$$$":
        str1 = str1[:-3]
        isEnd = 1
    if str2[-3:] == "$$$":
        str2 = str2[:-3]
        isEnd = 1
    if len(str1) != len(str2) and not isEnd:
        return 0
    l = len(str1) if len(str1) < len(str2) else len(str2)
    for i in xrange(l):
        if str1[i] != str2[i] and str1[i] != u"Ψ" and str2[i] != u"Ψ":
            return 0
    return 1


def CorTable(str1, str2):
    str1 = lower(str1)
    str2 = lower(str2)
    dic = CorTableRead()
    for i in dic:
        if str1 in i:
            if str2 in i:
                return 1
    else:
        for i in dic:
            for ii in xrange(len(i)):
                if isSimilar(str1, i[ii]):
                    for iii in xrange(len(i)):
                        if isSimilar(str2, i[iii]):
                            return 1
        return 0
  
def AddTable(m1, m2):
    if len(m1) != len(m2):
        return 0
    dic = []
    empty = 0
    CorTableNo = 0
    for i in m1:
        list = []
        for ii in m2:
            if CorTable(i, ii) == 1:
                list += [ii]
        if len(list) == 1:
            dic += [list[0]]
        else:
            CorTableNo = 1
    if len(m1) - len(dic) == 1:
        if "$$$" in m1:
            empty, CorTableNo = [], 0
            for i in m2:
                if not i in dic:
                    empty += [i]
            if len(empty) == 1:
                dic.insert(m1.index("$$$"), empty[0])
    if CorTableNo:
        CorTableNot(m1, m2)
    if len(dic) != len(m1):
        return "continue"
    return dic
