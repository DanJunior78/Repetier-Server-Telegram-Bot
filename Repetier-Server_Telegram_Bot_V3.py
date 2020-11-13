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
import arrow # Datum in ISO 8601
import threading, time, signal # threading libraries
import pathlib
from urllib.parse import urlparse
import getpass
import json
from websocket import create_connection
import requests
import imageio
from pygifsicle import optimize #pip install pygifsicle + https://eternallybored.org/misc/gifsicle/ und bei Python kopieren
import cv2
import telegram
from telegram import (InlineQueryResultArticle,
                    InputTextMessageContent,
                    InlineKeyboardButton,
                    InlineKeyboardMarkup,
                    ReplyKeyboardMarkup,
                    Animation,
                    ParseMode)

from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          InlineQueryHandler,
                          CallbackQueryHandler,
                          Filters,
                          ConversationHandler)
from telegram.error import (TelegramError,
                            Unauthorized,
                            BadRequest,
                            TimedOut,
                            ChatMigrated,
                            NetworkError)

SW_VERSION = "0.3"
CFG_VERSION = "V03"
EX_DEBUG = False

LANGUAGE = "de"

# Repetier-Server
RepetierServerIP = ""
RepetierServerIP2 = ""
RepetierServerPort = ""
MY_REPETIER_SERVER_API_KEY = ""
MessCnt = 0

# Bot Einstellungen
MY_TELEGRAM_TOKEN = ""
CHATID = ""
Printer = 1
# Bot Ebenen
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN = range(10)

# Ermittlung der verwendeten Platform
checkPlatform = platform.platform()

# Logfile erstellen im Unterordner von der Aufrufumgebung
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

# Konfiguration und externe Daten

## Konfigurationsdatei
FILENAME_FILE_NO_EXT_CFG = FILENAME_NO_EXTENSION
CFGFILENAME =  os.path.join(os.getcwd(), FILENAME_FILE_NO_EXT_CFG + '.json')

## Video & Gifs
PNGFILEFOLDER = os.path.join(os.getcwd(), 'pic', 'png')
GIFFILEFOLDER = os.path.join(os.getcwd(), 'pic', 'gif') 
VIDFILEFOLDER = os.path.join(os.getcwd(), 'vid') 

## Konstanten
HEIGHTMSG, TIMEMSG, LAYERMSG = range(3)
### Funktionen

# Sprachverwaltung

def changeLang(langSel = None):
    global presLan
    _ = presLan.gettext
    langPath = os.path.join(os.getcwd(), 'locale')
    logger.info(_("Sprachedateipfad: %s") % langPath)
    if langSel == None:
        if sys.platform.startswith('win'):
            if os.getenv('LANG') is None:
                lang, enc = locale.getdefaultlocale()
                logger.info(_("Sprache OS: %s/%s") % locale.getdefaultlocale())
                os.environ['LANG'] = lang
                langSel = lang
    else:
        os.environ['LANG'] = '%s' % langSel
    if gettext.find('Repetier-Server_Telegram_Bot_V3', langPath) == None:
        os.environ['LANG'] = 'en'
        logger.info(_("Sprache auf Ausweichsprache englisch umgestellt"))
    else:
        logger.info(_("Sprache auf \"%s\" umgestellt") % langSel)
    presLan = gettext.translation('Repetier-Server_Telegram_Bot_V3', './locale')
    print(5)
    logger.debug(_("Sprachedateiinfo: %s") % presLan._info)
    presLan.install()
    _ = presLan.gettext
    
# Logger aufsetzen

def setup_logger(name, formatter, level, log_file):
    """To setup as many loggers as you want"""
    if EX_DEBUG == True:
        logging.basicConfig(format=formatter,level=level)
    else:
        logging.basicConfig(filename=LOGFILENAME, filemode='w',format=formatter,
                     level=level)
    
    logger = logging.getLogger(name)
    logger.info(_("Logger: %s wurde im Debug Modus(%s) aktiviert. Level: %s") % (name, EX_DEBUG, level))
    
    return logger

# Konfigurationsdatei einlesen
def impConfig():
    global LANGUAGE,MY_REPETIER_SERVER_API_KEY,RepetierServerIP
    global RepetierServerIP2,RepetierServerPort,MY_TELEGRAM_TOKEN,CHATID
    global LOGFILENAME,LOGFILENAMEWS,PNGFILEFOLDER,GIFFILEFOLDER,VIDFILEFOLDER
    global presLan
    try:
        with open(CFGFILENAME) as json_file:
            data = json.load(json_file)
    except:
        logger.error(_("Konfigurationsdatei nicht gefunden - impConfig - : %s") % CFGFILENAME)
        sys.exit()
    try:
        if data['CFG_VERSION'] == CFG_VERSION:
            logger.info(_("Konfigurationsversion stimmt überein: %s") % CFG_VERSION)
        else:
            logger.error(_("Konfigurationsdatei Versionskonflikt: %s, anstatt: %s") % (data['CFG_VERSION'], CFG_VERSION))
    except:
        logger.error(_("Konfigurationsdatei enthält Element CFG_VERSION nicht"))
        sys.exit()
    try:
        LANGUAGE = data['LANGUAGE']
        logger.info(_("Sprache Repetier Server: %s") % LANGUAGE)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element LANGUAGE nicht"))
        sys.exit()
    if LANGUAGE != "":
        changeLang(LANGUAGE)
    try:
        MY_REPETIER_SERVER_API_KEY = data['MY_REPETIER_SERVER_API_KEY']
        logger.info(_("API Key Repetier Server: %s") % MY_REPETIER_SERVER_API_KEY)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element MY_REPETIER_SERVER_API_KEY nicht"))
        sys.exit()
    try:
        RepetierServerIP = data['RepetierServerIP']
        logger.info(_("Repetier Server IP: %s") % RepetierServerIP)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element RepetierServerIP nicht"))
        sys.exit()
    try:
        RepetierServerIP2 = data['RepetierServerIP2']
        logger.info(_("Repetier Server IP2: %s") % RepetierServerIP2)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element RepetierServerIP2 nicht"))
        sys.exit()
    try:
        RepetierServerPort = data['RepetierServerPort']
        logger.info(_("Repetier Server Port: %s") % RepetierServerPort)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element RepetierServerPort nicht"))
        sys.exit()
    try:
        MY_TELEGRAM_TOKEN = data['MY_TELEGRAM_TOKEN']
        logger.info(_("Telegram Token: %s") % MY_TELEGRAM_TOKEN)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element MY_TELEGRAM_TOKEN nicht"))
        sys.exit() 
    try:            
        CHATID = data['MY_TELEGRAM_ID'] 
        logger.info(_("Administrator Telegram ID: %s") % CHATID)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element MY_TELEGRAM_ID nicht"))
        sys.exit()
    try:            
        LogFileName = data['LOGFILENAME'] 
        logger.info(_("LogFileName: %s") % LogFileName)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element LOGFILENAME nicht"))
        sys.exit()
    if LogFileName != "":
        LOGFILENAME = LogFileName
    data['LOGFILENAME'] = LOGFILENAME
    try:            
        LogFileNameWS = data['LOGFILENAMEWS'] 
        logger.info(_("LogFileNameWS: %s") % LogFileNameWS)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element LOGFILENAMEWS nicht"))
        sys.exit()
    if LogFileNameWS != "":
        LOGFILENAMEWS = LogFileNameWS
    data['LOGFILENAMEWS'] = LOGFILENAMEWS
    try:            
        PNGFileFolder = data['PNGFILEFOLDER'] 
        logger.info(_("PNGFileFolder: %s") % PNGFileFolder)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element PNGFILEFOLDER nicht"))
        sys.exit()
    if PNGFileFolder != "":
        PNGFILEFOLDER = PNGFileFolder
    data['PNGFILEFOLDER'] = PNGFILEFOLDER
    try:            
        GIFFileFolder = data['GIFFILEFOLDER'] 
        logger.info(_("GIFFileFolder: %s") % GIFFileFolder)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element GIFFILEFOLDER nicht"))
        sys.exit()
    if GIFFileFolder != "":
        GIFFILEFOLDER = GIFFileFolder
    data['GIFFILEFOLDER'] = GIFFILEFOLDER
    try:            
        VIDFileFolder = data['VIDFILEFOLDER'] 
        logger.info(_("VIDFileFolder: %s") % VIDFileFolder)        
    except:
        logger.error(_("Konfigurationsdatei enthält Element GIFFILEFOLDER nicht"))
        sys.exit()
    if VIDFileFolder != "":
        VIDFILEFOLDER = VIDFileFolder
    data['VIDFILEFOLDER'] = VIDFILEFOLDER
    try:
        with open(CFGFILENAME, 'w') as outfile:
            json.dump(data, outfile) 
    except:
            logger.error(_("Konfigurationsdatei konnte nicht beschrieben werden"))

    logger.info(_("Konfigurationsdatei erfolgreich eingelesen: %s") % CFGFILENAME) 

# Telegram Hauptfunktionen
def telegramSendMsg(msg, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN):
    bot = telegram.Bot(token=token)
    return bot.sendMessage(chat_id=chat_id, 
                           text=msg,
                           reply_markup=reply_markup)

def telegramDelMsg(message_id, chat_id=CHATID, token=MY_TELEGRAM_TOKEN):
    bot = telegram.Bot(token=token)
    return bot.deleteMessage(chat_id=chat_id, 
                             message_id=message_id)

def telegramSendPic(pic, caption, chat_id=CHATID, token=MY_TELEGRAM_TOKEN):
    bot = telegram.Bot(token=token)
    return bot.send_photo(chat_id=chat_id, 
                          photo=open(pic, 'rb'), timeout=100,
                          caption=caption)

def telegramSendAnimation(anim, caption, chat_id=CHATID, token=MY_TELEGRAM_TOKEN):
    bot = telegram.Bot(token=token)
    return bot.send_animation(chat_id=chat_id, 
                          animation=open(anim, 'rb'), timeout=100,
                          caption=caption)

def telegramSendVideo(video, caption, chat_id=CHATID, token=MY_TELEGRAM_TOKEN):
    bot = telegram.Bot(token=token)
    return bot.send_video(chat_id=chat_id,video=open(video, 'rb'), 
                          timeout=100, 
                          supports_streaming=True,
                          caption=caption)

def telegramEditMsg(msg, message_id, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN):
    bot = telegram.Bot(token=token)
    return bot.edit_message_text(chat_id=chat_id, 
                                  message_id=message_id,
                                  text=msg,
                                  reply_markup=reply_markup)

def telegramChatAction(action, chat_id=CHATID, token=MY_TELEGRAM_TOKEN):
                        bot = telegram.Bot(token=token)
                        bot.sendChatAction(chat_id=chat_id , 
                                            action = action)
                        # telegram.ChatAction.TYPING
                        #                    .FIND_LOCATION
                        #                    .RECORD_AUDIO
                        #                    .RECORD_VIDEO
                        #                    .RECORD_VIDEO_NOTE
                        #                    .UPLOAD_AUDIO
                        #                    .UPLOAD_DOCUMENT
                        #                    .UPLOAD_PHOTO
                        #                    .UPLOAD_VIDEO
                        #                    .UPLOAD_VIDEO_NOTE
def isfloat(str):
    try: 
        float(str)
    except ValueError: 
        return False
    return True

def isint(str):
    try: 
        int(str)
    except ValueError: 
        return False
    return True

def getGranularity(deltaT = 0): # in seconds (datetime..timedelta.total_seconds())
    seconds = int(deltaT)
    seconds_in_day = 60 * 60 * 24
    seconds_in_hour = 60 * 60
    seconds_in_minute = 60

    days = seconds // seconds_in_day
    hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
    minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
    second = seconds % 60
    if days > 0:
        
        granularity=["day","hour", "minute","second"]
        return granularity
    elif hours > 0:
        granularity=["hour", "minute","second"]
        return granularity
    elif minutes > 0:
        granularity=["minute","second"]
        return granularity
    else:
        granularity=["second"]
        return granularity

def getTimeToGo(start = 0, timeToPrint = 0):
    global LANGUAGE
    present = arrow.now()
    present = present.replace(tzinfo='UTC')
    printFinishTime = arrow.get(int(start) + int(timeToPrint))#, 'Europe/Berlin') #Europe/Berlin    
    timeToGo = printFinishTime - present
    message = printFinishTime.humanize(present, locale=LANGUAGE, granularity=getGranularity(timeToGo.total_seconds())) # LANGUAGE # 'de'
    return message

def getTimeGone(start = 0):
    global LANGUAGE
    present = arrow.now()
    present = present.replace(tzinfo='UTC')
    printStart = arrow.get(int(start))
    actPrintTime = present - printStart
    message = printStart.humanize(present, locale=LANGUAGE,granularity=getGranularity(actPrintTime.total_seconds()))
    return message

def error_callback(update, error): # def callback(update: Update, context: CallbackContext) -> context.error
    """
    Handle errors in the dispatcher and decide which errors are just logged and which errors are important enough to
    trigger a message to the admin.
    """
    try:
        telegramSendMsg(_("BOT Fehler!!! Versuch es noch einmal.\n %s") % error.error,reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        raise error.error
    except telegram.error.BadRequest:
        logger.error(_('Bot Bad Request "%s"') % error.error)
    except telegram.error.TimedOut:
        logger.error(_('Bot TimedOut "%s"') % error.error)
    except:
        logger.error(_('Bot Error "%s"') % error.error) 

def checkUserIDValid(update, chatID=CHATID):
    if update.effective_chat.id == chatID:
        return True
    else:
        return False    

# Telegram spezifische Bot Funktionen
def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    """
    :param buttons: a list of buttons.
    :param n_cols:  how many columns to show the butt,ons in
    :param header_buttons:  list of buttons appended to the beginning
    :param footer_buttons:  list of buttons added to the end
    :return: the menu
    """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return InlineKeyboardMarkup(menu)

def getStartKeyboard(userKeyb = []):
    stdKeyb = []

    stdKeyb.append(InlineKeyboardButton(_("Ende"), callback_data='End'))
    reply_markup = build_menu(userKeyb,
               1,
               footer_buttons=stdKeyb)
    return reply_markup

def getKeyboard(userKeyb = [], back = ""):
    stdKeyb = []

    stdKeyb.append(InlineKeyboardButton(_("Zurück"), callback_data='Back'))
    stdKeyb.append(InlineKeyboardButton(_("Ende"), callback_data='End'))
    reply_markup = build_menu(userKeyb,
               2,
               footer_buttons=stdKeyb)
    return reply_markup

def checkStartKeys(slug):
    slug = slug[1:]    
    key = []
    msg = printerData("listExternalCommands")
    msg2 = printerData("getPrinterConfig", slug)
    if msg == "Error" or msg2 == "Error":
        return key
    items = msg['data']
    if len(items) > 0:    
        key.append(InlineKeyboardButton(_("ExtCommands"), callback_data='ExtCommands'))
    items2 = msg2['data']
    for webcam in range(0,len(items2['webcams'])):
        key.append(InlineKeyboardButton(_('Webcam %s') % str(webcam + 1), callback_data='Webcam %s' % str(webcam + 1)))
    return key

def getExtCommands():
    key = []
    msg = printerData("listExternalCommands")
    if msg == "Error":
        return key
    items = msg['data']
    for item in items:    
        key.append(InlineKeyboardButton(item['name'], callback_data=item['id']))
    return key

def getExtCommandsConfirmButton(command):
    key = []
    msg = printerData("listExternalCommands")
    if msg == "Error":
        return key
    items = msg['data']
    for item in items:
        if item['id'] == command:
            key.append(InlineKeyboardButton(_("OK"), callback_data='OK'))
    return key

def getExtCommandsConfirmText(command):
    msg = printerData("listExternalCommands")
    if msg == "Error":
        return "Error"
    items = msg['data']
    for item in items:
        if item['id'] == command:            
            return item['confirm']
        
def sendExtCommand(updateMsgTxt):
    key = []
    msg = printerData("listExternalCommands")
    if msg == "Error":
        return key
    items = msg['data']
    for item in items:
        if item['confirm'] == updateMsgTxt:
            packOrder = {}
            packOrder['id'] = item['id']
            if printerData("runExternalCommand","My Printer",packOrder) == "Error":
                timeDelThread(bot = True, 
                            feedbackMsg = telegramSendMsg(_("Befehl fehlgeschlagen"),reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN),
                            botRequests = botThreads.botRequests)
            else:
                timeDelThread(bot = True, 
                            feedbackMsg = telegramSendMsg(_("Befehl ausgeführt"),reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN),
                            botRequests = botThreads.botRequests)
    return key

def getWebcamConfig(slug, update):
    slug = slug[1:]  
    queryData = update.callback_query.data
    key = []
    msg2 = printerData("getPrinterConfig", slug)
    if msg2 == "Error":
        return key
    items2 = msg2['data']
    x = int(queryData.split()[1]) - 1
    if items2['webcams'][x]['dynamicUrl'] != "":
        key.append(InlineKeyboardButton(_('Sende Video Kamera %s') % str(x + 1), callback_data='Sende Video %s' % str(x + 1))) # 'Sende Video %s' % str(webcam + 1)
    if items2['webcams'][x]['staticUrl'] != "": 
        key.append(InlineKeyboardButton(_('Sende Gif Kamera %s') % str(x + 1), callback_data='Sende Gif %s' % str(x + 1)))
        key.append(InlineKeyboardButton(_('Sende Png Kamera %s') % str(x + 1), callback_data='Sende Png %s' % str(x + 1)))
    return key

def saveAdditionalMessage(slug, msgReply): 
    slug = slug[1:]
    for IDs in botThreads.msgIDs:
        if IDs['slug'] == slug:
            AddMsg = {}
            AddMsg['messageID'] = msgReply['message_id']
            AddMsg['chatID'] = msgReply['chat']['id']
            IDs['additional_message'].append(AddMsg)

def removeAdditionalMessage(slug,context):
    slug = slug[1:]
    for IDs in botThreads.msgIDs:
        if IDs['slug'] == slug:
            for msgs in IDs['additional_message']:
                context.bot.deleteMessage(chat_id=msgs['chatID'], message_id=msgs['messageID'])
            IDs['additional_message'] = []

def removeAllAdditionalMessage(context):
    for IDs in botThreads.msgIDs:
        for msgs in IDs['additional_message']:
            context.bot.deleteMessage(chat_id=msgs['chatID'], message_id=msgs['messageID'])
        IDs['additional_message'] = []

def checkPrinterMsgID(slug): 
    slug = slug[1:]
    for printerData in botThreads.msgIDs:
        if printerData['slug'] == slug:
            return printerData['messageID']

def updatePrinterMsgReplayMarkup(slug, msgReply, reNewMsg = False):
    slug = slug[1:]
    for printerData in botThreads.msgIDs:
        if printerData['slug'] == slug:
            printerData['reply_markup'] = msgReply['reply_markup']
            if reNewMsg:
                logger.info(_("updatePrinterMsgReplayMarkup: Drucker %s löscht MessageID: %s") % (printerData['slug'], printerData['messageID']))
                telegramDelMsg(printerData['messageID'], chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
                printerData['RequestNewMessageID'] = True
                printerData['expanded'] = True
                
def printerAddTracking(slug, context):
    context.user_data['slug'] = slug    

def printerGetTracking(context):
    return context.user_data['slug']

def removePrinterMsgReplayMarkup(slug):
    slug = slug[1:]
    for printerData in botThreads.msgIDs:
        if printerData['slug'] == slug:
            printerData['reply_markup'] = None
            printerData['expanded'] = False

def removeAllPrinterMsgReplayMarkup():
    for printerData in botThreads.msgIDs:
        printerData['reply_markup'] = None
        printerData['expanded'] = False

def mainMenu(update, context):
    if not checkUserIDValid(update,chatID=CHATID):
        logger.critical(_("Bot antwortet auf unbekannten client: %s / %s: %s, %s") % (update.effective_chat.username, 
                                                                                      update.effective_chat.id, 
                                                                                      update.effective_chat.last_name, 
                                                                                      update.effective_chat.first_name)
                        )
        msgTelegram = _("Unbefugter Zugriff durch Nutzer %s, %s %s") % (update.effective_chat.username, 
                                                                        update.effective_chat.first_name, 
                                                                        update.effective_chat.last_name
                                                                        )
        telegramSendMsg(msgTelegram,reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
    
        update.message.reply_text(_('Kein Zugriff!'))
        return ConversationHandler.END
    timeDelThread(messageID = update.message.message_id, delayTimeSelect = 1)
    text = update.message.text
    printerAddTracking(text, context)
    updatePrinterMsgReplayMarkup(
                            text,
                            context.bot.edit_message_reply_markup(chat_id=update.message.chat.id,
                            message_id=checkPrinterMsgID(text), 
                            reply_markup=getStartKeyboard(checkStartKeys(text))),
                            True)
    return ONE 

def extCommands(update, context):
    queryMessageData = update.callback_query.message
    updatePrinterMsgReplayMarkup(
                            printerGetTracking(context),
                            context.bot.edit_message_reply_markup(chat_id=queryMessageData.chat.id,
                            message_id=queryMessageData.message_id, 
                            reply_markup=getKeyboard(getExtCommands())))
    return TWO

def extCommandsBack(update,context):
    queryMessageData = update.callback_query.message
    updatePrinterMsgReplayMarkup(
                            printerGetTracking(context),
                            context.bot.edit_message_reply_markup(chat_id=queryMessageData.chat.id,
                            message_id=queryMessageData.message_id, 
                            reply_markup=getStartKeyboard(checkStartKeys(printerGetTracking(context)))))    
    removeAllAdditionalMessage(context)
    return ONE

def extCommandsChoosen(update,context):
    queryMessageData = update.callback_query.message
    updatePrinterMsgReplayMarkup(
                            printerGetTracking(context),
                            context.bot.edit_message_reply_markup(chat_id=queryMessageData.chat.id,
                            message_id=queryMessageData.message_id, 
                            reply_markup=None))  
    saveAdditionalMessage(
                            printerGetTracking(context),
                            context.bot.send_message(
                            chat_id=queryMessageData.chat.id,
                            text=getExtCommandsConfirmText(int(update.callback_query.data)),
                            reply_markup=getKeyboard(getExtCommandsConfirmButton(int(update.callback_query.data)))))
    return THREE

def extCommandAction(update,context):
    queryMessageData = update.callback_query.message
    updatePrinterMsgReplayMarkup(
                            printerGetTracking(context),
                            context.bot.edit_message_reply_markup(
                            chat_id=queryMessageData.chat.id,
                            message_id=queryMessageData.message_id, 
                            reply_markup=getKeyboard(getExtCommands()))) 
    sendExtCommand(queryMessageData.text)
    removeAllAdditionalMessage(context)
    return TWO

def webcams(update, context):
    queryMessageData = update.callback_query.message
    updatePrinterMsgReplayMarkup(
                            printerGetTracking(context),
                            context.bot.edit_message_reply_markup(
                            chat_id=queryMessageData.chat.id,
                            message_id=queryMessageData.message_id, 
                            reply_markup=getKeyboard(getWebcamConfig(printerGetTracking(context), update))))
    return FOUR

def webcamSendVideo(update, context):
    queryData = update.callback_query.data
    botThreads.startVidThread(queryData, queryData, printerGetTracking(context), CHATID)
    removeAllPrinterMsgReplayMarkup()
    removeAllAdditionalMessage(context)
    return ConversationHandler.END

def webcamSendGif(update, context):
    queryData = update.callback_query.data
    botThreads.startGifThread(queryData, queryData, printerGetTracking(context), CHATID)
    removeAllPrinterMsgReplayMarkup()
    removeAllAdditionalMessage(context)
    return ConversationHandler.END

def webcamSendPng(update, context):
    queryData = update.callback_query.data
    botThreads.startPngThread(queryData, queryData, printerGetTracking(context), CHATID)
    removeAllPrinterMsgReplayMarkup()
    removeAllAdditionalMessage(context)
    return ConversationHandler.END

def exitBot(update, context):
    removeAllPrinterMsgReplayMarkup()
    removeAllAdditionalMessage(context)
    logger.debug(_("Bot beendet Konversation: %s (%s): %s, %s") 
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

def unknownCommand(update, context):  
    removeAllPrinterMsgReplayMarkup()
    removeAllAdditionalMessage(context)
    timeDelThread(bot = True,
                  feedbackMsg = telegramSendMsg(_("Ich nix versteh %s, %s.") % (update.message.text, update.effective_chat.first_name),
                                                reply_markup=None, 
                                                chat_id=CHATID, 
                                                token=MY_TELEGRAM_TOKEN),
                  delayTimeSelect = 10,
                  botRequests = botThreads.botRequests)
    logger.info(_("Bot kennt Antwort nicht: %s") % update.message.text)
    return ConversationHandler.END

def botTimeout(update, context):   
    removeAllPrinterMsgReplayMarkup()
    removeAllAdditionalMessage(context)
    timeDelThread(bot = True,
                  feedbackMsg = telegramSendMsg(_("Du warst zu langsam, %s. Jetzt darfst nochmal drücken!!!") 
                                                % update.effective_chat.first_name,
                                                  reply_markup=None, 
                                                  chat_id=CHATID, 
                                                  token=MY_TELEGRAM_TOKEN), 
                  delayTimeSelect = 10,
                  botRequests = botThreads.botRequests)
    logger.info(_("Konversations-Timeout"))
    return ConversationHandler.END

def resetMsgs(update, context):
    timeDelThread(messageID = update.message.message_id, delayTimeSelect = 1)
    for item in botThreads.msgIDs:
        item['RequestNewMessageID'] = True
    return ConversationHandler.END

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

# Threading

class ProgramKilled(Exception):
    pass

def signal_handler(signum, frame):
    raise ProgramKilled

class wsThread(threading.Thread):
    def __init__(self, interval, execute, name, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.name = name
        self.websocket = None
        self.serverData = []
        self.args = args
        self.kwargs = kwargs
        loggerWS.info(_("Thread initialisiert: %s") % self.name)
        
    def stop(self):
        self.stopped.set()
        self.join()        
        loggerWS.info(_("Thread %s beendet: Ident: %s / ID: %s") % (self.getName(), self.ident, self.native_id))
        
    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.serverData.insert(0, [self.execute(self.websocket,*self.args, **self.kwargs)])
            
class hdlThread(threading.Thread):
    def __init__(self, interval, execute, name, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.name = name
        self.args = args
        self.kwargs = kwargs
        loggerWS.info(_("Thread initialisiert: %s") % self.name)
        
    def stop(self):
        self.stopped.set()
        self.join()        
        loggerWS.info(_("Thread %s beendet: Ident: %s / ID: %s") % (self.getName(), self.ident, self.native_id))
        
    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)

class timeDelThread(threading.Thread):
    def __init__(self, bot = False, context = None, feedbackMsg = {}, messageID = 0, chatID = CHATID, delayTimeSelect = 15, printer = "Communication Message", botRequests = [], *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.bot = bot
        self.context = context
        self.feedbackMsg = feedbackMsg
        self.messageID = messageID
        self.chatID = chatID
        self.delayTimeSelect = timedelta(seconds=delayTimeSelect)
        self.printer = printer
        self.botRequests = botRequests
        self.args = args
        self.kwargs = kwargs

        if self.messageID == 0 or self.chatID == 0:
            self.messageID = self.feedbackMsg['message_id']
            self.name = self.messageID        
            self.chatID = self.feedbackMsg['chat']['id']
            logger.info(_("Thread (keine ID vorhanden) initialisiert für MessageID: %s mit er Laufzeit: %ss") % (self.messageID, self.delayTimeSelect))
        else:
            self.name = self.messageID                
            if self.printer != None:
                logger.info(_("Thread initialisiert für Drucker: %s und MessageID: %s mit er Laufzeit: %ss") % (printer, self.messageID, self.delayTimeSelect))
            else:
                logger.info(_("Thread initialisiert für MessageID: %s mit er Laufzeit: %ss") % (self.messageID, self.delayTimeSelect))
        self.start()
        
    def stop(self):
        self.join()        
        logger.info(_("Thread Nachricht löschen für MessageID %s beendet: Ident: %s / ID: %s") % (self.messageID, self.ident, self.native_id))
        
    def run(self):
        self.stopped.wait(self.delayTimeSelect.total_seconds())
        self.delMessage(*self.args, **self.kwargs)

    def delMessage(self):
        if self.delayTimeSelect != 0:
            try:
                self.telegramDelMsg(self.messageID, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
            except:
                loggerWS.error(_("Konnte in delMessage Methode keine telegramDelMsg senden auf messageID: %s") % self.messageID)
            logger.info(_("MessageID %s von der chatID %s wurde gelöscht") % (self.messageID, self.chatID))

    def telegramDelMsg(self, message_id, chat_id, token = MY_TELEGRAM_TOKEN):
        bot = telegram.Bot(token=token)
        return bot.deleteMessage(chat_id=chat_id, message_id=message_id)

class msgThread(threading.Thread):
    def __init__(self, execute, name, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval=timedelta(seconds=2)
        self.execute = execute
        self.name = name
        self.args = args
        self.kwargs = kwargs

        self.messageID = 0
        self.chatID = 0
        loggerWS.info(_("Drucker Thread initialisiert: %s") % self.name)
        
    def stop(self):
        self.stopped.set()
        self.join()        
        loggerWS.info(_("Thread %s beendet: Ident: %s / ID: %s") % (self.getName(), self.ident, self.native_id))
        
    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.messageID, self.chatID = self.execute(self.name, self.messageID, self.chatID, *self.args, **self.kwargs)
            
class vidGifThread(threading.Thread):
    def __init__(self, execute, queryData, slug, chatID, name, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.execute = execute
        self.queryData = queryData
        self.slug = slug
        self.chatID = chatID
        self.name = name
        self.args = args
        self.kwargs = kwargs

        loggerWS.info(_("Thread initialisiert: %s") % self.name)
        
    def stop(self):
        self.stopped.set()
        self.join()        
        loggerWS.info(_("Thread %s beendet: Ident: %s / ID: %s") % (self.getName(), self.ident, self.native_id))
        
    def run(self):
        self.execute(self.queryData, self.slug, self.chatID, *self.args, **self.kwargs)
                                
class wsThreadHdl(wsThread):
    def __init__(self, telegramDispatcher, *args, **kwargs):
        self.telegramDispatcher = telegramDispatcher
        self.botHandlers = []
        self.webserver = "ws://" + RepetierServerIP + ":" + RepetierServerPort + "/socket/?lang=de&&apikey=" + MY_REPETIER_SERVER_API_KEY
        self.websocket = None
        self.restartWsSR = 0
        self.restartOD = 0
        self.blockMultiJobsChangedMsg = 0
        self.blockprinterListChangedMsg = 0
        self.intervalSend = timedelta(seconds=5)
        self.intervalRec = timedelta(seconds=0)
        self.intervalOrder = timedelta(seconds=2)
        self.intervalRestart = timedelta(seconds=30)
        self.sendCommand = self.encCommand()
        self.orderDataStorage = []
        self.botRequests = []
        self.msgActiveThreads = []
        self.msgIDs = []
        self.actGifs = []
        self.actVids = []
        self.threadLock = threading.Lock()
        self.wsThreadSend = wsThread(interval=self.intervalSend, execute=self.ThreadSend, name="Repetier-Server-Send")
        self.wsThreadRec = wsThread(interval=self.intervalRec, execute=self.ThreadRec, name="Repetier-Server-Receive")
        self.wsThreadOrderData = hdlThread(interval=self.intervalOrder, execute=self.ThreadHdlOrderData, name="Repetier-Server-Order-Data")
        self.wsThreadRestart = hdlThread(interval=self.intervalRestart, execute=self.ThreadHdlRestart, name="Repetier-Server-Restart-Threads")

    def start(self):
        if self.wsWebsocket() == 'Error':
            return 'Error'
        self.wsThreadSend.websocket = self.websocket
        self.wsThreadRec.websocket = self.websocket
        self.botData()        
        self.wsThreadSend.start()
        self.wsThreadRec.start()
        self.wsThreadOrderData.start()
        self.wsThreadRestart.start()
        self.checkForMsgThreads()
        loggerWS.info(_("Threads %s gestartet") % self.getNames())

    def stop(self):
        self.stopMsgThreads()
        self.wsThreadRestart.stop()
        self.wsThreadSend.stop()
        self.wsThreadRec.stop()
        self.wsThreadOrderData.stop()
        self.websocket.close()
        loggerWS.info(_("Threads %s beendet") % self.getNames())
        return None

    def stopMsgThreads(self):
        for threads in self.msgActiveThreads:
            threads.stop()
        
    def startMsgThread(self, name):
        x = msgThread(execute=self.msgPrinter,
                          name=name)
        x.start()
        self.msgActiveThreads.append(x)

    def startPngThread(self, name, queryData, slug, chatID):
        x = vidGifThread(execute=self.buildPng, 
                      queryData=queryData, 
                      slug=slug, 
                      chatID=chatID,
                      name=name)
        x.start()

    def startGifThread(self, name, queryData, slug, chatID):
        x = vidGifThread(execute=self.buildGif, 
                      queryData=queryData, 
                      slug=slug, 
                      chatID=chatID,
                      name=name)
        x.start()

    def startVidThread(self, name, queryData, slug, chatID):
        x = vidGifThread(execute=self.buildVid, 
                      queryData=queryData, 
                      slug=slug, 
                      chatID=chatID,
                      name=name)
        x.start()
        
    def checkMsgThreadAvail(self, name):
        for threads in self.msgActiveThreads:
            if threads.name == name:
                return True
        return False

    def getPrinterMsgThread(self, name):
        printerThreads = []
        for threads in self.msgActiveThreads:
            if threads.name == name:
                printerThreads.append(threads)
        return printerThreads
        
    def stopByMsgThread(self, thread):
        for threads in self.msgActiveThreads:
            if  threads == thread:
                threads.stop()
                try:
                    self.msgActiveThreads.remove(threads)
                except:
                    loggerWS.error(_("Kann Thread nicht aus Liste msgActiveThreads löschen. Drucker: %s") % threads.name)
                loggerWS.info(_("Thread %s beendet") % threads.name)

    def stopSingleMsgThread(self, name):
        for threads in self.msgActiveThreads:
            if threads.name == name:
                threads.stop()
                try:
                    self.msgActiveThreads.remove(threads)
                except:
                    loggerWS.error(_("Kann Thread nicht aus Liste msgActiveThreads löschen. Drucker: %s") % name)
                loggerWS.info(_("Thread %s beendet") % self.getName())

    def delPrinterMsg(self):
        for IDs in self.msgIDs:
            timeDelThread(printer=IDs['name'],messageID=IDs['messageID'],delayTimeSelect=1)

    def addHandler(self, item):
        conv_handler = ConversationHandler(
        entry_points=[CommandHandler(item['slug'], mainMenu)
                      ],
        states={
            ONE: [CallbackQueryHandler(exitBot, pattern="^End$"),
                  CallbackQueryHandler(extCommands, pattern="^ExtCommands$"), # Start Ebene
                  CallbackQueryHandler(webcams, pattern="Webcam*")],
            TWO: [CallbackQueryHandler(exitBot, pattern="^End$"), # ExtCommand Ebene
                  CallbackQueryHandler(extCommandsBack, pattern="^Back$"), 
                  CallbackQueryHandler(extCommandsChoosen)
                  ],
            THREE: [CallbackQueryHandler(exitBot, pattern="^End$"), # ExtCommand Ebene
                  CallbackQueryHandler(extCommands, pattern="^Back$"), 
                  CallbackQueryHandler(extCommandAction, pattern="^OK$")
                  ],
            FOUR: [CallbackQueryHandler(exitBot, pattern="^End$"), # ExtCommand Ebene
                  CallbackQueryHandler(extCommandsBack, pattern="^Back$"), 
                  CallbackQueryHandler(webcamSendVideo, pattern="Sende Video*"),
                  CallbackQueryHandler(webcamSendGif, pattern="Sende Gif*"),
                  CallbackQueryHandler(webcamSendPng, pattern="Sende Png*")
                  ],
            ConversationHandler.TIMEOUT:[MessageHandler(Filters.all, botTimeout)], # ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, timeout)]        
                },
        fallbacks=[MessageHandler(Filters.all, unknownCommand)],
        allow_reentry=True,
        conversation_timeout=60,
        name="Repetier-Server-Bot"
        )
        toAdd = {}
        toAdd['slug'] = item['slug']
        toAdd['handler'] = conv_handler
        self.telegramDispatcher.add_handler(conv_handler)
        self.botHandlers.append(toAdd)
        loggerWS.info(_("Handler %s hinzugefügt") % item['slug'])

    def removeHandler(self, botItem): # remove_handler(handler)
        for handler in self.botHandlers:
            if handler['slug'] == botItem['slug']:
                self.telegramDispatcher.remove_handler(handler['handler'])
                self.botHandlers.remove(handler)


    def getNewPrinter(self, slug = "ugly printer", name = "nasty printer", telegramHistory = False, 
                      telegramDelMessTime = 60):
        printerBuffer = {}
        printerBuffer['printer'] = slug
        printerBuffer['name'] = name        
        printerBuffer['telegramHistory'] = telegramHistory
        return printerBuffer

    def updPrinterDataInThread(self, data = {}):
        for printers in self.botRequests:
            if printers['name'] == data['name']:
                printers['telegramHistory'] = data['telegramHistory'] 
                
    def checkForMsgThreads(self):
        msg = printerData("listPrinter") 
        if msg != "Error":
            items = msg['data']
            self.checkServerConfigChange(items)
            self.checkBotToServerConfig(items)
            for item in items:
                if item['job'] == "none":
                    printThrdList = self.getPrinterMsgThread(item['name'])
                    for printer in printThrdList:
                        self.renewMsgID(item['name'])
                        self.stopByMsgThread(printer)
                    self.keepBasicPrinterInfo(item)
                else:
                    printSet = self.getPrinterSetting(item['name'])
                    printThrdList = self.getPrinterMsgThread(item['name'])
                    if not self.checkMsgThreadAvail(item['name']):
                        self.renewMsgID(item['name'])
                        self.startMsgThread(item['name'])
        else:
            logger.error(_("Keine Server Rückmeldung in Methode checkForMsgThreads")) 
            
    def checkServerConfigChange(self, items):
        for thread in self.msgActiveThreads:
            unknownThread = True
            for item in items:
                if item['name'] == thread.name:
                    unknownThread = False
                    break
            if unknownThread:
                logger.info(_("Beende in Methode checkServerConfigChange Thread: %s") % thread.name) 
                for botItem in self.botRequests:
                    if botItem['name'] == thread.name:
                        self.botRequests.remove(botItem)
                        self.removeHandler(botItem) # remove_handler(handler)
                self.stopByMsgThread(thread)

    def checkBotToServerConfig(self, items):
        systemChange = False
        for item in items: 
            itemInSystem = False
            for botPrinter in self.botRequests:
                if botPrinter['name'] == item['name']:
                    itemInSystem = True
                    break
            if not itemInSystem:
                systemChange = True
                printerBuffer = self.getNewPrinter(item['slug'], item['name'])
                self.botRequests.append(printerBuffer)
                self.addHandler(item)
                logger.info(_("Bot Teilnehmer in checkBotToServerConfig hinzugefügt: %s") % item['name'])
        if systemChange:
            data = self.rConfigFile()
            data['data'] = self.botRequests
            wConfigFile(data)
                
    def botData(self):
        msg = printerData("listPrinter")
        if msg != "Error":
            items = msg['data']
            if self.botRequests == []:    
                data = self.rConfigFile()
                if data == "Error":
                    for i in range(0,len(items)):
                        printerBuffer = self.getNewPrinter(items[i]['slug'], items[i]['name'])                     
                        self.botRequests.append(printerBuffer)
                        self.addHandler(items[i])
                        logger.info(_("Teilnehmer in botData hinzugefügt: %s") % items[i]['name'])
                        return
                else:
                    try:
                        telegramDataAvailable = data['data']
                    except:
                        logger.info(_("Konfigurationsdatei in botData enthält keine Telegram Datenablage"))
                        for i in range(0,len(items)):
                            printerBuffer = self.getNewPrinter(items[i]['slug'], items[i]['name'])
                            self.botRequests.append(printerBuffer)
                            self.addHandler(items[i])
                            logger.info(_("Teilnehmer in botData hinzugefügt: %s") % items[i]['name'])
                        return
                
                for i in range(0,len(items)):
                    printerFound = False
                    pData = data['data']
                    for j in range(0,len(pData)):
                        if items[i]['slug'] == pData[j]['printer']:
                            printerFound = True
                            rData = pData[i]
                            printerBuffer = self.getNewPrinter(rData['printer'], 
                                                               rData['name'], 
                                                               rData['telegramHistory'])
                    if not printerFound:
                        printerBuffer = self.getNewPrinter(items[i]['slug'], items[i]['name'])
                    self.botRequests.append(printerBuffer)
                    self.addHandler(items[i])
                    logger.info(_("Teilnehmer in botData hinzugefügt: %s") % items[i]['name'])
                data['data'] = self.botRequests
                self.wConfigFile(data)
            else:
                data = self.rConfigFile()
                if data == "Error":
                    return
                for i in range(0,len(items)):
                    printerFound = False
                    for j in range(0,len(self.botRequests)):
                        if items[i]['slug'] == self.botRequests[j]['printer']:
                            printerFound = True                            
                        if not printerFound:
                            printerBuffer = getNewPrinter(items[i]['slug'], items[i]['name'])
                            self.botRequests.append(printerBuffer)
                            self.addHandler(items[i])
                            logger.info(_("Teilnehmer in botData hinzugefügt: %s") % items[i]['name'])
                data['data'] = self.botRequests
                self.wConfigFile(data)
            loggerWS.info(_("Bot Data angelegt"))
        else:
            loggerWS.error(_("Bot Data Initialisierung fehlgeschlagen"))

    def rConfigFile(self):
        try:
            with open(CFGFILENAME) as json_file:
                data = json.load(json_file)
        except:
            logger.error(_("Konfigurationsdatei nicht gefunden in botData: %s") % CFGFILENAME)
            return "Error"
        return data

    def wConfigFile(self, data):
        try:
            with open(CFGFILENAME, 'w') as outfile:
                json.dump(data, outfile) 
        except:
                logger.error(_("Konfigurationsdatei konnte nicht beschrieben werden"))

    def checkMsgID(self, name):
        for IDs in self.msgIDs:
            if IDs['name'] == name:
                if IDs['RequestNewMessageID']:
                    logger.info(_("checkMsgID: Drucker %s fordert neue MessageID für MessageID an: %s") % (IDs['name'], IDs['messageID']))
                    IDs['messageID'] = 0
                    IDs['RequestNewMessageID'] = False
                return IDs['messageID']
        return 0

    def renewMsgID(self, name):
        for IDs in self.msgIDs:
            if IDs['name'] == name:
                timeDelThread(messageID=IDs['messageID'],delayTimeSelect=1,printer=IDs['name'])
                IDs['RequestNewMessageID'] = True
            return True
        return False

    def renewMsgIDs(self):
        for IDs in self.msgIDs:
            timeDelThread(messageID=IDs['messageID'],delayTimeSelect=1,printer=IDs['name'])
            IDs['RequestNewMessageID'] = True
            
    def updMsgID(self, item, messageID, chatID=CHATID):
        for IDs in self.msgIDs:
            if IDs['name'] == item['name']:
                IDs['messageID'] = messageID
                return
        msgIDInfo = {}
        msgIDInfo['name'] = item['name']
        msgIDInfo['slug'] = item['slug']
        msgIDInfo['messageID'] = messageID
        msgIDInfo['RequestNewMessageID'] = False
        msgIDInfo['chatID'] = chatID
        msgIDInfo['reply_markup'] = None
        msgIDInfo['expanded'] = False
        msgIDInfo['additional_message'] = []
        self.msgIDs.append(msgIDInfo)

    def delMsgID(self, name):
        for IDs in self.msgIDs:
            if IDs['name'] == name:
                timeDelThread(messageID=IDs['messageID'],delayTimeSelect=1,printer=IDs['name'])
                self.msgIDs.remove(IDs)

    def getMsgIDExpanded(self, name):
        for IDs in self.msgIDs:
            if IDs['name'] == name:
                return IDs['expanded']
        return False
               
    def keepBasicPrinterInfo(self, item):
        messageBuffer = "/" + str(item['slug']) + "\n"
        messageBuffer += _("Update: %s um %s") % (arrow.now().format('DD.MM.YYYY'), arrow.now().format('HH:mm:ss') + "\n") 
        if item['online'] == 1 and item['active'] == True:
            messageBuffer += _("Einsatzbereit")
        else:
            messageBuffer += _("Ausgeschaltet")
        self.threadLock.acquire()        
        messageID = self.checkMsgID(item['name'])
        if messageID == 0:
            try:
                feedbackMsg = telegramSendMsg(messageBuffer, self.getMsgReplyMarkup(item['name']), chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
                messageID = feedbackMsg['message_id']
                chatID = feedbackMsg['chat']['id']
                self.updMsgID(item, messageID)
            except:
                loggerWS.error(_("Konnte keepBasicPrinterInfo keine Bot Nachricht senden an %s") % item['name'])
            loggerWS.info(_("keepBasicPrinterInfo: Drucker %s erzeugt neue MessageID: %s") % (item['name'], messageID))    
        else:
            try:
                telegramEditMsg(messageBuffer, self.checkMsgID(item['name']), self.getMsgReplyMarkup(item['name']), chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
            except:
                loggerWS.error(_("Konnte keepBasicPrinterInfo keinen telegramEditMsg senden an %s auf messageID: %s") % (item['name'], self.checkMsgID(item['name'])))
        self.threadLock.release()        
        
    def getMsgReplyMarkup(self, name):
        for IDs in self.msgIDs:
            if IDs['name'] == name:
                return IDs['reply_markup']
            
    def getNames(self):
        return {self.wsThreadSend.getName(), self.wsThreadRec.getName(), self.wsThreadOrderData.getName(), self.wsThreadRestart.getName()}

    def are_alive(self):
        return {self.wsThreadSend.is_alive(), self.wsThreadRec.is_alive(), self.wsThreadOrderData.is_alive(), self.wsThreadRestart.is_alive()}

    def idents(self):
        return {self.wsThreadSend.ident, self.wsThreadRec.ident, self.wsThreadOrderData.ident, self.wsThreadRestart.ident}

    def native_ids(self):
        return {self.wsThreadSend.native_id, self.wsThreadRec.native_id, self.wsThreadOrderData.native_id, self.wsThreadRestart.native_id}

    def encCommand(self, action = "ping", callback_id = -1, printer = "My Printer", data = {}):
        command = {}
        command['action'] = action
        command['data'] = data
        command['printer'] = printer
        command['callback_id'] = callback_id
        command = json.dumps(command)
        
        return command
    
    def getPrinterSetting(self, name):
        for setting in self.botRequests:
            if setting['name'] == name:
                return setting
        for setting in self.botRequests:
            if setting['printer'] == name:
                return setting
        loggerWS.error(_("Printer %s not found in method getPrinterSetting!") % name)
            
    def wsWebsocket(self):
        try:
            websocket = create_connection(self.webserver)
        except:
            loggerWS.error(_("Response to open threading websocket: %s, Unexpected Error: %s") % (self.webserver, sys.exc_info()[0]))
            self.websocket = None
            return "Error"
        self.websocket = websocket
        loggerWS.info(_("Websocket established to: %s") % self.webserver) 
       
        return self.websocket

    def msgPrinter(self, name, messageID, chatID):
        msg = printerData("listPrinter")
        msg2 = printerData("stateList")
        if msg != "Error" and msg2 != "Error":
            listPrinters = msg['data']
            stateLists = msg2['data']
            for printer in listPrinters:
                if printer['name'] == name:
                    state = stateLists[printer['slug']] # state['extruder'], state['heatedBeds']
                    msgF = self.checkFanssStatus(state['fans'])
                    statusC, msgC = self.checkChambersStatus(state['heatedChambers'])
                    statusHB, msgHB = self.checkHeatedBedsStatus(state['heatedBeds'])
                    statusE, msgE = self.checkExtrudersStatus(state['extruder'])
                    if self.getMsgIDExpanded(printer['name']):
                        if statusC and statusHB and statusE:
                            messageBuffer = "/" + str(printer['slug']) + "\n"
                            messageBuffer += _("Update: %s um %s") % (arrow.now().format('DD.MM.YYYY'), arrow.now().format('HH:mm:ss')) + "\n\n"
                            messageBuffer += _("Druck der Datei") + "\n"
                            messageBuffer += "\"" + str(printer['job']) + "\"\n"
                            messageBuffer += _("ist bei %.1f") % printer['done'] + "%\n"
                            messageBuffer += _("Layer: %s/%s bei Z: %.3fmm") % (state['layer'], printer['ofLayer'], state['z']) + "\n"
                            messageBuffer += _("Fertigstellung %s") % getTimeToGo(int(printer['start']),int(printer['printTime'])) + "\n"
                            messageBuffer += _("Druck wurde %s begonnen") % getTimeGone(int(printer['start']))+ "\n"
                            messageBuffer += _("Vorraussichtliches Ende: %s") % arrow.get(int(printer['start']) + int(printer['printTime'])).format('DD.MM.YYYY - HH:mm') + "\n\n"
                            messageBuffer += _("Drucker Status:") + "\n"
                            messageBuffer += _("Druckgeschwindigkeit: %s%% Fluss: %s%%") % (state['speedMultiply'], state['flowMultiply']) + "\n"
                            messageBuffer += msgF
                            if len(state['heatedChambers']) > 0:
                                messageBuffer += msgC
                            if len(state['heatedBeds']) > 0:
                                messageBuffer += msgHB
                            if len(state['extruder']) > 0:
                                messageBuffer += msgE
                        else:
                            messageBuffer = "/" + str(printer['slug']) + "\n"
                            messageBuffer += _("Update: %s um %s") % (arrow.now().format('DD.MM.YYYY'), arrow.now().format('HH:mm:ss')) + "\n\n" 
                            messageBuffer += _("Aufheizvorgang:") + "\n"
                            messageBuffer += msgF
                            if len(state['heatedChambers']) > 0:
                                messageBuffer += msgC
                            if len(state['heatedBeds']) > 0:
                                messageBuffer += msgHB
                            if len(state['extruder']) > 0:
                                messageBuffer += msgE
                    else:
                        messageBuffer = "/" + str(printer['slug']) + "\n"
                        messageBuffer += _("Update: %s um %s") % (arrow.now().format('DD.MM.YYYY'), arrow.now().format('HH:mm:ss')) + "\n" 
                        if statusC and statusHB and statusE:
                            messageBuffer += "\"%s\" - %.1f" % (printer['job'], printer['done']) + "%\n"
                        else:
                            messageBuffer += _("Aufheizvorgang:") + "\n" + msgC + msgHB + msgE
                    self.threadLock.acquire()        
                    messageID = self.checkMsgID(printer['name'])
                    if messageID == 0:
                        try:
                            feedbackMsg = telegramSendMsg(messageBuffer, self.getMsgReplyMarkup(printer['name']),chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
                            messageID = feedbackMsg['message_id']
                            chatID = feedbackMsg['chat']['id']
                            self.updMsgID(printer, messageID)
                        except:
                            loggerWS.error(_("Konnte msgPrinter keine Bot Nachricht senden an %s") % printer['name'])
                        loggerWS.info(_("msgPrinter: Drucker %s erzeugt neue MessageID: %d") % (printer['name'], messageID))
                    else:
                        try:
                            telegramEditMsg(msg=messageBuffer, message_id=messageID, reply_markup=self.getMsgReplyMarkup(printer['name']), chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
                        except:
                            loggerWS.error(_("Konnte msgPrinter keinen telegramEditMsg senden an %s auf messageID: %s") % (printer['name'], messageID))
                    self.threadLock.release()
        else:
            loggerWS.error(_("Konnte msgPrinter nicht ausführen. Keine Daten vom Server für %s") % name)
                
        return messageID, chatID
        
    def checkFanssStatus(self, fans):
        feedbackMsg = ""
        if len(fans) > 0:
            for i in range(0, len(fans)):
                fan = fans[i]
                if fan['on']:
                    fanSpeed = 100 * fan['voltage'] / 255
                    feedbackMsg += _("Lüfter %d: %.0f%%") % (i+1, fanSpeed) + "\n"
                else:
                    feedbackMsg += _("Lüfter %d: Aus") % (i+1) + "\n"
        
        return feedbackMsg

    def checkChambersStatus(self, chambers):
        feedbackMsg = ""
        feedback = True
        if len(chambers) > 0:
            for i in range(0, len(chambers)):
                chamber = chambers[i]
                if chamber['tempRead'] > (chamber['tempSet'] - 10) and chamber['tempRead'] < (chamber['tempSet'] + 10):
                    feedbackMsg += _("Chamber %d: %.1f °C/ %.1f °C\n") % (i+1, chamber['tempRead'], chamber['tempSet'])
                else:
                    feedbackMsg += _("Chamber %d: %.1f °C/ %.1f °C\n") % (i+1, chamber['tempRead'], chamber['tempSet'])
                    feedback = False
        
        return feedback, feedbackMsg

    def checkHeatedBedsStatus(self, heatBeds):
        feedbackMsg = ""
        feedback = True
        if len(heatBeds) > 0:
            for i in range(0, len(heatBeds)):
                heatBed = heatBeds[i]
                if heatBed['tempRead'] > (heatBed['tempSet'] - 10) and heatBed['tempRead'] < (heatBed['tempSet'] + 10):
                    feedbackMsg += _("Heatbed %d: %.1f °C/ %.1f °C\n") % (i+1, heatBed['tempRead'], heatBed['tempSet'])
                else:
                    feedbackMsg += _("Heatbed %d: %.1f °C/ %.1f °C\n") % (i+1, heatBed['tempRead'], heatBed['tempSet'])
                    feedback = False
        
        return feedback, feedbackMsg

    def checkExtrudersStatus(self, extruders):
        feedbackMsg = ""
        feedback = True
        if len(extruders) > 0:
            for i in range(0, len(extruders)):
                extruder = extruders[i]
                if extruder['tempRead'] > (extruder['tempSet'] - 10) and extruder['tempRead'] < (extruder['tempSet'] + 10):
                    feedbackMsg += _("Extruder %d: %.1f °C/ %.1f °C\n") % (i+1, extruder['tempRead'], extruder['tempSet'])
                else:
                    feedbackMsg += _("Extruder %d: %.1f °C/ %.1f °C\n") % (i+1, extruder['tempRead'], extruder['tempSet'])
                    feedback = False
        
        return feedback, feedbackMsg

    def buildPng(self, cam, slug, chatID):
        cam = int(cam.split()[2])
        slug = slug[1:]
        msg = printerData("listPrinter")
        msg2 = printerData("getPrinterConfig", slug)
        if msg == "Error" or msg2 == "Error":
            loggerWS.error(_("Anfragefehler getPrinterConfig in buildPng für Drucker: %s") % str(name))
            return
        listPrinters = msg['data']
        printerSet = self.getPrinterSetting(slug)
        webcam = msg2['data']['webcams'][cam-1]
        pngDir = os.path.join(PNGFILEFOLDER, printerSet['printer'])
        loggerWS.info(_("Png Erstellung startet für %s") % printerSet['name'])
        for eachFileInPath in pathlib.Path(pngDir).glob('*.png'):
            loggerWS.critical(_("Lösche %s") % eachFileInPath)
            eachFileInPath.unlink()
        telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        filePathNamePng = self.get_img(webcam, printerSet['printer'], pngDir)
        if filePathNamePng == "Error":
            return
        loggerWS.info(_("Png Erstellung beendet für %s") % printerSet['name'])
        caption='/%s' % printerSet['printer'] 
        for printerMsg in listPrinters:
            if printerMsg['slug'] == printerSet['printer']:
                if printerMsg['job'] != "none":
                    caption=_('/%s druckt \"%s\" bei %.1f%%') % (printerMsg['slug'],printerMsg['job'],printerMsg['done']) 
                else:
                    if printerMsg['online'] == 1:
                        caption=_('/%s - eingeschaltet') % printerMsg['slug'] 
                    else:
                        caption=_('/%s - ausgeschaltet') % printerMsg['slug'] 
        loggerWS.info(_("Png Caption Erstellung beendet für %s") % printerSet['name'])
        telegramChatAction(action=telegram.ChatAction.UPLOAD_PHOTO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        try:
            telegramSendPic(pic=filePathNamePng, caption=caption, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        except:
            loggerWS.error(_("Sendefehler telegramSendPic in buildGif für Drucker: %s") % printerSet['name'])
        loggerWS.info(_("Png versendet für %s") % printerSet['name'])
        for eachFileInPath in pathlib.Path(pngDir).glob('*.png'):
            eachFileInPath.unlink()
        self.renewMsgIDs()
        

    def get_img(self, webcam, printer, pngDir):
        """
        Get image based on url.
        :return: Image name if everything OK, False otherwise
        """
        try:
            realUrlServer = self.getWebcamStaticUrl(webcam['staticUrl'])
        except:
            loggerWS.error(_("Anfragefehler getWebcamStaticUrl in get_image für Drucker: %s") % printer)
            return "Error"
        
        imageName = printer + ".png"
        try:
            image = requests.get(realUrlServer)
        except OSError:  # Little too wide, but work OK, no additional imports needed. Catch all conection problems
            loggerWS.error(_("Anfragefehler requests in get_image für Drucker: %s") % printer)
            return "Error"
        if image.status_code == 200:  # we could have retrieved error page
            pathlib.Path(pngDir).mkdir(parents=True, exist_ok=True)
            with open(os.path.join(pngDir, imageName), "wb") as f:
                f.write(image.content)
            if webcam['orientation'] != 0:
                img = cv2.imread(os.path.join(pngDir, imageName))
                if webcam['orientation'] == 90:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                elif webcam['orientation'] == 270:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif webcam['orientation'] == 180:
                    img = cv2.rotate(img, cv2.ROTATE_180)
                status = cv2.imwrite(os.path.join(pngDir, imageName),img)
            return os.path.join(pngDir, imageName)
        else:
            loggerWS.error(_("Verzeichnis/Datei konnte nicht in get_image für Drucker erstellt werden: %s") % printer)
            return "Error"

    def buildGif(self, cam, slug, chatID):
        cam = int(cam.split()[2])
        slug = slug[1:]
        msg = printerData("listPrinter")
        msg2 = printerData("getPrinterConfig", slug)
        if msg == "Error" or msg2 == "Error":
            loggerWS.error(_("Anfragefehler getPrinterConfig in buildGif für Drucker: %s") % name)
            return
        listPrinters = msg['data']
        printerSet = self.getPrinterSetting(slug)
        webcam = msg2['data']['webcams'][cam-1]
        pngDir = os.path.join(PNGFILEFOLDER, printerSet['printer'])
        gifDir = os.path.join(GIFFILEFOLDER, printerSet['printer'])
        filePathGif = pathlib.Path(gifDir)
        filePathGif.mkdir(parents=True, exist_ok=True)
        fileNameGif = printerSet['printer'] + ".gif"
        filePathNameGif = filePathGif / fileNameGif
        loggerWS.info(_("Gif Erstellung startet für %s") % printerSet['name'] + "\n")
        for eachFileInPath in pathlib.Path(pngDir).glob('*.png'):
            loggerWS.critical('Lösche %s' % eachFileInPath)
            eachFileInPath.unlink()
        for eachFileInPath in pathlib.Path(filePathGif).glob('*.gif'):
            loggerWS.critical('Lösche %s' % eachFileInPath)
            eachFileInPath.unlink()
        telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        if self.get_gif(webcam, printerSet['printer'], pngDir) == "Error":
            return
        loggerWS.info(_("Png Erstellung beendet für %s") % printerSet['name'])
        telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        try:
            with imageio.get_writer(filePathNameGif, mode='I') as writer:
                for fileName in os.listdir(pngDir):
                    if fileName.endswith('.png'):
                        filePathPng = os.path.join(pngDir, fileName)
                        cv2.imwrite(filePathPng, cv2.resize(cv2.imread(filePathPng), (350, 290), interpolation = cv2.INTER_AREA))
                        writer.append_data(imageio.imread(filePathPng))
        except:
            loggerWS.error(_("Erstellungsfehler imageio.mimsave in buildGif für Drucker: %s") % printerSet['name'])
            return
        for eachFileInPath in pathlib.Path(pngDir).glob('*.png'):
            eachFileInPath.unlink()
        telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO_NOTE, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        try:
            optimize(filePathNameGif.name)
        except TypeError as err:
            loggerWS.error(_("TypeError bei gifsicle in buildGif: %s") % err)
        except:
            loggerWS.error(_("Optimierungsfehler optimize von gifsicle in buildGif für Drucker: %s") % printerSet['name'])
        loggerWS.info(_("Gif Erstellung beendet für %s") % printerSet['name'])
        caption='/%s' % printerSet['printer'] 
        for printerMsg in listPrinters:
            if printerMsg['slug'] == printerSet['printer']:
                if printerMsg['job'] != "none":
                    caption=_('/%s druckt \"%s\" bei %.1f%%') % (printerMsg['slug'],printerMsg['job'],printerMsg['done']) 
                else:
                    if printerMsg['online'] == 1:
                        caption=_('/%s - eingeschaltet') % printerMsg['slug'] 
                    else:
                        caption=_('/%s - ausgeschaltet') % printerMsg['slug'] 
        loggerWS.info(_("Gif Caption Erstellung beendet für %s") % printerSet['name'])
        telegramChatAction(action=telegram.ChatAction.UPLOAD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        try:
            telegramSendAnimation(anim=filePathNameGif, caption=caption, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        except:
            loggerWS.error(_("Sendefehler telegramSendAnimation in buildGif für Drucker: %s") % printerSet['name'])
        loggerWS.info(_("Gif versendet für %s") % printerSet['name'])
        for eachFileInPath in pathlib.Path(filePathGif).glob('*.gif'):
                eachFileInPath.unlink()
        self.renewMsgIDs()

    def get_gif(self, webcam, printer, pngDir):
        """
        Get image based on url.
        :return: Image name if everything OK, False otherwise
        """
        try:
            realUrlServer = self.getWebcamStaticUrl(webcam['staticUrl'])
        except:
            loggerWS.error(_("Anfragefehler getWebcamStaticUrl in get_image für Drucker: %s") % printer)
            return "Error"
        
        for i in range(0,20):
            imageName = printer + str(i)+".png" #'Test.png'# path.split(image_url)[1]
            try:
                image = requests.get(realUrlServer)
            except OSError:  # Little too wide, but work OK, no additional imports needed. Catch all conection problems
                loggerWS.error(_("Anfragefehler requests in get_gif für Drucker: %s") % printer)
                return "Error"
            if image.status_code == 200:  # we could have retrieved error page
                pathlib.Path(pngDir).mkdir(parents=True, exist_ok=True)
                with open(os.path.join(pngDir, imageName), "wb") as f:
                    f.write(image.content)
                if webcam['orientation'] != 0:
                    img = cv2.imread(os.path.join(pngDir, imageName))
                    if webcam['orientation'] == 90:
                        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                    elif webcam['orientation'] == 270:
                        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif webcam['orientation'] == 180:
                        img = cv2.rotate(img, cv2.ROTATE_180)
                    status = cv2.imwrite(os.path.join(pngDir, imageName),img)
                time.sleep(0.25)

    def getWebcamStaticUrl(self, staticUrl):
        # http://192.168.100.84:9000/?action=snapshot
        repetierUrl = urlparse(staticUrl)
        realUrlServer = "http://" + str(RepetierServerIP) + ":" + str(repetierUrl.port) + "/?action=snapshot"
        return realUrlServer
    
    def buildVid(self, cam, slug, chatID):
        # PNGFILEFOLDER = os.getcwd() + '\\pic\\png'
        # GIFFILEFOLDER = os.getcwd() + '\\pic\\gif'
        # VIDFILEFOLDER = os.getcwd() + '\\vid\\'
        cam = int(cam.split()[2])
        slug = slug[1:]
        msg = printerData("listPrinter")
        msg2 = printerData("getPrinterConfig", slug)
        if msg == "Error" or msg2 == "Error":
            loggerWS.error(_("Anfragefehler getPrinterConfig in buildVid für Drucker: %s") % name)
            return
        listPrinters = msg['data']
        printerSet = self.getPrinterSetting(slug)
        webcam = msg2['data']['webcams'][cam-1]
        vidDir = os.path.join(VIDFILEFOLDER, printerSet['printer'])
        loggerWS.info(_("Vid Erstellung startet für %s") % printerSet['name'] + "\n")
        for eachFileInPath in pathlib.Path(vidDir).glob('*.avi'):
            loggerWS.critical(_('removing %s') % eachFileInPath)
            eachFileInPath.unlink()
        telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        filePathNameVid = self.get_Vid(webcam, printerSet['printer'], vidDir)
        if filePathNameVid == "Error":
            return
        loggerWS.info(_("Vid Erstellung beendet für %s") % printerSet['name'])
        telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        caption='/%s' % printerSet['printer'] 
        for printerMsg in listPrinters:
            if printerMsg['slug'] == printerSet['printer']:
                if printerMsg['job'] != "none":
                    caption=_('/%s druckt \"%s\" bei %.1f%%') % (printerMsg['slug'],printerMsg['job'],printerMsg['done']) 
                else:
                    if printerMsg['online'] == 1:
                        caption=_('/%s - eingeschaltet') % printerMsg['slug'] 
                    else:
                        caption=_('/%s - ausgeschaltet') % printerMsg['slug'] 
        loggerWS.info(_("Vid Caption Erstellung beendet für %s") % printerSet['name'])
        telegramChatAction(action=telegram.ChatAction.UPLOAD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        try:
            telegramSendVideo(video=filePathNameVid, caption=caption, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        except:
            loggerWS.error(_("Sendefehler telegramSendPic in buildGif für Drucker: %s") % printerSet['name'])
        loggerWS.info(_("Vid versendet für %s") % printerSet['name'])
        for eachFileInPath in pathlib.Path(vidDir).glob('*.avi'):
                eachFileInPath.unlink()
        self.renewMsgIDs()

        
    def get_Vid(self, webcam, printer, vidDir):
        fps = 24
        width = 320
        height = 270
        videoCodec = cv2.VideoWriter_fourcc(*'XVID')
        try:
            realUrlServer = self.getWebcamDynamicUrl(webcam['dynamicUrl'])
        except:
            loggerWS.error(_("Anfragefehler getWebcamDynamicUrl in get_Vid für Drucker: %s") % printer)
            return "Error"
        
        videoName = printer + ".avi"
        cap = cv2.VideoCapture(realUrlServer)
        ret = cap.set(3, width)
        ret = cap.set(4, height)
        videoFile = os.path.join(vidDir, videoName)
        pathlib.Path(vidDir).mkdir(parents=True, exist_ok=True)
        vidWriter = cv2.VideoWriter(
                                videoFile, 
                                videoCodec, 
                                fps, 
                                (int(cap.get(3)), int(cap.get(4)))
                                )
        vidStart = time.time()
        while cap.isOpened():
            ret, frame = cap.read()
            if webcam['orientation'] != 0:
                if webcam['orientation'] == 90:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                elif webcam['orientation'] == 270:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif webcam['orientation'] == 180:
                    frame = cv2.rotate(frame, cv2.ROTATE_180)
            if ret == True:
                if time.time() - vidStart > 20:
                    break 
                vidWriter.write(frame)
            else:
                loggerWS.error(_("Stream konnte nicht in get_Vid für Drucker gelesen werden: %s") % printer)
                return "Error"
        cap.release()
        return os.path.join(vidDir, videoName)
        
    def getWebcamDynamicUrl(self, dynamicUrl):
        # http://192.168.100.84:9000/?action=stream
        repetierUrl = urlparse(dynamicUrl)
        realUrlServer = "http://" + RepetierServerIP + ":" + str(repetierUrl.port) + "/?action=stream"
        return realUrlServer

    def ThreadSend(self, ws): 
        try:
            result = ws.send(self.sendCommand)
        except:
            loggerWS.error(_("Antwort: %s - Unerwarteter Fehler: %s") % (RepetierServerIP, sys.exc_info()[0]))
            self.wsThreadSend.stop()        
            return "Error"
        loggerWS.debug(_("Thread Send aktiv"))
        
        return None
        
    def ThreadRec(self, ws):
        try:
            resServ = ws.recv()
        except:
            loggerWS.error(_("Antwort unerwarteter Fehler: %s") % sys.exc_info()[0])
            ws.close()
            self.wsThreadRec.stop()        
            return "Error"
        loggerWS.debug(_("Thread Rec aktiv"))
        
        return resServ

    def ThreadHdlOrderData(self):
        startTime = arrow.now()
        self.threadLock.acquire()
        loggerWS.debug(_("Thread lock gestartet"))
        orderDataRaw = self.wsThreadRec.serverData
        self.wsThreadRec.serverData = []
        self.wsThreadSend.serverData = []
        self.threadLock.release()
        loggerWS.debug(_("Thread lock freigegeben"))
        # Wiederholende Ereignisse, die mehrfach in einem Zyklus gemeldet werden, unterdrücken

        if self.blockMultiJobsChangedMsg > 0: 
            self.blockMultiJobsChangedMsg += 1
            if self.blockMultiJobsChangedMsg >= 2:
                self.blockMultiJobsChangedMsg = 0  
        if self.blockprinterListChangedMsg > 0: 
            self.blockprinterListChangedMsg += 1
            if self.blockprinterListChangedMsg >= 2:
                self.blockprinterListChangedMsg = 0  

        for j in range(len(orderDataRaw),0,-1):
            i = j - 1
            try:
                dataSetCompl = json.loads(orderDataRaw[i][0])                
            except:
                loggerWS.error(_("Event - JSON laden fehlgeschlagen: %s") % dataSetCompl)
                continue
            try:
                dataSet = dataSetCompl['data']
            except:
                loggerWS.error(_("Event - Struktur data nicht erreichbar: %s") % dataSetCompl)
                continue
            if len(dataSet) != 0:
                for k in range(0,len(dataSet)):
                    try:
                        eventTyp = dataSet[k]['event']                    
                    except:
                        loggerWS.error(_("Event - Loggen nicht möglich: %s") % dataSetCompl)
                        continue
                    loggerWS.debug("Event: " + str(eventTyp))
                    if eventTyp == "printerListChanged": 
                    # Payload: List of printers like in listPrinters response. / Gets triggered when a printer was added, deleted or modified. 
                    # {'data': [{'active': True, 'job': 'none', 'name': 'Anycubic Mega X', 'online': 0, 'pauseState': 0, 'paused': False, 'slug': 'Anycubic_Mega_X1'}, 
                    # {'active': True, 'analysed': 1, 'done': 1.389607231300929, 'job': 'AI3M_smoking_ashtray1', 'jobid': 4, 'linesSend': 4057, 'name': 'Anycubic i3 Mega S', 
                    # 'ofLayer': 129, 'online': 1, 'pauseState': 0, 'paused': False, 'printStart': 1603146356.477, 'printTime': 12354.11670494031, 'printedTimeComp': 1523.609069987379, 
                    # 'slug': 'Anycubic_i3_Mega_S', 'start': 1603153556, 'totalLines': 291953}], 'event': 'printerListChanged'}
                        if self.blockprinterListChangedMsg == 0:
                            self.blockprinterListChangedMsg += 1
                            messageBuffer = ""
                            for x in range(0, len(dataSet[k]['data'])):
                                if dataSet[k]['data'][x]['active']:
                                    messageBuffer += dataSet[k]['data'][x]['name'] + _(" ist aktiviert ") 
                                    if dataSet[k]['data'][x]['online'] != 0:
                                        messageBuffer += _("und eingeschaltet")
                                        if dataSet[k]['data'][x]['job'] == "none":
                                            messageBuffer += "."
                                        else:
                                            messageBuffer += "." + _(" Druckt: ") + dataSet[k]['data'][x]['job']
                                    else:
                                        messageBuffer += _("und ausgeschaltet.")
                                else:
                                    messageBuffer += dataSet[k]['data'][x]['name'] + _(" ist deaktiviert.")                                         
                                messageBuffer += "\n"
                            timeDelThread(bot = True, 
                                          feedbackMsg = telegramSendMsg(messageBuffer, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN), 
                                          botRequests = self.botRequests)
                            
                    elif eventTyp == "move":
                    # Payload: {"x":1,"y":1,"z":0,"e":67.233,"de":0.023} / When moves are enabled (sendMoves action) you will get a event for every move the printer does. This can be used to provide a live preview of what the printer does.
                        #telegramSendMsg("move" + str(dataSet[k]), ADMIN_IDS[0][0])
                        print(str(dataSet[k]))
                    elif eventTyp == "temp":
                    # Payload: { "O": 0, "S": 0, "T": 24, "id": 1, "t": 1423671195610 } / New temperature entry. O = Output, S = Set temperature, T = Measued temperature, id = Extruder number, t = Timestamp
                        if self.orderDataStorage == []:
                            printerBuffer = {}
                            tempBuffer = {}

                            msg = printerData("listPrinter")
                            if msg != "Error":
                                for i in range(0,len(msg['data'])):
                                    if dataSet[k]['printer']  == msg['data'][i]['slug']:
                                        printerBuffer['name'] = msg['data'][i]['name']
                            else:
                                printerBuffer['name'] = "Unbekannt"
                            printerBuffer['printer'] = dataSet[k]['printer']
                            printerBuffer['data'] = {}
                            printerBuffer['messages'] = []
                            printerBuffer['data']['temp'] = []
                            tempBuffer = dataSet[k]['data']
                            if dataSet[k]['data']['id'] < 1000: # Chamber nummer nicht bekannt, die Auswertung fehlt
                                tempBuffer['name'] = "Hotend E" + str(dataSet[k]['data']['id'])
                            elif dataSet[k]['data']['id'] >= 1000:
                                tempBuffer['name'] = "Heatbed " + str(dataSet[k]['data']['id']-999)
                            printerBuffer['data']['temp'].append(tempBuffer)                            
                            self.orderDataStorage.append(printerBuffer)
                            loggerWS.info(_("Drucker hinzugefügt: %s") % printerBuffer['name'])
                            timeDelThread(bot = True, 
                                             feedbackMsg = telegramSendMsg(printerBuffer['name'] + _(" hinzugefügt"),reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN),
                                             botRequests = self.botRequests)
                        else:
                            printerBuffer = {}
                            printerBuffer['printer'] = dataSet[k]['printer']
                            printerBuffer['data'] = {}
                            printerBuffer['messages'] = []
                            printerBuffer['data']['temp'] = []
                            printerInList = False
                            for printers in self.orderDataStorage:
                                if printers['printer'] == dataSet[k]['printer']:
                                    printerInList = True
                                    tempInList = False
                                    for temps in range(0,len(printers['data']['temp'])):
                                        if printers['data']['temp'][temps]['id'] == dataSet[k]['data']['id']:
                                            tempInList = True
                                            name = printers['data']['temp'][temps]['name']
                                            printers['data']['temp'][temps] = dataSet[k]['data']
                                            printers['data']['temp'][temps]['name'] = name
                                    if not tempInList:
                                        tempBuffer = {}
                                        tempBuffer = dataSet[k]['data']
                                        if dataSet[k]['data']['id'] < 1000: # Chamber nummer nicht bekannt, die Auswertung fehlt
                                            tempBuffer['name'] = "Hotend E" + str(dataSet[k]['data']['id'])
                                        elif dataSet[k]['data']['id'] >= 1000:
                                            tempBuffer['name'] = "Heatbed " + str(dataSet[k]['data']['id']-999)
                                        printerBuffer['data']['temp'].append(tempBuffer)

                            if not printerInList:
                                printerBuffer = {}
                                tempBuffer = {}
                                msg = printerData("listPrinter")
                                if msg != "Error":
                                    for i in range(0,len(msg['data'])):
                                        if dataSet[k]['printer']  == msg['data'][i]['slug']:
                                            printerBuffer['name'] = msg['data'][i]['name']
                                else:
                                    printerBuffer['name'] = _("Unbekannt")
                                printerBuffer['printer'] = dataSet[k]['printer']
                                printerBuffer['data'] = {}
                                printerBuffer['messages'] = []
                                printerBuffer['data']['temp'] = []
                                tempBuffer = dataSet[k]['data'] 
                                if dataSet[k]['data']['id'] < 1000: # Chamber nummer nicht bekannt, die Auswertung fehlt
                                    tempBuffer['name'] = "Hotend E" + str(dataSet[k]['data']['id'])
                                elif dataSet[k]['data']['id'] >= 1000:
                                    tempBuffer['name'] = "Heatbed " + str(dataSet[k]['data']['id']-999)
                                printerBuffer['data']['temp'].append(tempBuffer)                            
                                self.orderDataStorage.append(printerBuffer)
                                loggerWS.info(_("Drucker hinzugefügt: %s") % printerBuffer['name'])
                                timeDelThread(bot = True, 
                                             feedbackMsg = telegramSendMsg(_("%s hinzugefügt") % printerBuffer['name'],reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN),
                                             botRequests = self.botRequests)
                                                        
                    elif eventTyp == "messagesChanged":
                    # Payload: None. / Gets triggered when a new message gets available. That way you do not need to poll for new messages, only once at the connection start.
                    # {'data': {'date': '2020-10-18T21:29:42+02:00', 'id': 5, 'link': '/printer/msg/Anycubic_i3_Mega_S?a=jobfinsihed&id=5', 'msg': 'Print of AI3M_CHTop_100s on printer Anycubic i3 Mega S finished. Send 76664 lines. Printing time: 5:32:40', 'pause': False, 'slug': 'Anycubic_i3_Mega_S'}, 
                    # 'event': 'messagesChanged', 'printer': 'Anycubic_i3_Mega_S'}
                        msg = printerData("messages")
                        if msg != "Error":
                            for printers in self.orderDataStorage:
                                print("Davor: " + str(printers['messages']))
                                if printers['printer'] == dataSet[k]['printer']: 
                                    messageBuffer = ""
                                    for messages in dataSet[k]['data']:
                                        messageBuffer = messages['msg']
                                        printers['messages'].append(messageBuffer)
                                    print("Danach: " + str(printers['messages']))

                    elif eventTyp == "jobsChanged":
                    # Payload: None. / Gets triggered if a printer has a change in it's stored g-file list. {'data': {'slug': 'Anycubic_i3_Mega_S'}, 'event': 'jobsChanged', 'printer': 'Anycubic_i3_Mega_S'}
                        if self.blockMultiJobsChangedMsg == 0:
                            self.blockMultiJobsChangedMsg += 1
                            msg = printerData("listPrinter")
                            for printers in self.orderDataStorage:
                                if printers['printer'] == dataSet[k]['printer']:
                                    for x in range(0, len(msg['data'])):
                                        if msg['data'][x]['slug'] == dataSet[k]['printer']: 
                                            messageBuffer = _("Druckauftrag %s wurde geändert") % printers['name']                                     
                                    printers['messages'].append(messageBuffer)

                    elif eventTyp == "jobFinished":
                    # Payload: {start:unixTime,duration:seconds,end:unixTime,lines:linesOfJob} / Gets send after a normal job has finished. 
                    # # {'duration': 5507, 'end': 5507, 'lines': 117373, 'start': 1603207724}, 'event': 'jobFinished', 'printer': 'Anycubic_Mega_X1'}
                        for printers in self.orderDataStorage:
                            if printers['printer'] == dataSet[k]['printer']: 
                                present = arrow.now()
                                future = present.shift(seconds=dataSet[k]['data']['duration'])                                
                                messageBuffer = _("%s hat nach %s den Druck beendet.") % (printers['name'], future.humanize(present,locale='de', only_distance=True, granularity=["day","hour", "minute","second"]))
                                printers['messages'].append(messageBuffer)

                    elif eventTyp == "jobKilled":
                    # Payload: {start:unixTime,duration:seconds,end:unixTime,lines:linesOfJob} / Gets send after a normal job has been killed.
                        msg = printerData("listPrinter")
                        for printers in self.orderDataStorage:
                            if printers['printer'] == dataSet[k]['printer']:
                                for x in range(0, len(msg['data'])):
                                    if msg['data'][x]['slug'] == dataSet[k]['printer']:
                                        print(msg['data'][x])
                                        present = arrow.now()
                                        past = present.shift(seconds=dataSet[k]['data']['duration'])                                          
                                        messageBuffer = _("Druck von %s wurde nach %s abgebrochen") % (printers['name'], past.humanize(present,locale='de', only_distance=True, granularity=["minute","second"])) 
                                printers['messages'].append(messageBuffer)
                    elif eventTyp == "jobStarted":
                    # Payload: {start:unixTime} / Gets send after a normal job has been started. {'data': {'start': 1603036621}, 'event': 'jobStarted', 'printer': 'Anycubic_i3_Mega_S'}
                        msg = printerData("listPrinter")
                        for printers in self.orderDataStorage:
                            if printers['printer'] == dataSet[k]['printer']:
                                jobTitle = ""
                                for x in range(0, len(msg['data'])):
                                    if msg['data'][x]['slug'] == dataSet[k]['printer']: 
                                        jobTitle = msg['data'][x]['job']
                                        messageBuffer = _("%s hat um %s den Druck %s gestartet und wird vorraussichtlich am %s fertig sein.") % (printers['name'], 
                                                                                     arrow.get(int(msg['data'][x]['start'])).format('DD.MM.YYYY - HH:mm'),
                                                                                     jobTitle,
                                                                                     arrow.get(int(msg['data'][x]['start']) + int(msg['data'][x]['printTime'])).format('DD.MM.YYYY - HH:mm')
                                                                                     ) 
                                printers['messages'].append(messageBuffer)
                        
                    elif eventTyp == "printqueueChanged":
                    # Payload: None. / Gets triggered if a printer has a change in it's list of waiting prints. {'data': {'slug': 'Anycubic_i3_Mega_S'}, 'event': 'printqueueChanged', 'printer': 'Anycubic_i3_Mega_S'}
                        for printers in self.orderDataStorage:
                            if printers['printer'] == dataSet[k]['printer']:
                                messageBuffer = _("Druckerwarteschlange %s wurde geändert") % printers['name']                                     
                                printers['messages'].append(messageBuffer)
                    elif eventTyp == "state":
                    # Payload: State data for one printer. / Gets triggered when a state changes.
                    # {'data': {'activeExtruder': 0, 'debugLevel': 6, 'doorOpen': False, 
                    # 'extruder': [{'error': 0, 'output': 0, 'tempRead': 20.39999961853027, 'tempSet': 0.0}], 
                    # 'fans': [{'on': False, 'voltage': 0}], 'filterFan': False, 'firmware': 'Marlin', 'firmwareURL': '', 
                    # 'flowMultiply': 100, 'hasXHome': False, 'hasYHome': False, 'hasZHome': False, 
                    # 'heatedBeds': [{'error': 0, 'output': 0, 'tempRead': 19.79999923706055, 'tempSet': 0.0}], 
                    # 'heatedChambers': [], 'layer': 0, 'lights': 0, 'numExtruder': 1, 'powerOn': False, 'rec': False, 'sdcardMounted': True, 'shutdownAfterPrint': False, 
                    # 'speedMultiply': 100, 'volumetric': False, 'x': 0.0, 'y': 0.0, 'z': 0.0}, 'event': 'state', 'printer': 'Anycubic_i3_Mega_S'}
                        for printers in self.orderDataStorage:
                            if printers['printer'] == dataSet[k]['printer']:
                                messageBuffer = _("Drucker Einstellung %s Fluss: %d%% Druckgeschwindigkeit: %d%%") % (printers['name'],
                                                                                                                     dataSet[k]['data']['flowMultiply'],
                                                                                                                     dataSet[k]['data']['speedMultiply'])
                                printers['messages'].append(messageBuffer)
                    elif eventTyp == "config":
                    # Payload: Config data for one printer. / Gets triggered when a configuration changes. {'data': {'connection': {'connectionMethod': 0, 'continueAfterFastReconnect': True, 
                    # 'ip': {'address': '', 'port': 23}, 'lcdTimeMode': 4, 'password': '', 'pipe': {'file': ''}, 'powerOffIdleMinutes': 0, 'powerOffMaxTemperature': 50, 'resetScript': '', 
                    # 'serial': {'baudrate': 250000, 'communicationTimeout': 6.0, 'connectionDelay': 0, 'device': '/dev/serial/by-id/usb-marlinfw.org_Marlin_USB_Device_08FFD018AF4A09025D5E80FBF50020C0-if00', 'dtr': 0, 
                    # 'inputBufferSize': 127, 'malyanHack': False, 'pingPong': False, 'rts': 0, 'usbreset': 0, 'visibleWithoutRunning': False}}, 
                    # 'extruders': [{'acceleration': 30.0, 'alias': '', 'changeFastDistance': 20.0, 'changeSlowDistance': 20.0, 'cooldownPerSecond': 0.5, 'eJerk': 30.0, 'extrudeSpeed': 2.0, 'filamentDiameter': 1.75, 
                    # 'heatupPerSecond': 2.0, 'lastTemp': 205, 'maxSpeed': 30.0, 'maxTemp': 260, 'num': 0, 'offset': 0, 'offsetX': 0.0, 'offsetY': 0.0, 'retractSpeed': 30.0, 'supportTemperature': True, 
                    # 'tempMaster': 0, 'temperatures': [{'name': 'ABS 245', 'temp': 245}, {'name': 'PLA 210', 'temp': 210}, {'name': 'PLA 195', 'temp': 195}], 
                    # 'toolDiameter': 0.4, 'toolType': 0}], 'general': {'active': True, 'defaultVolumetric': False, 'doorHandling': 1, 'eepromType': 'marlin', 'firmwareName': 'Marlin', 
                    # 'heatedBed': True, 'logHistory': True, 'model': '', 'name': 'Anycubic i3 Mega S', 'numFans': 1, 'pauseHandling': 0, 'pauseSeconds': 120, 'printerVariant': 'cartesian', 'sdcard': False, 
                    # 'slug': 'Anycubic_i3_Mega_S', 'softwarePower': True, 'tempUpdateEvery': 1, 'useModelFromSlug': '', 'useOwnModelRepository': True}, 
                    # 'heatedBeds': [{'alias': '', 'cooldownPerSecond': 0.1, 'heatupPerSecond': 0.1, 'lastTemp': 80, 'maxTemp': 110, 'offset': 0, 'temperatures': []}], 
                    # 'heatedChambers': [], 'movement': {'G10Distance': 3.0, 'G10LongDistance': 50.0, 'G10Speed': 50.0, 'G10ZLift': 0.0, 'G11ExtraDistance': 0.0, 
                    # 'G11ExtraLongDistance': 0.0, 'G11Speed': 50.0, 'allEndstops': True, 'defaultAcceleration': 10000.0, 'defaultRetractAcceleration': 4000.0, 
                    # 'defaultTravelAcceleration': 10000.0, 'invertX': False, 'invertY': False, 'invertZ': False, 'maxXYSpeed': 500.0, 'maxZSpeed': 8.0, 'movebuffer': 16, 'timeMultiplier': 1.0, 
                    # 'xEndstop': True, 'xHome': 0.0, 'xMax': 200.0, 'xMin': 0.0, 'xyJerk': 20.0, 'xyPrintAcceleration': 2000.0, 'xySpeed': 100.0, 
                    # 'xyTravelAcceleration': 2000.0, 'yEndstop': True, 'yHome': 0.0, 'yMax': 200.0, 'yMin': 0.0, 'zEndstop': True, 'zHome': 0.0, 'zJerk': 0.3, 'zMax': 210.0, 'zMin': 0.0, 
                    # 'zPrintAcceleration': 60.0, 'zSpeed': 2.0, 'zTravelAcceleration': 60.0}, 'properties': {}, 'quickCommands': [{'command': 'G29\nM500', 'name': 'Auto Bed Leveling'}, 
                    # {'command': 'G28 X0 Y0', 'name': 'Home XY'}, {'command': 'G28\nG90\nG1 Z10 F4000\nG1 X100 Z150 F4000\nM84', 'name': 'Head Works High'}], 
                    # 'recover': {'delayBeforeReconnect': 30, 'enabled': False, 'extraZOnFirmwareDetect': 0.0, 'firmwarePowerlossSignal': '', 'maxTimeForAutocontinue': 300, 'procedure': 'G28 X0 Y0', 
                    # 'reactivateBedOnConnect': True, 'replayExtruderSwitches': False, 'runOnConnect': 'G28 X0 Y0'}, 'responseEvents': [], 'shape': {'basicShape': {'color': '#dddddd', 'radius': 100, 'shape': 'rectangle', 
                    # 'x': 0, 'xMax': 225.0, 'xMin': 0.0, 'y': 0, 'yMax': 220.0, 'yMin': 0.0}, 'gridColor': '#454545', 'gridSpacing': 10.0, 'marker': []}, 
                    # 'webcams': [{'dynamicUrl': 'http://127.0.0.1:8081/?action=stream', 'forceSnapshotPosition': False, 'method': 3, 'orientation': 0, 'pos': 0, 'reloadInterval': 3.0, 'snapshotDelay': 800, 'snapshotX': 100.0, 
                    # 'snapshotY': 200.0, 'staticUrl': 'http://127.0.0.1:8081/?action=snapshot', 'timelapseBitrate': 1000, 'timelapseFramerate': 30, 'timelapseHeight': 0.1, 'timelapseInterval': 20.0, 'timelapseLayer': 1, 
                    # 'timelapseMethod': 1, 'timelapseSelected': 2}]}, 'event': 'config', 'printer': 'Anycubic_i3_Mega_S'}
                        timeDelThread(bot = True, 
                                          feedbackMsg = telegramSendMsg("Drucker konfig",reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN), 
                                          botRequests = self.botRequests)
                    elif eventTyp == "settingChanged":
                    # Payload: List of new settings / Gets triggered when a global setting variable got changed.
                        timeDelThread(bot = True, 
                                          feedbackMsg = telegramSendMsg("Server setting" + str(dataSet[k]),reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN), 
                                          botRequests = self.botRequests)
                    elif eventTyp == "printerSettingChanged":
                    # Payload: {key:"key",value:"new value"} / Gets triggered everytime a printer setting gets changed.
                        timeDelThread(bot = True, 
                                          feedbackMsg = telegramSendMsg("Drucker setting" + str(dataSet[k]),reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN), 
                                          botRequests = self.botRequests)
                    elif eventTyp == "prepareJob":
                    # Payload: none / Gets triggered if a model gets copied to job directory. Since feedback is normally instant and large files can take some time this allows giving some feedback.
                    # {'data': {}, 'event': 'prepareJob', 'printer': 'Anycubic_i3_Mega_S'}
                        msg = printerData("listPrinter")
                        for printers in self.orderDataStorage:
                            if printers['printer'] == dataSet[k]['printer']:
                                for x in range(0, len(msg['data'])):
                                    if msg['data'][x]['slug'] == dataSet[k]['printer']: 
                                        messageBuffer = _("Druckauftrag für %s wird bearbeitet") % printers['name']                                     
                                printers['messages'].append(messageBuffer)                        
                    elif eventTyp == "prepareJobFinished":
                    # Payload: none / Gets triggered at the end of copy model to job. Used to hide messages from prepareJob. 
                    # {'data': {}, 'event': 'prepareJobFinished', 'printer': 'Anycubic_i3_Mega_S'}
                        msg = printerData("listPrinter")
                        for printers in self.orderDataStorage:
                            if printers['printer'] == dataSet[k]['printer']:
                                for x in range(0, len(msg['data'])):
                                    if msg['data'][x]['slug'] == dataSet[k]['printer']: 
                                        messageBuffer = _("Druckauftragsbearbeitung für %s wurde fertiggestellt") % printers['name']                                     
                                printers['messages'].append(messageBuffer)
                    elif eventTyp == "changeFilamentRequested":
                    # Payload: none / Firmware requested a filament change on server side.
                        timeDelThread(bot = True, 
                                          feedbackMsg = telegramSendMsg("Drucker Filament Ende" + str(dataSet[k]),reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN), 
                                          botRequests = self.botRequests)
        for printers in self.orderDataStorage:
            messageBuffer = ""
            for x in range(0, len(printers['messages'])):
                messageBuffer += "[" + str(x+1) + "]: " + printers['messages'][x] + "\n"
            if messageBuffer != "":
                loggerWS.info(_("Drucker %s hat %s versendet") % (printers['name'], messageBuffer))
                timeDelThread(bot = True, 
                            feedbackMsg = telegramSendMsg(messageBuffer,reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN),
                            botRequests = self.botRequests)
            printers['messages'] = []
        
        botThreads.checkForMsgThreads()
        stopTime = arrow.now() 
        runTime = stopTime - startTime
        loggerWS.debug(_("Order Storage Runtime: %ssek.") % runTime)
                
    def ThreadHdlRestart(self):
        loggerWS.debug(_("Threads Alive:\nwsThreadSend: %s, wsThreadRec: %s, wswsThreadOrderData: %s, wsThreadRestart: %s, Restarts Websocket/Send/Receive: %d, Restarts Order Data: %d") % (self.wsThreadSend.is_alive(), 
                                                                                self.wsThreadRec.is_alive(),
                                                                                self.wsThreadOrderData.is_alive(),
                                                                                self.wsThreadRestart.is_alive(),
                                                                                self.restartWsSR,
                                                                                self.restartOD
                                                                                )
                       )
        if not self.wsThreadSend.is_alive() and not self.wsThreadRec.is_alive():
            if self.restartWsSR >= 100000:
                loggerWS.info(_("wsThreadSend und wsThreadRec restart Zähler zurückgesetzt"))
                self.restartWsSR = 0
            self.restartWsSR += 1
            if self.wsWebsocket() == 'Error':
                return 'Error'
            self.wsThreadSend = wsThread(interval=self.intervalSend, execute=self.ThreadSend, name="Repetier-Server-Send")
            self.wsThreadRec = wsThread(interval=self.intervalRec, execute=self.ThreadRec, name="Repetier-Server-Receive")        
            self.wsThreadSend.websocket = self.websocket
            self.wsThreadRec.websocket = self.websocket
            self.wsThreadSend.start()
            self.wsThreadRec.start()
            loggerWS.info(_("Websocket established to: %s") % self.webserver)
            loggerWS.info(_("wsThreadSend und wsThreadRec nachgestartet. Zähler: %d") % self.restartWsSR)

        if not self.wsThreadOrderData.is_alive():
            if self.restartOD >= 100000:
                loggerWS.info(_("wsThreadOrderData restart Zähler zurückgesetzt"))
                self.restartOD = 0
            self.restartOD += 1
            self.wsThreadOrderData = hdlThread(interval=self.intervalOrder, execute=self.ThreadHdlOrderData, name="Repetier-Server-Order-Data")
            self.wsThreadOrderData.start()
            loggerWS.info(_("wsThreadOrderData nachgestartet. Zähler: %s") % self.restartOD)
        loggerWS.debug(_("Auflistung aller aktiven Threads. Zähler: %d") % threading.active_count())
        listThreads = threading.enumerate()
        for threads in listThreads:
            loggerWS.debug(_("Thread: %s") % threads)

### Hauptcode
if __name__ == "__main__":
    threading.current_thread().name = FILENAME_NO_EXTENSION
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    logger = setup_logger("Main Thread",formatter,logging.INFO,LOGFILENAME)
    loggerWS = setup_logger("WS Thread",formatter,logging.INFO,LOGFILENAMEWS)

    changeLang(None)
    presLan.install()
    _ = presLan.gettext

    logger.info(_("########### Repetier-Server Bot ###########"))
    logger.info(_("Software Version: %s") % SW_VERSION)
    logger.info(_("Thread Name: %s") % threading.current_thread().getName())
    logger.info(_("########### Geräte and Python Information ###########"))
    logger.info(_("Python Version: %s") % platform.python_version())
    logger.info(_("OS: %s") % platform.system())
    logger.info(_("OS Version: %s") % platform.platform())
    username = getpass.getuser()
    logger.info(_("Active User: %s") % username + "\n")

    # Import Konfigurationsdatei
    impConfig()
    presLan.install()
    _ = presLan.gettext

    # Bot
    updater = Updater(MY_TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Websocket - Repetier-Server Testumgebung
    botThreads = wsThreadHdl(dp)
    botThreads.start()
    
    dp.add_handler(CommandHandler('reset', resetMsgs))
    
    dp.add_error_handler(error_callback) 
    
    updater.start_polling()
    updater.idle()

    # Programm wird beendet
    botThreads.stop()
    numActiveThread = threading.active_count()
    numActiveThreadbefore = numActiveThread - 1
    while threading.active_count() != 1:
        time.sleep(1)
        numActiveThread = threading.active_count()
        if numActiveThread != numActiveThreadbefore:
            logger.info(_("Python Programm wurde beendet. Aktive Threads: %d/ %s") % (threading.active_count(), threading.enumerate()))
            numActiveThreadbefore = numActiveThread
    botThreads.delPrinterMsg()
    telegramSendMsg(msg=_("Bot geht Offline"), chat_id=CHATID,token=MY_TELEGRAM_TOKEN) 
    sys.exit()



