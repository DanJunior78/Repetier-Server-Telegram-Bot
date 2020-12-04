######################################################################################################################
# Repetier-Server_Telegram_Bot
# Copyright (c) 2020 Repetier-Server_Telegram_Bot [https://github.com/DanJunior78/Repetier-Server-Telegram-Bot]
# Owner: Daniel Glock, Germany Twitter: @Daniel_Glock
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
######################################################################################################################

import __main__ as main
import gettext
presLan = gettext
_ = presLan.gettext
import logging
import sys
import os
import platform
import locale
import datetime
import time
from datetime import timedelta
import arrow # Date ISO 8601
import threading, time, signal # threading libraries
import pathlib
import copy
from urllib.parse import urlparse
import getpass
import json
from websocket import create_connection
import requests
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
import tkinter.ttk as ttk
from ttkthemes import ThemedTk
import telegram

SW_VERSION = "1.0.000" 
CFG_VERSION = "V1.00"
EX_DEBUG = False

LANGUAGE = "de"

# Repetier-Server
RepetierServerIP = ""
RepetierServerPort = ""
MY_REPETIER_SERVER_API_KEY = ""
MessCnt = 0

# Bot Parameters
MY_TELEGRAM_TOKEN = ""
CHATID = ""

# Check platform
checkPlatform = platform.platform()

# Create Logfile in sub folder of program
formatter='(%(threadName)-10s) - %(asctime)s - %(name)s - %(levelname)s - %(message)s '

locale.setlocale(locale.LC_ALL, '')
now = datetime.datetime.now()
Uhrzeit = "{:%y%m%d_%H%M%S}"
PROGRAM_FILE = main.__file__
LOGFILEFOLDER = os.path.join(os.getcwd(), 'log')
pathlib.Path(LOGFILEFOLDER).mkdir(parents=False, exist_ok=True)
BASENAME = os.path.basename(PROGRAM_FILE)
FILENAME_NO_EXTENSION = os.path.splitext(BASENAME)[0]
PROGRAM_FILE_NO_EXT = os.path.splitext(PROGRAM_FILE)[0]
FILENAME_FILE_NO_EXT_WS = FILENAME_NO_EXTENSION + "Websocket"
LOGFILENAME = os.path.join(LOGFILEFOLDER, Uhrzeit.format(now) + "_" + FILENAME_NO_EXTENSION + '.log')
LOGFILENAMEWS = os.path.join(LOGFILEFOLDER, Uhrzeit.format(now) + "_" + FILENAME_FILE_NO_EXT_WS + '.log')

# Configuration and external Data

## Configuration file
FILENAME_FILE_NO_EXT_CFG = 'RepetierBot'
CFGFILENAME =  os.path.join(os.getcwd(), FILENAME_FILE_NO_EXT_CFG + '.json')

### Functions

# Language Management

def changeLang(langSel = None):
    global presLan
    _ = presLan.gettext
    langPath = os.path.join(os.getcwd(), 'locale')
    logger.info(_("Language file folder: %s") % langPath)
    if langSel == None:
        if sys.platform.startswith('win'):
            if os.getenv('LANG') is None:
                lang, enc = locale.getdefaultlocale()
                logger.info(_("Language OS: %s/%s") % locale.getdefaultlocale())
                os.environ['LANG'] = lang
                langSel = lang
    else:
        os.environ['LANG'] = '%s' % langSel
    if gettext.find('RepetierBotSetup', langPath) == None:
        os.environ['LANG'] = 'en'
        logger.info(_("Changed to alternative language english"))
    else:
        logger.info(_("Changed language to \"%s\"") % langSel)
    presLan = gettext.translation('RepetierBotSetup', './locale')
    logger.debug(_("Language file information: %s") % presLan._info)
    presLan.install()
    _ = presLan.gettext
    
# Logger setup

def setup_logger(name, formatter, level, log_file):
    """To setup as many loggers as you want"""
    if EX_DEBUG == True:
        logging.basicConfig(format=formatter,level=level)
    else:
        logging.basicConfig(filename=LOGFILENAME, filemode='w',format=formatter,
                     level=level)
    
    logger = logging.getLogger(name)
    logger.info(_("Logger: %s was activated in debug mode (%s). Level: %s") % (name, EX_DEBUG, level))
    
    return logger

# Read and check configuration file

def impConfig():
    global LANGUAGE,MY_REPETIER_SERVER_API_KEY,RepetierServerIP
    global RepetierServerPort,MY_TELEGRAM_TOKEN,CHATID
    global presLan
    try:
        with open(CFGFILENAME) as json_file:
            data = json.load(json_file)
    except:
        logger.error(_("Configuration file not found - impConfig - : %s") % CFGFILENAME)
        sys.exit()
    try:
        if data['version']['CFG_VERSION'] == CFG_VERSION:
            logger.info(_("Configuration file matches: %s") % CFG_VERSION)
        else:
            logger.error(_("Configuration file version conflict: %s, instead of: %s") % (data['version']['CFG_VERSION'], CFG_VERSION))
    except:
        logger.error(_("Configuration file does not contain CFG_VERSION element"))
        sys.exit()
    serverData = data['server']
    try:
        LANGUAGE = serverData['LANGUAGE']
        logger.info(_("Repetier Server language: %s") % LANGUAGE)        
    except:
        logger.error(_("Configuration file does not contain LANGUAGE element"))
        sys.exit()
    if LANGUAGE != "":
        changeLang(LANGUAGE)
    try:
        MY_REPETIER_SERVER_API_KEY = serverData['MY_REPETIER_SERVER_API_KEY']
        logger.info(_("API Key Repetier Server: %s") % MY_REPETIER_SERVER_API_KEY)        
    except:
        logger.error(_("Configuration file does not contain MY_REPETIER_SERVER_API_KEY element"))
        sys.exit()
    try:
        RepetierServerIP = serverData['RepetierServerIP']
        logger.info(_("Repetier Server IP: %s") % RepetierServerIP)        
    except:
        logger.error(_("Configuration file does not contain RepetierServerIP element"))
        sys.exit()
    try:
        RepetierServerPort = serverData['RepetierServerPort']
        logger.info(_("Repetier Server Port: %s") % RepetierServerPort)        
    except:
        logger.error(_("Configuration file does not contain RepetierServerPort element"))
        sys.exit()
    try:
        MY_TELEGRAM_TOKEN = serverData['MY_TELEGRAM_TOKEN']
        logger.info(_("Telegram Token: %s") % MY_TELEGRAM_TOKEN)        
    except:
        logger.error(_("Configuration file does not contain MY_TELEGRAM_TOKEN element"))
        sys.exit() 
    try:            
        CHATID = serverData['MY_TELEGRAM_ID'] 
        logger.info(_("Administrator Telegram ID: %s") % CHATID)        
    except:
        logger.error(_("Configuration file does not contain MY_TELEGRAM_ID element"))
        sys.exit()
    try:
        with open(CFGFILENAME, 'w') as outfile:
            json.dump(data, outfile) 
    except:
            logger.error(_("Configuration file could not be saved"))

    logger.info(_("Configuration file successfull imported: %s") % CFGFILENAME)
    return data 
    
# Telegram main external functions

def telegramSendMsg(msg, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN, parse_mode=telegram.ParseMode.MARKDOWN):
    bot = telegram.Bot(token=token)
    return bot.sendMessage(chat_id=chat_id, 
                           text=msg,
                           reply_markup=reply_markup,
                           parse_mode=parse_mode)

# Websocket

def messageCntHndl():
    global MessCnt

    MessCnt += 1    
    if MessCnt >= 1000:
        MessCnt = 1
    
    return MessCnt

def encCommand(action = "ping", callback_id = 200, printer = "My Printer", data = {}):
    command = {}
    command['action'] = action
    command['data'] = data
    command['printer'] = printer
    command['callback_id'] = callback_id
    command = json.dumps(command)
        
    return command

def printerData(action = "ping", printer = "My Printer", data = {}):
    repServAdress = "ws://" + RepetierServerIP + ":" + RepetierServerPort + "/socket/?lang=" + LANGUAGE + "&&apikey=" + MY_REPETIER_SERVER_API_KEY
    try:
        ws = create_connection(repServAdress)        
    except:
        logger.error(_("Antwort öffnen des Websocket: %s, Unerwarteter Fehler: %s") 
                     % (repServAdress, sys.exc_info()[0]))
        return "Error"
    messageCnt = messageCntHndl()
    sendServ = encCommand(action, messageCnt, printer, data)
    try:
        b = ws.send(sendServ)
    except:
        logger.error(_("Antwort auf: %s, Websocket Rückmeldung: %s : Unerwarteter Fehler: %s")
                    % (repServAdress, b, sys.exc_info()[0]))
        return "Error"

    logger.debug(_("Über Websocket gesendet: %s") % sendServ)
        
    for i in range(0,20):
        try:
            resServ = ws.recv()
        except:
            logger.error(_("Unerwarteter Fehler bei Antwort des Websocket: %s") % sys.exc_info()[0])
            ws.close()
            return "Error"
        logger.debug(_("Vom Websocket erhalten: %s") % resServ)
        
        try:
            serMess = json.loads(resServ)                
        except:
            logger.error(_("JSON: %s : Unerwarteter Fehler: %s") % (resServ, sys.exc_info()[0]))
            ws.close()
            return "Error"
        if serMess['callback_id'] != messageCnt:
            logger.debug(_("Server Meldung nicht die angeforderten: %s : Kein nutzbarer Inhalt") % resServ)
            if i == 2:
                ws.close()
                resServ = "Error"
        else:
            ws.close()
            return serMess

### GUI

class myConfigGUI(ThemedTk):
    def __init__(self, configFile, *args, **kwargs):
        super(myConfigGUI, self).__init__(*args, **kwargs)
        self.configFile = configFile
        self.set_theme(theme_name="ubuntu") 
        # "arc"/"ubuntu"/"clearlooks"/"elegance"/"radiance"
        # "kroc"/"plastik"/"winxpblue"/"blue"
        self.title(_("Quick Configuration tool for Repetier-Server bot") + " - " + _("Config Version: ") + self.configFile['version']['CFG_VERSION'] + " / " + _("Tool Version: ") + SW_VERSION)
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.iconbitmap(os.path.join(os.getcwd(), FILENAME_FILE_NO_EXT_CFG + '.ico'))
        self.initUI()
        
    def saveProgram(self):
        with open(CFGFILENAME, 'w') as outfile:
            json.dump(self.configFile, outfile)
        logger.info(_("JSON saved"))
        self.quit()

    def exitProgram(self): 
        logger.info(_("Exiting program"))
        sys.exit()

    def testConn(self):
        global LANGUAGE,MY_REPETIER_SERVER_API_KEY,RepetierServerIP
        global RepetierServerPort,MY_TELEGRAM_TOKEN,CHATID
    
        if self.checkTextFields():
            testSuccess = True
            logger.info(_("Start test routine"))
            infoMsg = _("Test Repetier Server connection:") + "\n"
            msg = printerData("listPrinter")
            if msg == "Error":
                infoMsg += _("   Connecting to Repetier-Server: %s - failed") % RepetierServerIP + "\n"
                testSuccess = False
            else:
                infoMsg += _("   Connecting to Repetier-Server: %s - successful connected") % RepetierServerIP + "\n"
                for printer in msg['data']:
                    infoMsg += _("      - Printer: %s - found") % printer['name'] + "\n"
            infoMsg += _("Test Telegram Bot connection:") + "\n"
            feedback = ""
            try:
                feedback = telegramSendMsg(_("Repetier-Server Test Message"), reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN, parse_mode=telegram.ParseMode.MARKDOWN)
                infoMsg += _("   Connecting to Telegram Bot: successful") + "\n"
            except telegram.error.BadRequest:
                infoMsg += _("   Connecting to Telegram Bot: Wrong Telegram ID - failed")
                testSuccess = False
            except telegram.error.Unauthorized:
                infoMsg += _("   Connecting to Telegram Bot: Wrong Telegram Bot Token - failed")
                testSuccess = False
            except:
                infoMsg += _("   Connecting to Telegram Bot: %s - failed") % sys.exc_info()[0]
                testSuccess = False
            self.infoText.label['text'] = infoMsg
            if testSuccess:
                logger.info(_("Test routine successful"))
                self.bottomFrame.saveButton['state'] = "normal"
                self.configFile['gui']['testSuccess'] = True
            else:
                logger.info(_("Test routine failed"))
                self.bottomFrame.saveButton['state'] = "disabled"
                self.configFile['gui']['testSuccess'] = False
        else:
            showerror(_("Blank field detected"), _("Fill out all fields!!!"))

    def initUI(self):
        ttk.Style().configure("TButton", 
                              padding=6, 
                              relief="flat",
                              background="#ccc")
        style = ttk.Style()
        style.map("C.TButton",
                foreground=[('pressed', 'green'), ('active', 'blue')],
                background=[('pressed', '!disabled', 'black'), ('active', 'white')]
                )
        style.theme_settings("default", {
                           "TCombobox": {
                               "configure": {"padding": 5},
                               "map": {
                                   "background": [("active", "green2"),
                                                  ("!disabled", "green4")],
                                   "fieldbackground": [("!disabled", "green3")],
                                   "foreground": [("focus", "OliveDrab1"),
                                                  ("!disabled", "OliveDrab2")]
                               }
                           }
                        })
        self.backgroundColor = "orange"
        self.winFrame = mainFrame(self, 
                                  width=self.winfo_width()-20, 
                                  height=self.winfo_height()-20,
                                  highlightbackground=self.backgroundColor, 
                                  highlightcolor=self.backgroundColor, 
                                  highlightthickness=1)
                                  #background="grey")
        self.winFrame.pack(expand=True, fill="both", padx=1, pady=1)
        #self.winFrame.columnconfigure(1, weight=1)
        #self.winFrame.columnconfigure(3, pad=7)
        #self.winFrame.rowconfigure(3, weight=1)
        #self.winFrame.rowconfigure(5, pad=7)
        
        configItems = self.configFile['server']
        self.language = botLanguageFrame(self.winFrame, 
                                  highlightbackground=self.backgroundColor, 
                                  highlightcolor=self.backgroundColor, 
                                  highlightthickness=1,
                                  #background="grey",
                                  item=_("Select Language"),
                                  itemData=configItems['LANGUAGE'])
        self.language.grid(row=0, column=0, columnspan=1,
                            padx=5, pady=5, sticky="ewsn")
        self.label1 = ttk.Label(self.winFrame, text=_("Network settings:"))
        self.label1.grid(row=1, column=0,sticky="w", pady=4, padx=5)
        self.netFrame = mainFrame(self.winFrame, 
                                  highlightbackground=self.backgroundColor, 
                                  highlightcolor=self.backgroundColor, 
                                  highlightthickness=1)
                                  #background="grey")
        self.netFrame.grid(row=2, column=0, rowspan=2, columnspan=4,
                            padx=5, pady=5, sticky="ewsn")
        self.rsNetwork = rsNetworkFrame(self.netFrame, 
                                  highlightbackground=self.backgroundColor, 
                                  highlightcolor=self.backgroundColor, 
                                  highlightthickness=1,
                                  #background="grey",
                                  item=_("Your Repetier-Server network adress"),
                                  itemData={"ip":configItems['RepetierServerIP'],"port":configItems['RepetierServerPort']})
        self.rsNetwork.grid(row=0, column=0, columnspan=1,
                            padx=5, pady=5, sticky="ewsn")
        self.rsAPI = botAPIFrame(self.netFrame, 
                                  highlightbackground=self.backgroundColor, 
                                  highlightcolor=self.backgroundColor, 
                                  highlightthickness=1,
                                  #background="grey",
                                  item=_("Your Repetier API Key"),
                                  itemData=configItems['MY_REPETIER_SERVER_API_KEY'])
        self.rsAPI.grid(row=1, column=0, columnspan=1,
                            padx=5, pady=5, sticky="ewsn")
        self.telegramToken = botAPIFrame(self.netFrame, 
                                  highlightbackground=self.backgroundColor, 
                                  highlightcolor=self.backgroundColor, 
                                  highlightthickness=1,
                                  #background="grey",
                                  item=_("Your Telegram botfather token"),
                                  itemData=configItems['MY_TELEGRAM_TOKEN'])
        self.telegramToken.grid(row=0, column=1, columnspan=1,
                            padx=5, pady=5, sticky="ewsn")
        self.telegramID = botAPIFrame(self.netFrame, 
                                  highlightbackground=self.backgroundColor, 
                                  highlightcolor=self.backgroundColor, 
                                  highlightthickness=1,
                                  #background="grey",
                                  item=_("Your own Telgram ID"),
                                  itemData=configItems['MY_TELEGRAM_ID'])
        self.telegramID.grid(row=1, column=1, columnspan=1,
                            padx=5, pady=5, sticky="ewsn")
        self.testConnection = ttk.Button(self.netFrame, text=_("Test"), command=self.testConn , style="C.TButton")
        self.testConnection.grid(row=0, column=4, padx=5, pady=5)
        self.label3 = ttk.Label(self.winFrame, text=_("Information:"))
        self.label3.grid(row=10, column=0,sticky="w", pady=4, padx=5)
        self.infoText = informationFrame(self.winFrame, 
                                  highlightbackground=self.backgroundColor, 
                                  highlightcolor=self.backgroundColor, 
                                  highlightthickness=1,
                                  #background="grey",
                                  item=_("Please fill out your setup and push \"Test\" button afterwards!"),
                                  itemData=None)
        self.infoText.grid(row=11, column=0, rowspan=3, columnspan=5,
                            padx=5, pady=5, sticky="ewsn")
        self.bottomFrame = bottomFrame(self.winFrame, 
                                  item=self.configFile['gui'],
                                  itemData=None)
        self.bottomFrame.grid(row=14, column=0, columnspan=5,
                            padx=5, pady=5, sticky="ewsn")
        self.checkTextFields()
    
    def checkTextFields(self):
        if self.rsNetwork.IP.get() != "" and self.rsNetwork.port.get() != "" and self.rsAPI.text.get() != "" and self.telegramToken.text.get() != "" and self.telegramID.text.get() != "":
            global LANGUAGE,MY_REPETIER_SERVER_API_KEY,RepetierServerIP
            global RepetierServerPort,MY_TELEGRAM_TOKEN,CHATID
    
            RepetierServerIP = self.rsNetwork.IP.get()
            RepetierServerPort = self.rsNetwork.port.get() 
            MY_REPETIER_SERVER_API_KEY = self.rsAPI.text.get() 
            MY_TELEGRAM_TOKEN = self.telegramToken.text.get() 
            CHATID = self.telegramID.text.get() 
            logger.info(_("checkTextFields: Repetier-Server: %s:%s, Repetier-Server-API: %s, Telegram-Token: %s, Telegram-ID: %s") % (RepetierServerIP,
                                                                                                             RepetierServerPort,
                                                                                                             MY_REPETIER_SERVER_API_KEY,
                                                                                                             MY_TELEGRAM_TOKEN,
                                                                                                             CHATID))
            return True
        else:
            return False
        
    #def onValidate(self, d, i, P, s, S, v, V, W):
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
       # print('d=%s,i=%s,P=%s,s=%s,S=%s,v=%s,V=%s,W=%s' % (d, i, P, s, S, v, V, W))
        #self.checkChanges()
        #return True

        #vcmd = (self.register(self.parent.parent.parent.onValidate),
         #      '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        #self.IP = ttk.Entry(self, width=5*3, validate="key", validatecommand=vcmd)
       
class mainFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
                        
class botLanguageFrame(tk.Frame):
    def __init__(self, parent, item, itemData, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.langPath = os.path.join(os.getcwd(), 'locale')
        self.langList = []
        for filename in os.listdir(self.langPath):
            if os.path.isdir(os.path.join(self.langPath,filename)):
                self.langList.append(filename)
        self.languageSelect = tk.StringVar()
        self.languageSelect.set(itemData)
        self.label = ttk.Label(self, text=item + ":")
        self.label.pack(side="left",padx=5, pady=5)
        self.languageCombo = ttk.Combobox(self, textvariable=self.languageSelect)
        self.languageCombo.bind('<<ComboboxSelected>>', self.langSelect)
        self.languageCombo['values'] = tuple(self.langList)
        self.languageCombo.state(["readonly"])
        self.languageCombo.pack(side="right",padx=5, pady=5)

    def langSelect(self,event): #self.botDataModified
        self.parent.parent.botDataModified['server']['LANGUAGE'] = self.languageSelect.get()
        self.languageCombo.selection_clear()
        
class rsNetworkFrame(tk.Frame):
    def __init__(self, parent, item, itemData, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.label1 = ttk.Label(self, text=item + ":")
        self.label1.pack(side="left",padx=5, pady=5)
        self.port = ttk.Entry(self, width=5*2)
        self.port.pack(side="right",padx=5, pady=5)
        self.port.insert(0, itemData['port'])
        self.label2 = ttk.Label(self, text=":")
        self.label2.pack(side="right")
        self.IP = ttk.Entry(self, width=5*3)
        self.IP.insert(0, itemData['ip'])
        self.IP.pack(side="right",padx=5, pady=5)
        
class botAPIFrame(tk.Frame):
    def __init__(self, parent, item, itemData, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.label = ttk.Label(self, text=item + ":")
        self.label.pack(side="left",padx=5, pady=5)
        self.text = ttk.Entry(self, width=50)
        self.text.insert(0, itemData)
        self.text.pack(side="right",padx=5, pady=5)

class informationFrame(tk.Frame):
    def __init__(self, parent, item, itemData, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.label = ttk.Label(self, text=item)
        self.label.pack(side="left",padx=5, pady=5)
        
class bottomFrame(tk.Frame):
    def __init__(self, parent, item, itemData, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.saveButton = ttk.Button(self, text="Ok", style="C.TButton", command=self.parent.parent.saveProgram, state="disabled")
        self.closeButton = ttk.Button(self, text=_("Exit"), style="C.TButton", command=self.parent.parent.exitProgram)
        self.saveButton.pack(side="right", anchor="s", padx=5, pady=5)
        self.closeButton.pack(side="right", anchor="s", padx=5, pady=5)
     
### Hauptcode
if __name__ == "__main__":
    threading.current_thread().name = FILENAME_NO_EXTENSION
    logger = setup_logger("Main Thread",formatter,logging.INFO,LOGFILENAME)
    loggerWS = setup_logger("WS Thread",formatter,logging.INFO,LOGFILENAMEWS)

    changeLang(None)
    presLan.install()
    _ = presLan.gettext

    logger.info(_("########### Repetier-Server Bot Setup ###########"))
    logger.info(_("Software Version: %s") % SW_VERSION)
    logger.info(_("Thread Name: %s") % threading.current_thread().getName())
    logger.info(_("########### Geräte and Python Information ###########"))
    logger.info(_("Python Version: %s") % platform.python_version())
    logger.info(_("OS: %s") % platform.system())
    logger.info(_("OS Version: %s") % platform.platform())
    username = getpass.getuser()
    logger.info(_("Active User: %s") % username)
    logger.info("####################################")

    # Import Konfigurationsdatei
    configFile = impConfig()
    presLan.install()
    _ = presLan.gettext
    
    configWindow = myConfigGUI(configFile)
    configWindow.mainloop()
    
    sys.exit()



