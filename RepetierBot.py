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
import imageio
from pygifsicle import optimize #pip install pygifsicle + https://eternallybored.org/misc/gifsicle/
import cv2
import telegram
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
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

SW_VERSION = "1.1.0" 
CFG_VERSION = "V1.1"
EX_DEBUG = FALSE

LANGUAGE = "de"

# Repetier-Server
RepetierServerIP = ""
RepetierServerPort = ""
RepetierServerWebcamIP = ""
MY_REPETIER_SERVER_API_KEY = ""
MessCnt = 0

# Bot Parameters
MY_TELEGRAM_TOKEN = ""
CHATID = ""
Printer = 1

# Thread cycle time in seconds

THRDSLOW = 10
THRDSTANDBY = 5
THRDIDLE = 2
THRDACTIVE = 1
THRDNOW = 0

THRDSEND = 2
THRDRECEIVE = 0.2
THRDORDERDATA = 1
THRDBOTCOM = 1
THRDMANAGER = 1
THRDMODELMAN = 2
THRDRESTART = 10

# Bot Handler communication levels
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN = range(10)
ELEVEN, TWELVE, THIRTEEN, FOURTEEN, FIFTEEN, SIXTEEN, SEVENTEEN, EIGHTTEEN, NINETEEN, TWENTY = range(10,20)
TWENTYONE, TWENTYTWO, TWENTYTHREE, TWENTYFOUR, TWENTYFIVE, TWENTYSIX, TWENTYSEVEN, TWENTYEIGHT, TWENTYNINE, THIRTY = range(20,30)

# Check platform
checkPlatform = platform.platform()

# Create Logfile in sub folder of program
formatter=u'(%(threadName)-10s) - %(asctime)s - %(name)s - %(levelname)s - %(message)s'

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
LOGFILECONFIG = os.path.join(LOGFILEFOLDER, 'log.conf')

# Configuration and external Data

## Configuration file
FILENAME_FILE_NO_EXT_CFG = FILENAME_NO_EXTENSION
CFGFILENAME =  os.path.join(os.getcwd(), FILENAME_FILE_NO_EXT_CFG + '.json')

## Video & Gifs & Pictures & Model Pictures & Fonts
PNGFILEFOLDER = os.path.join(os.getcwd(), 'pic', 'png')
GIFFILEFOLDER = os.path.join(os.getcwd(), 'pic', 'gif') 
VIDFILEFOLDER = os.path.join(os.getcwd(), 'vid') 
MODELFILEFOLDER = os.path.join(os.getcwd(), 'mod')
FONTSFILEFOLDER = os.path.join(os.getcwd(), 'fonts')

fontSmall = ImageFont.truetype(os.path.join(FONTSFILEFOLDER, 'NCS Rogueland Slab Bold.ttf'), 16)
fontMedium = ImageFont.truetype(os.path.join(FONTSFILEFOLDER, 'NCS Rogueland Slab Bold.ttf'), 34)
### Functions

# Program datasets inits and updates

def getNewPrinterConfig(slug = "NA", name = "NA"): # Printer dataset for the bot
    printerConfig = {}
    printerConfig['slug'] = slug
    printerConfig['name'] = name        
    printerConfig['extrCoolTemp'] = 40
    printerConfig['extrCoolTempExtComm'] = None
    printerConfig['heatbCoolTemp'] = 40
    printerConfig['heatbCoolTempExtComm'] = None
    printerConfig['delayTimeAfterPrintPic'] = 0 # seconds
    printerConfig['AfterPrintPicCamSelect'] = None
    printerConfig['zHeightPrintPic'] = 1.0
    printerConfig['zHeightPrintPicCamSelect'] = None
    printerConfig['timeBasedPrintPic'] = 0 # minutes
    printerConfig['timeBasedPrintPicCamSelect'] = None
    return printerConfig

def getServerConfig(): # Program configuration dataset for the bot, including initialization for update reason
    mainConfig = {}
    mainConfig['LANGUAGE'] = "en"
    mainConfig['MY_REPETIER_SERVER_API_KEY'] = ""
    mainConfig['RepetierServerIP'] = ""
    mainConfig['RepetierServerPort'] = ""
    mainConfig['RepetierServerWebcamIP'] = ""
    mainConfig['MY_TELEGRAM_ID'] = ""
    mainConfig['MY_TELEGRAM_TOKEN'] = ""
    return mainConfig

# Language Management

def changeLang(langSel = None):
    global presLan
    _ = presLan.gettext
    langPath = os.path.join(os.getcwd(), 'locale')
    logger.info("Language file folder: %s" % langPath)
    if langSel == None:
        if sys.platform.startswith('win'):
            if os.getenv('LANG') is None:
                lang, enc = locale.getdefaultlocale()
                logger.info("Language OS: %s/%s" % locale.getdefaultlocale())
                os.environ['LANG'] = lang
                langSel = lang
    else:
        os.environ['LANG'] = '%s' % langSel
    if gettext.find('RepetierBot', langPath) == None:
        os.environ['LANG'] = 'en'
        logger.info("Changed to alternative language english")
    else:
        logger.info("Changed language to \"%s\"" % langSel)
    presLan = gettext.translation('RepetierBot', './locale')
    logger.debug("Language file information: %s" % presLan._info)
    presLan.install()
    _ = presLan.gettext
    
# Logger setup

def setup_logger(name, formatter, level, log_file):
    """To setup as many loggers as you want"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fileHdl = logging.handlers.TimedRotatingFileHandler(log_file, 
                                                        when="midnight", 
                                                        interval=1,
                                                        backupCount=7,
                                                        encoding = "UTF-8")
    fileHdl.setLevel(logging.INFO)
    fileHdl.setFormatter(logging.Formatter(formatter))
    fileHdl.suffix = "%Y%m%d"
    #fileHdl.extMatch = re.compile(r"^\d{8}$")
    logger.addHandler(fileHdl)
    if EX_DEBUG == True:
        strHdl = logging.StreamHandler()
        strHdl.setLevel(level)
        strHdl.setFormatter(logging.Formatter(formatter))
        logger.addHandler(strHdl)
    logger.info("Logger: %s was activated in debug mode (%s). Level: %s" % (name, EX_DEBUG, level))
    
    return logger

# Check configuration file and if entries missing or updates required, update dataset

def checkFileImport(data):
    configCheckFileVersion = CFG_VERSION
    configCheckServerData = getServerConfig()
    configCheckPrinterData = getNewPrinterConfig()
    try:
        if data['version']['CFG_VERSION'] != CFG_VERSION:
            logger.critical('Config file (JSON) upgrade file from version \"%s\" to version \"%s\"' % (data['version']['CFG_VERSION'], CFG_VERSION))
            data['version']['CFG_VERSION'] = CFG_VERSION
        else:
            logger.debug('Config file (JSON) version: %s' % (CFG_VERSION))
    except:
        logger.critical('Config file (JSON) version: loaded standard content \"%s\"' % (CFG_VERSION))
        data['version']['CFG_VERSION'] = CFG_VERSION
    for posLabel, posData in configCheckServerData.items():
        try:
            dataLabelValid = data['server'][posLabel]
            logger.debug('Config file (JSON) entry: %s with content: %s' % (posLabel, data['server'][posLabel]))
        except:
            logger.critical('Config file (JSON) entry: %s loaded standard content \"%s\"' % (posLabel, configCheckServerData[posLabel]))
            data['server'][posLabel] = configCheckServerData[posLabel]  
    try:
        dataLabelValid = data['printers']  
        logger.debug('Config file (JSON) printers root available')
    except:
        data['printers'] = []
        logger.critical('Config file (JSON) printers root implemented')
    for i in range(0,len(data['printers'])):
        for posPrinterLabel, posPrinterData in configCheckPrinterData.items():
            try:
                dataLabelValid = data['printers'][i][posPrinterLabel]
                logger.debug('Config file (JSON) entry: %s with content: %s' % (posPrinterLabel, data['printers'][i][posPrinterLabel]))
            except:
                logger.critical('Config file (JSON) entry: %s loaded standard content \"%s\"' % (posPrinterLabel, configCheckPrinterData[posPrinterLabel]))
                data['printers'][i][posPrinterLabel] = configCheckPrinterData[posPrinterLabel]
    return data

# Read and check configuration file

def impConfig():
    global LANGUAGE,MY_REPETIER_SERVER_API_KEY,RepetierServerIP
    global RepetierServerPort,MY_TELEGRAM_TOKEN,CHATID
    global RepetierServerWebcamIP
    global LOGFILENAME,LOGFILENAMEWS,PNGFILEFOLDER,GIFFILEFOLDER,VIDFILEFOLDER
    global presLan
    try:
        with open(CFGFILENAME) as json_file:
            data = json.load(json_file)
    except:
        logger.error("Configuration file not found - impConfig - : %s. Did you rename the RepetierBot.json.sample?" % CFGFILENAME)
        sys.exit()
    try:
        if data['gui']['testSuccess'] == True:
            logger.info("Repetier Server setup was done before") 
        else:
            logger.critical("Please do Repetier Server setup before running this program!!!")
    except:
        logger.error("Configuration file does not contain gui/testSuccess element")
    data = checkFileImport(data)
    try:
        if data['version']['CFG_VERSION'] == CFG_VERSION:
            logger.info("Configuration file matches: %s" % CFG_VERSION)
        else:
            logger.error("Configuration file version conflict: %s, instead of: %s" % (data['version']['CFG_VERSION'], CFG_VERSION))
    except:
        logger.error("Configuration file does not contain CFG_VERSION element")
        sys.exit()
    serverData = data['server']
    try:
        LANGUAGE = serverData['LANGUAGE']
        logger.info("Repetier Server language: %s" % LANGUAGE)        
    except:
        logger.error("Configuration file does not contain LANGUAGE element")
        sys.exit()
    if LANGUAGE != "":
        changeLang(LANGUAGE)
    try:
        MY_REPETIER_SERVER_API_KEY = serverData['MY_REPETIER_SERVER_API_KEY']
        logger.info("API Key Repetier Server: %s" % MY_REPETIER_SERVER_API_KEY)        
    except:
        logger.error("Configuration file does not contain MY_REPETIER_SERVER_API_KEY element")
        sys.exit()
    try:
        RepetierServerIP = serverData['RepetierServerIP']
        logger.info("Repetier Server IP: %s" % RepetierServerIP)        
    except:
        logger.error("Configuration file does not contain RepetierServerIP element")
        sys.exit()
    try:
        RepetierServerPort = serverData['RepetierServerPort']
        logger.info("Repetier Server Port: %s" % RepetierServerPort)        
    except:
        logger.error("Configuration file does not contain RepetierServerPort element")
        sys.exit()
    try:
        RepetierServerWebcamIP = serverData['RepetierServerWebcamIP']
        logger.info("Repetier Server Webcam IP: %s" % RepetierServerWebcamIP)        
    except:
        logger.error("Configuration file does not contain RepetierServerWebcamIP element")
        sys.exit()
    if RepetierServerWebcamIP == "":
        RepetierServerWebcamIP = RepetierServerIP
    data['server']['RepetierServerWebcamIP'] = RepetierServerWebcamIP
    try:
        MY_TELEGRAM_TOKEN = serverData['MY_TELEGRAM_TOKEN']
        logger.info("Telegram Token: %s" % MY_TELEGRAM_TOKEN)        
    except:
        logger.error("Configuration file does not contain MY_TELEGRAM_TOKEN element")
        sys.exit() 
    try:            
        CHATID = serverData['MY_TELEGRAM_ID'] 
        logger.info("Administrator Telegram ID: %s" % CHATID)        
    except:
        logger.error("Configuration file does not contain MY_TELEGRAM_ID element")
        sys.exit()
    try:
        with open(CFGFILENAME, 'w') as outfile:
            json.dump(data, outfile) 
    except:
            logger.error("Configuration file could not be saved")

    logger.info("Configuration file successfull imported: %s" % CFGFILENAME)
    return data 
    
# Telegram main external functions

def telegramSendMsg(msg, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN, parse_mode=telegram.ParseMode.HTML):
    bot = telegram.Bot(token=token)
    return bot.sendMessage(chat_id=chat_id, 
                           text=msg,
                           reply_markup=reply_markup,
                           parse_mode=parse_mode)

def telegramSendPic(pic, caption, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN, parse_mode=telegram.ParseMode.HTML):
    bot = telegram.Bot(token=token)
    return bot.send_photo(chat_id=chat_id, 
                          photo=open(pic, 'rb'), # .encode('utf-8')
                          timeout=100,
                          caption=caption,
                          reply_markup=reply_markup,
                          parse_mode=parse_mode)

def telegramSendAnimation(anim, caption, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN, parse_mode=telegram.ParseMode.HTML):
    bot = telegram.Bot(token=token)
    return bot.send_animation(chat_id=chat_id, 
                          animation=open(anim, 'rb'), 
                          timeout=100,
                          caption=caption,
                          reply_markup=reply_markup,
                          parse_mode=parse_mode)

def telegramSendVideo(video, caption, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN, parse_mode=telegram.ParseMode.HTML):
    bot = telegram.Bot(token=token)
    return bot.send_video(chat_id=chat_id,
                          video=open(video, 'rb'), 
                          timeout=100, 
                          supports_streaming=True,
                          caption=caption,
                          reply_markup=reply_markup,
                          parse_mode=parse_mode)

def telegramSendDocument(file, caption, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN, parse_mode=telegram.ParseMode.HTML):
    bot = telegram.Bot(token=token)
    return bot.sendDocument(chat_id=chat_id,
                            document=open(file, 'rb'), 
                            timeout=100, 
                            caption=caption,
                            reply_markup=reply_markup,
                            parse_mode=parse_mode)

def telegramEditMsg(msg, message_id, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN, parse_mode=telegram.ParseMode.HTML):
    bot = telegram.Bot(token=token)
    return bot.edit_message_text(chat_id=chat_id, 
                                  message_id=message_id,
                                  text=msg,
                                  reply_markup=reply_markup,
                                  parse_mode=parse_mode)

def telegramEditCapt(caption, message_id, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN, parse_mode=telegram.ParseMode.HTML):
    bot = telegram.Bot(token=token)
    return bot.edit_message_caption(chat_id=chat_id, 
                                    message_id=message_id,
                                    caption=caption,
                                    reply_markup=reply_markup,
                                    parse_mode=parse_mode)

def telegramEditReplyMarkup(message_id, reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN):
    bot = telegram.Bot(token=token)
    return bot.edit_message_reply_markup(chat_id=chat_id, 
                                        message_id=message_id,
                                        reply_markup=reply_markup,
                                        timeout=60)

def telegramDelMsg(message_id, chat_id=CHATID, token=MY_TELEGRAM_TOKEN):
    bot = telegram.Bot(token=token)
    return bot.deleteMessage(chat_id=chat_id, 
                             message_id=message_id)

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
# Check values for input

def isFloat(str):
    try: 
        float(str)
    except ValueError: 
        return False
    return True

def isInt(str):
    try: 
        int(str)
    except ValueError: 
        return False
    return True

# Format day and time (arrow) for actual prints

def getTimeDelta(deltaT = 0): # in seconds (datetime..timedelta.total_seconds())
    seconds = int(deltaT)
    seconds_in_day = 60 * 60 * 24
    seconds_in_hour = 60 * 60
    seconds_in_minute = 60

    days = seconds // seconds_in_day
    hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
    minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
    second = seconds % 60

    if second < 10:
        secondStr = "0%s"%second
    else:
        secondStr = "%s"%second
    if minutes < 10:
        minutesStr = "0%s"%minutes
    else:
        minutesStr = "%s"%minutes
    if hours < 10:
        hoursStr = "0%s"%hours
    else:
        hoursStr = "%s"%hours

    if days > 0:
        message="%sd - %s:%s:%s" % (days,hoursStr,minutesStr,secondStr)
        return message
    elif hours > 0:
        message="%s:%s:%s" % (hoursStr,minutesStr,secondStr)
        return message
    elif minutes > 0:
        message="00:%s:%s" % (minutesStr,secondStr)
        return message
    else:
        message="00:00:%s" % (secondStr)
        return message

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

def error_callback(update, error): # Telegram bot error handling
    """
    Handle errors in the dispatcher and decide which errors are just logged and which errors are important enough to
    trigger a message to the admin.
    """
    try:
        telegramSendMsg(_("BOT Error!!! Please try again.") + "\n %s" % error.error,reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        raise error.error
    except telegram.error.BadRequest:
        logger.error('Bot Bad Request "%s"' % error.error)
    except telegram.error.TimedOut:
        logger.error('Bot TimedOut "%s"' % error.error)
    except:
        logger.error('Bot Error "%s"' % error.error) 

def checkUserIDValid(update, chatID=CHATID):# Telegram check user ID
    if update.effective_chat.id == chatID:
        return True
    else:
        return False    

# Telegram interaction functions

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

def getStartKeyboard(userKeyb = []):# Main keyboard layout at start of bot for printer
    stdKeyb = []
    stdKeyb.append(InlineKeyboardButton(_("End"), callback_data='End'))
    reply_markup = build_menu(userKeyb,
               1,
               footer_buttons=stdKeyb)
    return reply_markup

def getKeyboard(userKeyb = [], back = ""):# Main keyboard layout of bot for printer levels below
    stdKeyb = []
    stdKeyb.append(InlineKeyboardButton(_("Back"), callback_data='Back'))
    stdKeyb.append(InlineKeyboardButton(_("End"), callback_data='End'))
    reply_markup = build_menu(userKeyb,
               2,
               footer_buttons=stdKeyb)
    return reply_markup

def getSpecialKeyboard(headerKeyb = [], userKeyb = [], back = ""):# Main keyboard layout of bot for printer levels below
    stdKeyb = []
    stdKeyb.append(InlineKeyboardButton(_("Back"), callback_data='Back'))
    stdKeyb.append(InlineKeyboardButton(_("End"), callback_data='End'))
    reply_markup = build_menu(userKeyb,
               2,
               footer_buttons=stdKeyb,
               header_buttons=headerKeyb)
    return reply_markup

def getMsgKeyboard():# Message keyboard add ons
    userKeyb = []
    msg = botThreads.getServerDataStorage(action="messages")
    for message in msg:
        userKeyb.append(InlineKeyboardButton(message['id'], callback_data=message['id']))
    stdKeyb = []
    stdKeyb.append(InlineKeyboardButton(_("End"), callback_data='End'))
    reply_markup = build_menu(userKeyb,
               4,
               footer_buttons=stdKeyb)
    return reply_markup

def checkStartKeys(slug):# Check start keyboard add ons
    key = []
    msg = botThreads.getServerDataStorage(action="listExternalCommands")
    msg2 = botThreads.getPrinterDataStorage(slug=slug, action="getPrinterConfig")
    listPrinters = botThreads.getPrinterDataStorage(slug, "listPrinter")
    if msg == "Error" or msg2 == "Error" or listPrinters == "Error":
        return key
    if len(msg) > 0:    
        key.append(InlineKeyboardButton(_("ExtCommands"), callback_data='ExtCommands'))
    for webcam in range(0,len(msg2['webcams'])):
        key.append(InlineKeyboardButton(_('Webcam %s') % str(webcam + 1), callback_data='Webcam %s' % str(webcam + 1)))
    if len(msg2['quickCommands']) > 0:
        key.append(InlineKeyboardButton(_('Quick Commands'), callback_data='QuickCommands'))
    if listPrinters['online'] == 1 and listPrinters['active'] == True:
        key.append(InlineKeyboardButton(_('Printer'), callback_data='HandlePrinter'))
    key.append(InlineKeyboardButton(_('Settings'), callback_data='Settings'))
    return key

def getLogfilesKeyboard():
    key = []
    for file in os.listdir(LOGFILEFOLDER):
        if file.endswith(FILENAME_NO_EXTENSION + '.log'): 
            buf = {}
            buf['filename'] = file
            x = file.split("_")
            date = x[0][4:] + "." + x[0][2:4] + "." + x[0][:2]
            time = x[1][:2] + ":" + x[1][2:4] + ":" + x[1][4:]
            buf['date'] = date
            buf['time'] = time
            key.append(InlineKeyboardButton(("%s/%s") % (buf['date'], buf['time']), callback_data=buf['filename']))
    key.append(InlineKeyboardButton(_("database"), callback_data='database'))
    key.append(InlineKeyboardButton(_("Active Threads"), callback_data='threads'))
    return key

def getRemPrinterFromBotKeyboard():
    key = []
    for printer in botThreads.botData['printers']:
        key.append(InlineKeyboardButton(_("Remove %s") % (printer), callback_data=printer))
    return key

def getRepetierBotStatsKeyboard():
    key = []
    for stats in botThreads.botData['server']['dataRepetier']['historySummary']:
        key.append(InlineKeyboardButton(stats, callback_data=stats))
    return key

def getExtCommands():# Get external commands from server
    key = []
    msg = botThreads.getServerDataStorage(action="listExternalCommands")
    if msg == "Error":
        return key
    for item in msg:    
        key.append(InlineKeyboardButton(item['name'], callback_data=item['id']))
    return key

def getExtCommandsConfirmButton(command):# Get external command OK button
    key = []
    msg = botThreads.getServerDataStorage(action="listExternalCommands")
    if msg == "Error":
        return key
    for item in msg:
        if item['id'] == command:
            key.append(InlineKeyboardButton(_("OK"), callback_data='OK'))
    return key

def getExtCommandsConfirmText(command):# Get external commands confirmation text from server
    msg = botThreads.getServerDataStorage(action="listExternalCommands")
    if msg == "Error":
        return "Error"
    for item in msg:
        if item['id'] == command:            
            return item['confirm']
        
def getWebcamConfig(slug, update):# Get webcam configuration from server
    queryData = update.callback_query.data
    key = []
    msg2 = botThreads.getPrinterDataStorage(slug=slug, action="getPrinterConfig")
    if msg2 == "Error":
        return key
    x = int(queryData.split()[1]) - 1
    if msg2['webcams'][x]['dynamicUrl'] != "":
        key.append(InlineKeyboardButton(_('Send Video Camera %s') % str(x + 1), callback_data='Send Video %s' % str(x + 1))) # 'Sende Video %s' % str(webcam + 1)
    if msg2['webcams'][x]['staticUrl'] != "": 
        key.append(InlineKeyboardButton(_('Send Gif Camera %s') % str(x + 1), callback_data='Send Gif %s' % str(x + 1)))
        key.append(InlineKeyboardButton(_('Send Png Camera %s') % str(x + 1), callback_data='Send Png %s' % str(x + 1)))
    return key

def getQuickCommandsButton(slug):# Get quick command configuration from server
    key = []
    msg2 = botThreads.getPrinterDataStorage(slug=slug, action="getPrinterConfig")
    if msg2 == "Error":
        loggerWS.error("Request error getPrinterConfig in getQuickCommandsButton for printer: %s" % str(slug))
        return key
    quickCom = msg2['quickCommands']
    for item in quickCom:    
        key.append(InlineKeyboardButton(item['name'], callback_data=item['name']))
    return key

def getSettingsButton(slug):# Get settings configuration from config file
    key = []
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            key.append(InlineKeyboardButton(_("Extr. cool down: %s°C") % item['extrCoolTemp'], callback_data='Extruder Temp Limit %s' % item['extrCoolTemp']))
            if item['extrCoolTempExtComm'] != None:
                msg = botThreads.getServerDataStorage(action="listExternalCommands")
                for msgitem in msg:
                    if item['extrCoolTempExtComm'] == msgitem['id']:
                        key.append(InlineKeyboardButton(_("ExtCom: %s") % msgitem['name'], callback_data='ExtCommand Temp Limit %d' % msgitem['id']))
            else:
                key.append(InlineKeyboardButton(_("ExtCom temp. dis."), callback_data='ExtCommand Temp Limit None'))
            key.append(InlineKeyboardButton(_("Heatb. cool down: %s°C") % item['heatbCoolTemp'], callback_data='Heatbed Temp Limit %s' % item['heatbCoolTemp']))
            if item['heatbCoolTempExtComm'] != None:
                msg = botThreads.getServerDataStorage(action="listExternalCommands")
                for msgitem in msg:
                    if item['heatbCoolTempExtComm'] == msgitem['id']:
                        key.append(InlineKeyboardButton(_("HeatbCom: %s") % msgitem['name'], callback_data='HeatbCommand Temp Limit %d' % msgitem['id']))
            else:
                key.append(InlineKeyboardButton(_("HeatbCom temp. dis."), callback_data='HeatbCommand Temp Limit None'))
            key.append(InlineKeyboardButton(_("Pic after print: %ss") % item['delayTimeAfterPrintPic'], callback_data='Print after time %s' % item['delayTimeAfterPrintPic']))
            if item['AfterPrintPicCamSelect'] != None:
                key.append(InlineKeyboardButton(_("From Cam: %s") % str(item['AfterPrintPicCamSelect']+1), callback_data='Send Png %s' % str(item['AfterPrintPicCamSelect'])))
            else:
                key.append(InlineKeyboardButton(_("Pic disabled"), callback_data='Send Png None'))
            key.append(InlineKeyboardButton(_("Pic after z height: %smm") % item['zHeightPrintPic'], callback_data='zHeight Value %s' % item['zHeightPrintPic']))
            if item['zHeightPrintPicCamSelect'] != None:
                key.append(InlineKeyboardButton(_("From Cam: %s") % str(item['zHeightPrintPicCamSelect']+1), callback_data='Send zHeight Png %s' % str(item['zHeightPrintPicCamSelect'])))
            else:
                key.append(InlineKeyboardButton(_("Pic disabled"), callback_data='Send zHeight Png None'))
            key.append(InlineKeyboardButton(_("Pic after time: %s min") % item['timeBasedPrintPic'], callback_data='Print time based time %s' % item['timeBasedPrintPic']))
            if item['timeBasedPrintPicCamSelect'] != None:
                key.append(InlineKeyboardButton(_("From Cam: %s") % str(item['timeBasedPrintPicCamSelect']+1), callback_data='Send time based Png %s' % str(item['timeBasedPrintPicCamSelect'])))
            else:
                key.append(InlineKeyboardButton(_("Pic disabled"), callback_data='Send time based Png None'))
    return key

def getExtComAndDisableButton():# Get external command buttons and disable button
    key = getExtCommands()
    key.append(InlineKeyboardButton(_("disable ExtCom"), callback_data='ExtCommand Temp Limit Disable'))
    return key

def getAfterPrintWebcamAndDisableButton(slug):# Get webcam buttons and disable button
    key = getAllWebcamsFromPrinterAfter(slug)
    key.append(InlineKeyboardButton(_("disable Pic"), callback_data='Send Png None'))
    return key

def getZHeightPrintWebcamAndDisableButton(slug):# Get webcam buttons and disable button
    key = getAllWebcamsFromPrinterZHeight(slug)
    key.append(InlineKeyboardButton(_("disable Pic"), callback_data='Send zHeight Png None'))
    return key

def getTimeBasedPrintWebcamAndDisableButton(slug):# Get webcam buttons and disable button
    key = getAllWebcamsFromPrinterTimeBased(slug)
    key.append(InlineKeyboardButton(_("disable Pic"), callback_data='Send time based Png None'))
    return key

def getAllWebcamsFromPrinterAfter(slug):# Get available webcams from server
    key = []
    msg2 = botThreads.getPrinterDataStorage(slug=slug, action="getPrinterConfig")
    if msg2 == "Error":
        return key
    for x in range(0, len(msg2['webcams'])):
        if msg2['webcams'][x]['staticUrl'] != "": 
            key.append(InlineKeyboardButton(_('Send Png Camera %s') % str(x + 1), callback_data='Send Png %s' % str(x + 1)))
    return key

def getAllWebcamsFromPrinterZHeight(slug):# Get available webcams from server
    key = []
    msg2 = botThreads.getPrinterDataStorage(slug=slug, action="getPrinterConfig")
    if msg2 == "Error":
        return key
    for x in range(0, len(msg2['webcams'])):
        if msg2['webcams'][x]['staticUrl'] != "": 
            key.append(InlineKeyboardButton(_('Send Png Camera %s') % str(x + 1), callback_data='Send zHeight Png %s' % str(x + 1)))
    return key

def getAllWebcamsFromPrinterTimeBased(slug):# Get available webcams from server
    key = []
    msg2 = botThreads.getPrinterDataStorage(slug=slug, action="getPrinterConfig")
    if msg2 == "Error":
        return key
    for x in range(0, len(msg2['webcams'])):
        if msg2['webcams'][x]['staticUrl'] != "": 
            key.append(InlineKeyboardButton(_('Send Png Camera %s') % str(x + 1), callback_data='Send time based Png %s' % str(x + 1)))
    return key

def getOKButton():# Get OK button
    key = []
    key.append(InlineKeyboardButton(_("OK"), callback_data='OK'))
    return key

def getStartPrintButton(slug):# Get OK button
    key = []
    key.append(InlineKeyboardButton(_("Printer queue"), callback_data='Queue'))
    stateLists = botThreads.getPrinterDataStorage(slug, "stateList")
    if stateLists != "Error":
        for i in range(0,len(stateLists['fans'])):
            key.append(InlineKeyboardButton((_("Fan speed") + " %d" % (i+1)), callback_data="FanSpeed %d" % i))
        for i in range(0,len(stateLists['extruder'])):
            key.append(InlineKeyboardButton((_("Extr temp") + " %d" % (i+1)), callback_data="ExtruderTemperature %d" % i))
        for i in range(0,len(stateLists['heatedBeds'])):
            key.append(InlineKeyboardButton((_("Bed temp") + " %d" % (i+1)), callback_data="BedTemperature %d" % i))
        for i in range(0,len(stateLists['heatedChambers'])):
            key.append(InlineKeyboardButton((_("Cham temp") + " %d" % (i+1)), callback_data="ChamberTemperature %d" % i))
    return key

def getHandlePrintButton(slug):
    key = []
    key.append(InlineKeyboardButton(_("Flow multiplier"), callback_data='FlowMultiply'))
    key.append(InlineKeyboardButton(_("Speed multiplier"), callback_data='SpeedMultiply'))
    stateLists = botThreads.getPrinterDataStorage(slug, "stateList")
    if stateLists != "Error":
        for i in range(0,len(stateLists['fans'])):
            key.append(InlineKeyboardButton((_("Fan speed") + " %d" % (i+1)), callback_data="FanSpeed %d" % i))
        for i in range(0,len(stateLists['extruder'])):
            key.append(InlineKeyboardButton((_("Extr temp") + " %d" % (i+1)), callback_data="ExtruderTemperature %d" % i))
        for i in range(0,len(stateLists['heatedBeds'])):
            key.append(InlineKeyboardButton((_("Bed temp") + " %d" % (i+1)), callback_data="BedTemperature %d" % i))
        for i in range(0,len(stateLists['heatedChambers'])):
            key.append(InlineKeyboardButton((_("Cham temp") + " %d" % (i+1)), callback_data="ChamberTemperature %d" % i))
    key.append(InlineKeyboardButton(_("Cancel print"), callback_data='Cancel'))
    return key

def getPrintQueueText(slug, pos):# Get quick command text from server
    fileList = []
    thumbnPos = 0
    filePathModel= pathlib.Path(os.path.join(MODELFILEFOLDER, slug))
    pngCounter = sum(1 for x in pathlib.Path(filePathModel).glob('*.png') if x.is_file())
    for eachFileInPath in pathlib.Path(filePathModel).glob('*.png'):
        printData = {}
        printData['id'] = int(os.path.splitext(os.path.basename(eachFileInPath))[0])
        printData['file'] = eachFileInPath
        fileList.append(printData)
    listModels = botThreads.getPrinterDataStorage(slug, "listModels")
    message = _("Printer Queue") + ":\n"
    if pngCounter == 0:
        message += "<b> " +  _("No files on the Server") + "...</b>"
    elif pngCounter > pos + 6:
        for txt in range(pos, (pos+6)):
            fileInfo = fileList[txt]
            for anyModel in listModels['data']:
                if anyModel['id'] == fileInfo['id']:
                    message += "<code> %d: %s, " % (thumbnPos+1,anyModel['name']) + _("Print Time: %s") % (getTimeDelta(anyModel['printTime'])) + "</code>\n"                    
            thumbnPos += 1
    else:
        amountPic = pngCounter - pos
        for pic in range(pos, pngCounter):
            fileInfo = fileList[pic]
            for anyModel in listModels['data']:
                if anyModel['id'] == fileInfo['id']:
                    message += "<code> %d: %s, " % (thumbnPos+1,anyModel['name']) + _("Print Time: %s") % (getTimeDelta(anyModel['printTime'])) + "</code>\n"
            thumbnPos += 1
    return message

def getPreviewPicSetting(preMsg):
    msg = {}
    msg['msgLong'] = preMsg
    msg['msgShort'] = preMsg
    msg['id'] = 0
    msg['actPrint'] = os.path.join(MODELFILEFOLDER,'preview.jpg')
    return msg

def getPrintSelectData(slug, fileID):# Get print file data
    filePathModel= pathlib.Path(os.path.join(MODELFILEFOLDER, slug))
    listModels = botThreads.getPrinterDataStorage(slug, "listModels")
    message = "<b> " +  _("Print File") + ":</b>\n"
    file = ""
    idInt = int(fileID)
    for eachFileInList in listModels['data']:
        if eachFileInList['id'] == idInt:
            filePathModelName = fileID + ".png"
            file = pathlib.Path(os.path.join(filePathModel, filePathModelName))
            message += "<code>" + _("Print: ") + ": %s" % (eachFileInList['name'])  + "</code>\n"
            if eachFileInList['notes'] != "":
                message += "<code>" + _("Note") + ": %s" % (eachFileInList['notes']) + "</code>\n"  
            message += "<code>" + _("Print Time") + ": %s" % (getTimeDelta(eachFileInList['printTime'])) + "</code>\n"
            message += "<code>" + _("Filament total") + ": %.2fm" % (eachFileInList['filamentTotal']/1000) + "</code>\n"
            message += "<code>" + _("Slicer") + ": %s" % (eachFileInList['slicer']) + "</code>\n" 
            message += "<code>" + _("Created") + ": %s" % (arrow.get(int(eachFileInList['created'])).format('DD.MM.YYYY - HH:mm')) + "</code>\n"
            message += "<code>" + _("Layers") + ": %d" % (int(eachFileInList['layer'])) + "</code>\n" 
            message += "<code>" + _("Printed") + ": %d" % (int(eachFileInList['printed'])) + "</code>\n" 
            if eachFileInList['fits']:
                message += "<code>" + _("Fits On Heatbed: Yes") + "</code>\n" 
            else:
                message += "<code>" + _("Fits On Heatbed: No") + "</code>\n"
    msg = {}
    msg['msgLong'] = message
    msg['msgShort'] = message
    msg['id'] = idInt
    msg['actPrint'] = file
    return msg, idInt

def getPrintQueueButton(slug, pos):# Get print queue
    key = []
    fileList = []
    thumbnPos = 0
    filePathModel= pathlib.Path(os.path.join(MODELFILEFOLDER, slug))
    fileBackground = os.path.join(MODELFILEFOLDER,'background.jpg') # (827, 512)
    filePreview = os.path.join(MODELFILEFOLDER,'preview.jpg') # (827, 512)
    pngCounter = sum(1 for x in pathlib.Path(filePathModel).glob('*.png') if x.is_file())
    key = getMoveQueueButton(pngCounter, pos)
    for eachFileInPath in pathlib.Path(filePathModel).glob('*.png'):
        printData = {}
        printData['id'] = int(os.path.splitext(os.path.basename(eachFileInPath))[0])
        printData['file'] = eachFileInPath
        fileList.append(printData)
    listModels = botThreads.getPrinterDataStorage(slug, "listModels")
    if pngCounter == 0:
        preview = Image.open(fileBackground)
        drawPreview = ImageDraw.Draw(preview)
        drawPreview.text((50, 256),_("No files on the Server"),(0,0,0),font=fontMedium)
        preview.save(filePreview)
    elif pngCounter > pos + 6:
        preview = Image.open(fileBackground)
        for pic in range(pos, (pos+6)):
            fileInfo = fileList[pic]
            for anyModel in listModels['data']:
                if anyModel['id'] == fileInfo['id']:
                    preview = addThumbnail(pic=preview,
                                           pos=thumbnPos,
                                           text=anyModel['name'],
                                           picThmbFile=fileInfo['file'])
                    key.append(InlineKeyboardButton(anyModel['name'], callback_data=str(anyModel['id'])))
            thumbnPos += 1
        preview.save(filePreview)
    else:
        preview = Image.open(fileBackground)
        amountPic = pngCounter - pos
        for pic in range(pos, pngCounter):
            fileInfo = fileList[pic]
            for anyModel in listModels['data']:
                if anyModel['id'] == fileInfo['id']:
                    preview = addThumbnail(pic=preview,
                                           pos=thumbnPos,
                                           text=anyModel['name'],
                                           picThmbFile=fileInfo['file'],
                                           amountPic=amountPic) 
                    key.append(InlineKeyboardButton(anyModel['name'], callback_data=str(anyModel['id'])))
            thumbnPos += 1
        preview.save(filePreview)
    return key

def getMoveQueueButton(pngCounter, pos):
    key = []
    if pos > 12:
        npos = pos - 12
        if npos < 0:
            npos = 0
        key.append(InlineKeyboardButton("<<", callback_data="<< %s" % str(npos)))
    if pos > 5:
        npos = pos - 6
        if npos < 0:
            npos = 0
        key.append(InlineKeyboardButton("<", callback_data="<< %s" % str(npos)))
    if pngCounter-pos > 12:
        npos = pos + 12
        key.append(InlineKeyboardButton(">>", callback_data=">> %s" % str(npos)))
    if pngCounter-pos > 6:
        npos = pos + 6
        key.append(InlineKeyboardButton(">", callback_data=">> %s" % str(npos)))
    return key

def getPrintSelectionButton(slug, id):# Get print queue
    key = []
    key.append(InlineKeyboardButton("Print", callback_data=str(id)))
    return key

def setFMultiplyButton():
    key = []
    key.append(InlineKeyboardButton("+10", callback_data="plus10"))
    key.append(InlineKeyboardButton("-10", callback_data="minus10"))
    key.append(InlineKeyboardButton("+5", callback_data="plus5"))
    key.append(InlineKeyboardButton("-5", callback_data="minus5"))
    key.append(InlineKeyboardButton("+1", callback_data="plus1"))
    key.append(InlineKeyboardButton("-1", callback_data="minus1"))
    return key

def setPrintFSpeedButton(queryData):
    fan = int(queryData.split()[1])
    key = []
    key.append(InlineKeyboardButton("100%", callback_data="100 %d" % fan))
    key.append(InlineKeyboardButton("90%", callback_data="90 %d" % fan))
    key.append(InlineKeyboardButton("80%", callback_data="80 %d" % fan))
    key.append(InlineKeyboardButton("70%", callback_data="70 %d" % fan))
    key.append(InlineKeyboardButton("60%", callback_data="60 %d" % fan))
    key.append(InlineKeyboardButton("50%", callback_data="50 %d" % fan))
    key.append(InlineKeyboardButton("40%", callback_data="40 %d" % fan))
    key.append(InlineKeyboardButton("30%", callback_data="30 %d" % fan))
    key.append(InlineKeyboardButton("20%", callback_data="20 %d" % fan))
    key.append(InlineKeyboardButton("10%", callback_data="10 %d" % fan))
    key.append(InlineKeyboardButton("OFF", callback_data="0 %d" % fan))
    return key

def setETempButton():
    key = []
    key.append(InlineKeyboardButton("+10", callback_data="plus10"))
    key.append(InlineKeyboardButton("-10", callback_data="minus10"))
    key.append(InlineKeyboardButton("+5", callback_data="plus5"))
    key.append(InlineKeyboardButton("-5", callback_data="minus5"))
    key.append(InlineKeyboardButton("+1", callback_data="plus1"))
    key.append(InlineKeyboardButton("-1", callback_data="minus1"))
    key.append(InlineKeyboardButton("200°C", callback_data="200"))
    key.append(InlineKeyboardButton("210°C", callback_data="210"))
    key.append(InlineKeyboardButton("220°C", callback_data="220"))
    key.append(InlineKeyboardButton("230°C", callback_data="230"))
    key.append(InlineKeyboardButton("240°C", callback_data="240"))
    key.append(InlineKeyboardButton("OFF", callback_data="0"))
    return key

def setBTempButton():
    key = []
    key.append(InlineKeyboardButton("+10", callback_data="plus10"))
    key.append(InlineKeyboardButton("-10", callback_data="minus10"))
    key.append(InlineKeyboardButton("+5", callback_data="plus5"))
    key.append(InlineKeyboardButton("-5", callback_data="minus5"))
    key.append(InlineKeyboardButton("+1", callback_data="plus1"))
    key.append(InlineKeyboardButton("-1", callback_data="minus1"))
    key.append(InlineKeyboardButton("50°C", callback_data="50"))
    key.append(InlineKeyboardButton("60°C", callback_data="60"))
    key.append(InlineKeyboardButton("70°C", callback_data="70"))
    key.append(InlineKeyboardButton("80°C", callback_data="80"))
    key.append(InlineKeyboardButton("90°C", callback_data="90"))
    key.append(InlineKeyboardButton("OFF", callback_data="0"))
    return key

def addThumbnail(pic, pos, text, picThmbFile, amountPic = 6):
    picthmb = Image.open(picThmbFile)
    box = (150, 100, 400, 300)
    picthmbBox = picthmb.crop(box)
    draw = ImageDraw.Draw(picthmbBox)
    try:
        draw.text((0,0),text,(0,0,0),font=fontSmall)
    except:
        loggerWS.error("addThumbnail not possible for pic: %s" % str(text))
    #foo = foo.resize((160,300),Image.ANTIALIAS)
    if amountPic == 1:
        position = (int(pic.width/2-picthmbBox.width/2), int(pic.height/2-picthmbBox.height/2))
    elif amountPic == 2:
        position = (int((pic.width/2*pos+pic.width/4)-picthmbBox.width/2), int(pic.height/2-picthmbBox.height/2))
    elif amountPic == 3:
        position = (int(pic.width/3*pos+10), int(pic.height/2-picthmbBox.height/2))
    elif amountPic == 4:
        if pos < 2:
            position = (int((pic.width/2*pos+pic.width/4)-picthmbBox.width/2), 10)
        else:
            position = (int((pic.width/2*(pos-2)+pic.width/4)-picthmbBox.width/2), int(pic.height-picthmbBox.height-10))
    elif amountPic == 5:
        if pos < 3:
            position = (int(pic.width/3*pos+10), 10)
        else:
            position = (int((pic.width/2*(pos-3)+pic.width/4)-picthmbBox.width/2), int(pic.height-picthmbBox.height-10))
    else:
        if pos < 3:
            position = (int(pic.width/3*pos+10), 10)
        else:
            position = (int(pic.width/3*(pos-3)+10), int(pic.height-picthmbBox.height-10))
    pic.paste(picthmbBox, position)
    return pic

def getQuickCommandsText(slug):# Get quick command text from server
    msg2 = botThreads.getPrinterDataStorage(slug=slug, action="getPrinterConfig")
    if msg2 == "Error":
        loggerWS.error("Request error getPrinterConfig in getQuickCommandsButton for printer: %s" % str(slug))
        return msg2
    quickCom = msg2['quickCommands']
    message = _("Quick Commands") + ":\n"
    for item in quickCom:    
        message += "<b>%s</b>:\n <code>%s</code>" % (item['name'], item['command']) + "\n"
    return message

def sendQuickCommand(slug, text):# Send quick command
    msg2 = botThreads.getPrinterDataStorage(slug=slug, action="getPrinterConfig")
    if msg2 == "Error":
        loggerWS.error("Request error getPrinterConfig in sendQuickCommand for printer: %s" % str(slug))
        sendMsgToBot(slug=slug, 
                 function="printer", 
                 msg="<b>" + _("Quick command handling aborted") + "</b>", 
                 reply_markup=None,
                 singleMsg=True)
        return
    quickCom = msg2['quickCommands']
    for item in quickCom:    
        if item['name'] == text:
            packOrder = {}
            packOrder['name'] = item['name']
            botThreads.sendRecExtendedData(action="sendQuickCommand", slug=slug, data=packOrder, messageCntItem="sendQuickCommand")

def sendDelayMessage(slug,function,reply_markup,timer=5):
    for i in range(timer,0,-1):
        sendMsgToBot(slug=slug, 
                     function=function, 
                     msg="<b>🔜 %d" % i + "......</b>", 
                     reply_markup=reply_markup)
        time.sleep(1)

def sendCancelPrint(slug):# Send cancel print command
    packOrder = {}
    botThreads.sendRecExtendedData(action="stopJob", slug=slug, data=packOrder, messageCntItem="stopJob")
    sendMsgToBot(slug=slug, 
                 function="printer", 
                 msg="<b>" + _("Stop job sent to printer") + "</b>", 
                 reply_markup=None,
                 singleMsg=True)
        
def sendEmStop(slug):# Send cancel print command
    packOrder = {}
    botThreads.sendRecExtendedData(action="emergencyStop", slug=slug, data=packOrder, messageCntItem="emergencyStop")
    sendMsgToBot(slug=slug, 
                 function="printer", 
                 msg="<b>" + _("Emergency stop sent to printer") + "</b>", 
                 reply_markup=None,
                 singleMsg=True)
        
def setFMultiply(slug, fMultply, typedValue=True):
    if typedValue:
        if isInt(fMultply):
            packOrder = {}
            packOrder['speed'] = fMultply
            botThreads.sendRecExtendedData(action="setFlowMultiply", slug=slug, data=packOrder, messageCntItem="setFlowMultiply")
            sendMsgToBot(slug=slug, 
                            function="setFMultiply", 
                            msg="<i>" + _("Flow multiply changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                            function="setFMultiply", 
                            msg="<b>" + _("Flow multiply change failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
    else:
        stateList = botThreads.getPrinterDataStorage(slug=slug, action="stateList")
        if stateList != "Error":
            if fMultply == "plus10":
                addMul = stateList['flowMultiply'] + 10
            elif fMultply == "plus5":
                addMul = stateList['flowMultiply'] + 5
            elif fMultply == "plus1":
                addMul = stateList['flowMultiply'] + 1
            elif fMultply == "minus10":
                addMul = stateList['flowMultiply'] - 10
            elif fMultply == "minus5":
                addMul = stateList['flowMultiply'] - 5
            elif fMultply == "minus1":
                addMul = stateList['flowMultiply'] - 1
            packOrder = {}
            packOrder['speed'] = addMul
            botThreads.sendRecExtendedData(action="setFlowMultiply", slug=slug, data=packOrder, messageCntItem="setFlowMultiply")
            sendMsgToBot(slug=slug, 
                            function="setFMultiply", 
                            msg="<i>" + _("Flow multiply changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        
def setSMultiply(slug, SMultply, typedValue=True):
    if typedValue:
        if isInt(SMultply):
            packOrder = {}
            packOrder['speed'] = SMultply
            botThreads.sendRecExtendedData(action="setSpeedMultiply", slug=slug, data=packOrder, messageCntItem="setSpeedMultiply")
            sendMsgToBot(slug=slug, 
                            function="setSMultiply", 
                            msg="<i>" + _("Speed multiply changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                            function="setSMultiply", 
                            msg="<b>" + _("Speed multiply change failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
    else:
        stateList = botThreads.getPrinterDataStorage(slug=slug, action="stateList")
        if stateList != "Error":
            if SMultply == "plus10":
                addMul = stateList['speedMultiply'] + 10
            elif SMultply == "plus5":
                addMul = stateList['speedMultiply'] + 5
            elif SMultply == "plus1":
                addMul = stateList['speedMultiply'] + 1
            elif SMultply == "minus10":
                addMul = stateList['speedMultiply'] - 10
            elif SMultply == "minus5":
                addMul = stateList['speedMultiply'] - 5
            elif SMultply == "minus1":
                addMul = stateList['speedMultiply'] - 1
            packOrder = {}
            packOrder['speed'] = addMul
            botThreads.sendRecExtendedData(action="setSpeedMultiply", slug=slug, data=packOrder, messageCntItem="setSpeedMultiply")
            sendMsgToBot(slug=slug, 
                            function="setSMultiply", 
                            msg="<i>" + _("Speed multiply changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        
def setFSpeed(slug, FSpeed, typedValue=False, fanID=0):
    if typedValue:
        if isInt(FSpeed):
            #100 * fan['voltage'] / 255
            packOrder = {}
            packOrder['speed'] = int(int(FSpeed)*255/100) # fanId
            packOrder['fanId'] = fanID # fanId
            botThreads.sendRecExtendedData(action="setFanSpeed", slug=slug, data=packOrder, messageCntItem="setFanSpeed")
            sendMsgToBot(slug=slug, 
                            function="setFSpeed", 
                            msg="<i>" + _("Fan speed changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                            function="setFSpeed", 
                            msg="<b>" + _("Fan Speed change failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
    else:
        speed=int(FSpeed.split()[0])
        fan=int(FSpeed.split()[1])
        packOrder = {}
        packOrder['speed'] = int(speed*255/100)
        packOrder['fanId'] = fan # fanId
        botThreads.sendRecExtendedData(action="setFanSpeed", slug=slug, data=packOrder, messageCntItem="setFanSpeed")
        sendMsgToBot(slug=slug, 
                        function="setFSpeed", 
                        msg="<i>" + _("Fan speed changed") + "</i>", 
                        reply_markup=None,
                        singleMsg=True,
                        delTime=5)
        
def setETemp(slug, eTemp, typedValue=False, extrID=0):
    if typedValue:
        if isInt(eTemp):
            packOrder = {}
            packOrder['temperature'] = int(eTemp)
            packOrder['extruder'] = extrID 
            botThreads.sendRecExtendedData(action="setExtruderTemperature", slug=slug, data=packOrder, messageCntItem="setExtruderTemperature")
            sendMsgToBot(slug=slug, 
                            function="setETemp", 
                            msg="<i>" + _("Extruder temperature changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                            function="setETemp", 
                            msg="<b>" + _("Extruder temperature change failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
    else:
        stateList = botThreads.getPrinterDataStorage(slug=slug, action="stateList")
        if stateList != "Error":
            if eTemp == "plus10":
                addSetTemp = int(stateList['extruder'][extrID]['tempSet']) + 10
            elif eTemp == "plus5":
                addSetTemp = int(stateList['extruder'][extrID]['tempSet']) + 5
            elif eTemp == "plus1":
                addSetTemp = int(stateList['extruder'][extrID]['tempSet']) + 1
            elif eTemp == "minus10":
                addSetTemp = int(stateList['extruder'][extrID]['tempSet']) - 10
            elif eTemp == "minus5":
                addSetTemp = int(stateList['extruder'][extrID]['tempSet']) - 5
            elif eTemp == "minus1":
                addSetTemp = int(stateList['extruder'][extrID]['tempSet']) - 1
            elif eTemp == "200":
                addSetTemp = 200
            elif eTemp == "210":
                addSetTemp = 210
            elif eTemp == "220":
                addSetTemp = 220
            elif eTemp == "230":
                addSetTemp = 230
            elif eTemp == "240":
                addSetTemp = 240
            elif eTemp == "0":
                addSetTemp = 0
            packOrder = {}
            packOrder['temperature'] = addSetTemp
            packOrder['extruder'] = extrID 
            botThreads.sendRecExtendedData(action="setExtruderTemperature", slug=slug, data=packOrder, messageCntItem="setExtruderTemperature")
            sendMsgToBot(slug=slug, 
                            function="setETemp", 
                            msg="<i>" + _("Extruder temperature changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        
def setBTemp(slug, bTemp, typedValue=False, heatbID=0):
    if typedValue:
        if isInt(bTemp):
            packOrder = {}
            packOrder['temperature'] = int(bTemp)
            packOrder['bedId'] = heatbID 
            botThreads.sendRecExtendedData(action="setBedTemperature", slug=slug, data=packOrder, messageCntItem="setBedTemperature")
            sendMsgToBot(slug=slug, 
                            function="setBTemp", 
                            msg="<i>" + _("Heatbed temperature changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                            function="setBTemp", 
                            msg="<b>" + _("Heatbed temperature change failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
    else:
        stateList = botThreads.getPrinterDataStorage(slug=slug, action="stateList")
        if stateList != "Error":
            if bTemp == "plus10":
                addSetTemp = int(stateList['heatedBeds'][heatbID]['tempSet']) + 10
            elif bTemp == "plus5":
                addSetTemp = int(stateList['heatedBeds'][heatbID]['tempSet']) + 5
            elif bTemp == "plus1":
                addSetTemp = int(stateList['heatedBeds'][heatbID]['tempSet']) + 1
            elif bTemp == "minus10":
                addSetTemp = int(stateList['heatedBeds'][heatbID]['tempSet']) - 10
            elif bTemp == "minus5":
                addSetTemp = int(stateList['heatedBeds'][heatbID]['tempSet']) - 5
            elif bTemp == "minus1":
                addSetTemp = int(stateList['heatedBeds'][heatbID]['tempSet']) - 1
            elif bTemp == "50":
                addSetTemp = 50
            elif bTemp == "60":
                addSetTemp = 60
            elif bTemp == "70":
                addSetTemp = 70
            elif bTemp == "80":
                addSetTemp = 80
            elif bTemp == "90":
                addSetTemp = 90
            elif bTemp == "0":
                addSetTemp = 0
            packOrder = {}
            packOrder['temperature'] = addSetTemp
            packOrder['bedId'] = heatbID 
            botThreads.sendRecExtendedData(action="setBedTemperature", slug=slug, data=packOrder, messageCntItem="setBedTemperature")
            sendMsgToBot(slug=slug, 
                            function="setBTemp", 
                            msg="<i>" + _("Heatbed temperature changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        
def setCTemp(slug, cTemp, typedValue=False, chamberId=0):
    if typedValue:
        if isInt(cTemp):
            packOrder = {}
            packOrder['temperature'] = int(cTemp)
            packOrder['chamberId'] = chamberId 
            botThreads.sendRecExtendedData(action="setChamberTemperature", slug=slug, data=packOrder, messageCntItem="setChamberTemperature")
            sendMsgToBot(slug=slug, 
                            function="setCTemp", 
                            msg="<i>" + _("Chamber temperature changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                            function="setCTemp", 
                            msg="<b>" + _("Chamber temperature change failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
    else:
        stateList = botThreads.getPrinterDataStorage(slug=slug, action="stateList")
        if stateList != "Error":
            if cTemp == "plus10":
                addSetTemp = int(stateList['heatedChambers'][chamberId]['tempSet']) + 10
            elif cTemp == "plus5":
                addSetTemp = int(stateList['heatedChambers'][chamberId]['tempSet']) + 5
            elif cTemp == "plus1":
                addSetTemp = int(stateList['heatedChambers'][chamberId]['tempSet']) + 1
            elif cTemp == "minus10":
                addSetTemp = int(stateList['heatedChambers'][chamberId]['tempSet']) - 10
            elif cTemp == "minus5":
                addSetTemp = int(stateList['heatedChambers'][chamberId]['tempSet']) - 5
            elif cTemp == "minus1":
                addSetTemp = int(stateList['heatedChambers'][chamberId]['tempSet']) - 1
            elif cTemp == "50":
                addSetTemp = 50
            elif cTemp == "60":
                addSetTemp = 60
            elif cTemp == "70":
                addSetTemp = 70
            elif cTemp == "80":
                addSetTemp = 80
            elif cTemp == "90":
                addSetTemp = 90
            elif cTemp == "0":
                addSetTemp = 0
            packOrder = {}
            packOrder['temperature'] = addSetTemp
            packOrder['chamberId'] = chamberId 
            botThreads.sendRecExtendedData(action="setChamberTemperature", slug=slug, data=packOrder, messageCntItem="setChamberTemperature")
            sendMsgToBot(slug=slug, 
                            function="setCTemp", 
                            msg="<i>" + _("Chamber temperature changed") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        
def sendStartPrint(slug, id):# Send quick command
    packOrder = {}
    packOrder['id'] = int(id)
    botThreads.sendRecExtendedData(action="copyModel", slug=slug, data=packOrder, messageCntItem="copyModel")
    sendMsgToBot(slug=slug, 
                 function="startPrint", 
                 msg="<i>" + _("Print started") + "</i>", 
                 reply_markup=None,
                 singleMsg=True,
                 delTime=5)
    loggerWS.info("Start print for printer: %s/%s" % (str(slug),id))
        
def getFMultiplyText(slug):
    stateList = botThreads.getPrinterDataStorage(slug, "stateList")
    if stateList != "Error":
        message = "<b>⚠️ " + _("Set flow multiplier from %d%% to?") % stateList['flowMultiply'] + "</b>"
    else:
        message = "<b>⚠️ " + _("Set flow multiplier? Actual value unknown!") + "</b>"
    return message

def getSMultiplyText(slug):
    stateList = botThreads.getPrinterDataStorage(slug, "stateList")
    if stateList != "Error":
        message = "<b>⚠️ " + _("Set speed multiplier from %d%% to?") % stateList['speedMultiply'] + "</b>"
    else:
        message = "<b>⚠️ " + _("Set speed multiplier? Actual value unknown!") + "</b>"
    return message

def getPrintFSpeedText(slug, queryData):
    stateList = botThreads.getPrinterDataStorage(slug, "stateList")
    fan = int(queryData.split()[1])
    message=""
    if stateList != "Error":
        #100 * fan['voltage'] / 255
        if stateList['fans'][fan]['on']:
            aSpeed = int(stateList['fans'][fan]['voltage']*100/255)
            message = "<b>⚠️ " + _("Set fan speed from %d%% to?") % aSpeed + "</b>"
        else:
            message = "<b>⚠️ " + _("Switch fan on to?") + "</b>"
    else:
        message = "<b>⚠️ " + _("Set fan speed? Actual value unknown!") + "</b>"
    return message

def getPrintETempText(slug, extr):
    stateList = botThreads.getPrinterDataStorage(slug, "stateList")
    message=""
    if stateList != "Error":
        aTemp = int(stateList['extruder'][extr]['tempSet'])
        message = "<b>⚠️ " + _("Set extruder temperature from %d°C to?") % aTemp + "</b>"
    else:
        message = "<b>⚠️ " + _("Extruder temperature? Actual value unknown!") + "</b>"
    return message

def getPrintBTempText(slug, heatb):
    stateList = botThreads.getPrinterDataStorage(slug, "stateList")
    message=""
    if stateList != "Error":
        aTemp = int(stateList['heatedBeds'][heatb]['tempSet'])
        message = "<b>⚠️ " + _("Set heatbed temperature from %d°C to?") % aTemp + "</b>"
    else:
        message = "<b>⚠️ " + _("Heatbed temperature? Actual value unknown!") + "</b>"
    return message

def getPrintCTempText(slug, chamb):
    stateList = botThreads.getPrinterDataStorage(slug, "stateList")
    message=""
    if stateList != "Error":
        aTemp = int(stateList['heatedChambers'][chamb]['tempSet'])
        message = "<b>⚠️ " + _("Set chamber temperature from %d°C to?") % aTemp + "</b>"
    else:
        message = "<b>⚠️ " + _("Chamber temperature? Actual value unknown!") + "</b>"
    return message

def getExtrSetLimitText(slug):# Text in interaction to get the temp. limit value
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            message =  _("Please input new extruder cool down temperature. Actual value: %d°C") % item['extrCoolTemp']
            return message

def getPrinExtCommText(slug):# Text in interaction to get external command
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if item['extrCoolTempExtComm'] == None:
                message = _("ExtCom disabled. Choose new action.")
            else:
                msg = botThreads.getServerDataStorage(action="listExternalCommands")
                if msg == "Error":
                    message = _("Could not connect to the server.")
                else:
                    item = msg[item['extrCoolTempExtComm']]                    
                    message = _("ExtCom active: %s") % item['name']
            return message

def setExtrSetLimit(slug, text):# set extruder temperature setting to define cold condition
    if isInt(text):
        for printer in botThreads.botData['printers']:
            if printer == slug:
                item = botThreads.botData['printers'][printer]['config']
                item['extrCoolTemp'] = int(text)
        if botThreads.savePrinterConfigFile():
            sendMsgToBot(slug=slug, 
                            function="extrCoolTemp", 
                            msg="<i>" + _("Configuration saved") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                            function="extrCoolTemp", 
                            msg="<b>" + _("Configuration saving failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)

def setPrinExtComm(slug, text):# set external command which will be after cool down temperature activated
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if isInt(text):
                item['extrCoolTempExtComm'] = int(text)
            else:
                item['extrCoolTempExtComm'] = None
            if botThreads.savePrinterConfigFile():
                sendMsgToBot(slug=slug, 
                            function="extrCoolTempExtComm", 
                            msg="<i>" + _("Configuration saved") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
            else:
                sendMsgToBot(slug=slug, 
                            function="extrCoolTempExtComm", 
                            msg="<b>" + _("Configuration saving failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)

def getHeatbSetLimitText(slug):# Text in interaction to get the temp. limit value
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            message =  _("Please input new heatbed cool down temperature. Actual value: %d°C") % item['heatbCoolTemp']
            return message

def getPrinHeatbCommText(slug):# Text in interaction to get external command
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if item['heatbCoolTempExtComm'] == None:
                message = _("ExtCom disabled. Choose new action.")
            else:
                msg = botThreads.getServerDataStorage(action="listExternalCommands")
                if msg == "Error":
                    message = _("Could not connect to the server.")
                else:
                    item = msg[item['heatbCoolTempExtComm']]                    
                    message = _("ExtCom active: %s") % item['name']
            return message

def setHeatbSetLimit(slug, text):# set extruder temperature setting to define cold condition
    if isInt(text):
        for printer in botThreads.botData['printers']:
            if printer == slug:
                item = botThreads.botData['printers'][printer]['config']
                item['heatbCoolTemp'] = int(text)
        if botThreads.savePrinterConfigFile():
            sendMsgToBot(slug=slug, 
                            function="heatbCoolTemp", 
                            msg="<i>" + _("Configuration saved") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                            function="heatbCoolTemp", 
                            msg="<b>" + _("Configuration saving failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)

def setPrinHeatbComm(slug, text):# set external command which will be after cool down temperature activated
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if isInt(text):
                item['heatbCoolTempExtComm'] = int(text)
            else:
                item['heatbCoolTempExtComm'] = None
            if botThreads.savePrinterConfigFile():
                sendMsgToBot(slug=slug, 
                            function="heatbCoolTempExtComm", 
                            msg="<i>" + _("Configuration saved") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
            else:
                sendMsgToBot(slug=slug, 
                            function="heatbCoolTempExtComm", 
                            msg="<b>" + _("Configuration saving failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)

def setAfterPrintTimeValue(slug, text):# set time delay for pic after print has finished
    if isInt(text):
        for printer in botThreads.botData['printers']:
            if printer == slug:
                item = botThreads.botData['printers'][printer]['config']
                item['delayTimeAfterPrintPic'] = int(text)
        if botThreads.savePrinterConfigFile():
            sendMsgToBot(slug=slug, 
                        function="delayTimeAfterPrintPic", 
                        msg="<i>" + _("Configuration saved") + "</i>", 
                        reply_markup=None,
                        singleMsg=True,
                        delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                        function="delayTimeAfterPrintPic", 
                        msg="<b>" + _("Configuration saving failed") + "</b>", 
                        reply_markup=None,
                        singleMsg=True,
                        delTime=5)

def setAfterPrintWebcam(slug, text):# select one of multiple cams to take pic after print has finished
    x = text.split()[2]
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if isInt(x):
                item['AfterPrintPicCamSelect'] = int(x) - 1
            else:
                item['AfterPrintPicCamSelect'] = None
            if botThreads.savePrinterConfigFile():
                sendMsgToBot(slug=slug, 
                            function="AfterPrintPicCamSelect", 
                            msg="<i>" + _("Configuration saved") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
            else:
                sendMsgToBot(slug=slug, 
                            function="AfterPrintPicCamSelect", 
                            msg="<b>" + _("Configuration saving failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)

def setZHeightValue(slug, text):# set z height value for pic 
    if isFloat(text):
        for printer in botThreads.botData['printers']:
            if printer == slug:
                item = botThreads.botData['printers'][printer]['config']
                item['zHeightPrintPic'] = float(text)
        if botThreads.savePrinterConfigFile():
            sendMsgToBot(slug=slug, 
                        function="zHeightPrintPic", 
                        msg="<i>" + _("Configuration saved") + "</i>", 
                        reply_markup=None,
                        singleMsg=True,
                        delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                        function="zHeightPrintPic", 
                        msg="<b>" + _("Configuration saving failed") + "</b>", 
                        reply_markup=None,
                        singleMsg=True,
                        delTime=5)

def setZHeightPrintPicCam(slug, text):# select one of multiple cams to take pic after print has finished
    x = text.split()[3]
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if isInt(x):
                item['zHeightPrintPicCamSelect'] = int(x) - 1
            else:
                item['zHeightPrintPicCamSelect'] = None
            if botThreads.savePrinterConfigFile():
                sendMsgToBot(slug=slug, 
                            function="setZHeightPrintPicCam", 
                            msg="<i>" + _("Configuration saved") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
            else:
                sendMsgToBot(slug=slug, 
                            function="setZHeightPrintPicCam", 
                            msg="<b>" + _("Configuration saving failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)

def setTimeBasedPrintPic(slug, text):# set extruder temperature setting to define cold condition
    if isInt(text):
        for printer in botThreads.botData['printers']:
            if printer == slug:
                item = botThreads.botData['printers'][printer]['config']
                item['timeBasedPrintPic'] = int(text)
        if botThreads.savePrinterConfigFile():
            sendMsgToBot(slug=slug, 
                            function="setTimeBasedPrintPic", 
                            msg="<i>" + _("Configuration saved") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
        else:
            sendMsgToBot(slug=slug, 
                            function="setTimeBasedPrintPic", 
                            msg="<b>" + _("Configuration saving failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)

def setTimeBasedPrintPicCam(slug, text):# select one of multiple cams to take pic after print has finished
    x = text.split()[4]
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if isInt(x):
                item['timeBasedPrintPicCamSelect'] = int(x) - 1
            else:
                item['timeBasedPrintPicCamSelect'] = None
            if botThreads.savePrinterConfigFile():
                sendMsgToBot(slug=slug, 
                            function="setTimeBasedPrintPicCam", 
                            msg="<i>" + _("Configuration saved") + "</i>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)
            else:
                sendMsgToBot(slug=slug, 
                            function="setTimeBasedPrintPicCam", 
                            msg="<b>" + _("Configuration saving failed") + "</b>", 
                            reply_markup=None,
                            singleMsg=True,
                            delTime=5)

def getAfterPrintTimeText(slug):# Text for interaction
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            message =  _("Please input new delay time. Actual value: %ds") % item['delayTimeAfterPrintPic']
            return message

def getAfterPrintWebcamText(slug):# Text for interaction
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if item['AfterPrintPicCamSelect'] == None:
                message = _("Pic after print disabled. Choose camera")
            else:
                message = _("Webcam %s active") % str(item['AfterPrintPicCamSelect']+1)
            return message

def getZHeightPrintPicText(slug):# Text for interaction
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            message =  _("Please input new z height. Actual value:") + " %.1fmm" % item['zHeightPrintPic']
            return message

def getZHeightPrintPicCamText(slug):# Text for interaction
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if item['zHeightPrintPicCamSelect'] == None:
                message = _("Z height pic disabled. Choose camera")
            else:
                message = _("Webcam %s active") % str(item['zHeightPrintPicCamSelect']+1)
            return message

def getTimeBasedPrintPicText(slug):# Text for interaction
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            message =  _("Please input new cycle time. Actual value:") + " %d min" % item['timeBasedPrintPic']
            return message

def getTimeBasedPrintPicCamText(slug):# Text for interaction
    for printer in botThreads.botData['printers']:
        if printer == slug:
            item = botThreads.botData['printers'][printer]['config']
            if item['timeBasedPrintPicCamSelect'] == None:
                message = _("Time based pic disabled. Choose camera")
            else:
                message = _("Webcam %s active") % str(item['timeBasedPrintPicCamSelect']+1)
            return message

def sendExtCommand(updateMsgTxt):# sends external command action
    key = []
    msg = botThreads.getServerDataStorage(action="listExternalCommands")
    if msg == "Error":
        return key
    for item in msg:
        if item['confirm'] == updateMsgTxt:
            packOrder = {}
            packOrder['id'] = item['id']
            botThreads.sendRecExtendedData(action="runExternalCommand", slug="server", data=packOrder, messageCntItem="runExternalCommand")
    return key

def sendDelMessage(id): # removeMessage from repetier server
    packOrder = {}
    packOrder['id'] = id
    botThreads.sendRecExtendedData(action="removeMessage", slug="server", data=packOrder, messageCntItem="removeMessage")
    
def botAddTracking(slug, function, context): # mark printer which activate bot interaction
    logger.debug("botAddTracking for: %s" % (slug))
    context.user_data['slug'] = slug
    actConv = {}
    actConv['slug'] = slug
    actConv['function'] = function
    botThreads.botData['bot']['actConv'] = actConv

def botGetTracking(context): # get marked printer which activate bot interaction
    return context.user_data['slug']

def botRemTracking():
    botThreads.botData['bot']['actConv'] = None

def botSetSpecialData(context, special):
    logger.debug("Set botSetSpecialData: %s" % (special))
    context.user_data['special'] = special

def botGetSpecialData(context):
    return context.user_data['special']

def getBotSlug(botFeedback): # get "/" rid of bot activation on slug for handling
    slug = botFeedback[1:]
    return slug

def getSystemDebugConfig(): # get debug information from application
    cfgFile = os.path.join(LOGFILEFOLDER, FILENAME_NO_EXTENSION + '.conf')
    configFile = {}
    configFile['server'] = botThreads.botData['server']['config']
    configFile['printers'] = {}
    for printers in botThreads.botData['printers']:
        configFile['printers'][printers] = botThreads.botData['printers'][printers]['config']
    try:
            with open(cfgFile, 'w') as outfile:
                json.dump(configFile, outfile) 
    except:
            logger.error("getSystemDebugConfig: Debug configuration file could not be written to: %s" % cfgFile)
    return cfgFile

def getStatisticEntryText(year):# Text for interaction
    message = "👣 <b>" + _("Bot running since") + ": </b>\n<code>%s</code>\n" % (botThreads.programStart.format('DD.MM.YYYY - HH:mm'))
    listhistorySummary = botThreads.getServerDataStorage(action="historySummary")
    if listhistorySummary != "Error" and len(listhistorySummary) != 0:
        for years in listhistorySummary:
            totalYear = {}            
            totalYear['filament'] = 0.0
            totalYear['costs'] = 0.0
            totalYear['num'] = 0
            totalYear['finished'] = 0
            totalYear['aborted'] = 0
            yearsData = listhistorySummary[years]
            for months in yearsData:
                totalYear['filament'] = months['filament'] + totalYear['filament']
                totalYear['costs'] = months['costs'] + totalYear['costs']
                totalYear['num'] = months['num'] + totalYear['num']
                totalYear['finished'] = months['finished'] + totalYear['finished']
                totalYear['aborted'] = months['aborted'] + totalYear['aborted']
            message += "💶 <b>" + _("Statistic") + " %d: </b>\n" % (years)
            message += "<code>🧶: %.2fm / " % (totalYear['filament']/1000) + "💸: %.2f€ </code>\n" % (totalYear['costs'])
            message += "<code>📠: %d / 🏁: %d / 🗑: %d" % (totalYear['num'],totalYear['finished'],totalYear['aborted']) + "</code>\n"
        year = int(year)
        if year in listhistorySummary:
            actYear = listhistorySummary[year]
            message += "\n💶 <b>" + _("Monthly Statistic") + " %d: </b>\n" % (year)
            totalYear['filament'] = 0.0
            totalYear['costs'] = 0.0
            totalYear['num'] = 0
            totalYear['finished'] = 0
            totalYear['aborted'] = 0
            for months in actYear:
                message += "<b><i>%s:\n</i></b>" % (getMonth(months['month']))
                message += "<code>🧶: %.2fm / " % (months['filament']/1000) + "💸: %.2f€ </code>\n" % (months['costs'])
                message += "<code>📠: %d / 🏁: %d / 🗑: %d" % (months['num'],months['finished'],months['aborted']) + "</code>\n" 
                totalYear['filament'] = months['filament'] + totalYear['filament']
                totalYear['costs'] = months['costs'] + totalYear['costs']
                totalYear['num'] = months['num'] + totalYear['num']
                totalYear['finished'] = months['finished'] + totalYear['finished']
                totalYear['aborted'] = months['aborted'] + totalYear['aborted']

            message += "\n<b><i>" + _("Total") + ":\n</i></b>"
            message += "<code>🧶: %.2fm / " % (totalYear['filament']/1000) + "💸: %.2f€ </code>\n" % (totalYear['costs'])
            message += "<code>📠: %d / 🏁: %d / 🗑: %d" % (totalYear['num'],totalYear['finished'],totalYear['aborted']) + "</code>\n" 
        message += "\n<i>🧶: " + _("Amount of Filament") + "</i>\n"
        message += "<i>💸: " + _("Costs") + "</i>\n"
        message += "<i>📠: " + _("Prints total") + "</i>\n"
        message += "<i>🏁: " + _("Prints finished") + "</i>\n"
        message += "<i>🗑: " + _("Prints aborted") + "</i>\n"
    return message

def getMonth(month):
    if month == 1:
        return _("January")
    elif  month == 2:
        return _("February")
    elif  month == 3:
        return _("March")
    elif  month == 4:
        return _("April")
    elif  month == 5:
        return _("May")
    elif  month == 6:
        return _("June")
    elif  month == 7:
        return _("July")
    elif  month == 8:
        return _("August")
    elif  month == 9:
        return _("September")
    elif  month == 10:
        return _("October")
    elif  month == 11:
        return _("November")
    elif  month == 12:
        return _("December")

def sendMsgToBot(slug, function, # send messages at conversation time to the bot
                 msg=None, msgLong=None, msgShort=None, 
                 path=None, caption=None, vidPic=False,
                 reply_markup=None,  
                 removeMsg=False, message_id=None,
                 singleMsg=False, delTime=15,
                 modMsg=None):
    if message_id != None:
        botThreads.remMsgFromBot(slug=slug, function=function, message_id=message_id)
        logger.info("sendMsgToBot - Remove: Slug: %s Function: %s" % (slug, function))
    elif removeMsg:
        botThreads.remMsgFromBot(slug=slug, function=function)
        logger.info("sendMsgToBot - Remove: Slug: %s Function: %s" % (slug, function))
    elif vidPic: 
        message = {}
        message['path'] = path
        message['caption'] = caption
        botThreads.addMsgToBot(slug=slug, function=function, msg=message, reply_markup=reply_markup, vidPic=vidPic, singleMsg=singleMsg, delTime=delTime, modMsg=modMsg, priority=True)
        logger.debug("sendMsgToBot - Send: Slug: %s Function: %s Path: %s Caption: %s ReplM: %s" % (slug, function, message['path'], message['caption'], reply_markup))
    elif modMsg != None:
        botThreads.addMsgToBot(slug=slug, function=function, msg=msg, reply_markup=reply_markup, singleMsg=singleMsg, delTime=delTime, modMsg=modMsg, priority=True)
        logger.debug("sendMsgToBot - Send: Slug: %s Function: %s msg: %s ReplM: %s" % (slug, function, msg, reply_markup))
    else:
        message = {}
        if singleMsg:
            message = msg
        else:
            if msg != None:
                message['msgLong'] = msg
                message['msgShort'] = msg
            else:
                message['msgLong'] = msgLong
                message['msgShort'] = msgShort
        botThreads.addMsgToBot(slug=slug, function=function, msg=message, reply_markup=reply_markup, singleMsg=singleMsg, delTime=delTime, modMsg="reply_markup", priority=True)
        logger.debug("sendMsgToBot - Send: Slug: %s Function: %s msg: %s ReplM: %s" % (slug, function, msg, reply_markup))

def pushMsgToFront(slug, function): # push all active messages to the front
    for item in botThreads.botData['bot']['messageID']:
        if item['slug'] == slug and item['slug'] == slug:
            with botThreads.threadLock:
                item['newMessageID'] = True

def mainServerMenu(update, context):
    if not checkUserIDValid(update,chatID=CHATID):
        logger.critical("Bot answered to an unknown user: %s / %s: %s, %s" % (update.effective_chat.username, 
                                                                                      update.effective_chat.id, 
                                                                                      update.effective_chat.last_name, 
                                                                                      update.effective_chat.first_name)
                        )
        msgTelegram = "Unauthorized access (ID: %s) from user %s, %s %s" % (update.effective_chat.id,
                                                                                 update.effective_chat.username, 
                                                                                 update.effective_chat.first_name, 
                                                                                 update.effective_chat.last_name
                                                                                 )
        telegramSendMsg(msgTelegram,reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
    
        update.message.reply_text(_('Access denied!'))
        return ConversationHandler.END
    botAddTracking(slug=getBotSlug(update.message.text), 
                   function="messages", 
                   context=context)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtEntry", 
                 message_id=update.message.message_id)
    logger.info("Starting conversation server %s / messageID: %s" % (botGetTracking(context), update.message.message_id))
    pushMsgToFront(botGetTracking(context), "messages")
    sendMsgToBot(slug=botGetTracking(context), 
                 function="messages", 
                 msg="<b>" + _("Server %s selected") % botGetTracking(context) + "...</b>", 
                 reply_markup=getMsgKeyboard())
    return ONE 

def delServerMessage(update, context):
    queryMessageData = update.callback_query.data
    sendDelMessage(queryMessageData)
    return ONE

def mainMenu(update, context):
    if not checkUserIDValid(update,chatID=CHATID):
        logger.critical("Bot answered to an unknown user: %s / %s: %s, %s" % (update.effective_chat.username, 
                                                                                      update.effective_chat.id, 
                                                                                      update.effective_chat.last_name, 
                                                                                      update.effective_chat.first_name)
                        )
        msgTelegram = "Unauthorized access (ID: %s) from user %s, %s %s" % (update.effective_chat.id,
                                                                                 update.effective_chat.username, 
                                                                                 update.effective_chat.first_name, 
                                                                                 update.effective_chat.last_name
                                                                                )
        telegramSendMsg(msgTelegram,reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
    
        update.message.reply_text(_('Access denied!'))
        return ConversationHandler.END
    botAddTracking(slug=getBotSlug(update.message.text), 
                   function="printer", 
                   context=context)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtEntry", 
                 message_id=update.message.message_id)
    logger.debug("Starting conversation for printer %s / messageID: %s" % (botGetTracking(context), update.message.message_id))
    pushMsgToFront(botGetTracking(context), "printer")
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Printer %s selected") % botGetTracking(context) + "...</b>", 
                 reply_markup=getStartKeyboard(checkStartKeys(botGetTracking(context))))
    return ONE 

def extCommands(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening external commands") + "...</b>", 
                 reply_markup=getKeyboard(getExtCommands()))
    return TWO

def extCommandsBack(update,context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Back to main menu...") + "...</b>", 
                 reply_markup=getStartKeyboard(checkStartKeys(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="extCommands", 
                 removeMsg=True)
    sendMsgToBot(botGetTracking(context), 
                 "quickCommands", 
                 removeMsg=True)
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintQueue", 
                 removeMsg=True)    
    return ONE

def extCommandsChoosen(update,context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening external command confirmation") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="extCommands", 
                 msg=getExtCommandsConfirmText(int(update.callback_query.data)), 
                 reply_markup=getKeyboard(getExtCommandsConfirmButton(int(update.callback_query.data))))
    return THREE

def extCommandAction(update,context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Going back to external commands") + "...</b>", 
                 reply_markup=getKeyboard(getExtCommands()))
    sendExtCommand(queryMessageData.text)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="extCommands", 
                 removeMsg=True)
    return TWO

def webcams(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening webcams") + "...</b>", 
                 reply_markup=getKeyboard(getWebcamConfig(botGetTracking(context), update)))
    return FOUR

def webcamSendVideo(update, context):
    queryData = update.callback_query.data
    botRemTracking()
    botThreads.startWebcamThread(slug=botGetTracking(context),
                                name="process_video", 
                                type="vid", 
                                queryData=queryData)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Generate video file. Closing keyboard") + "...</b>", 
                 reply_markup=None)
    return ConversationHandler.END

def webcamSendGif(update, context):
    queryData = update.callback_query.data
    botRemTracking()
    botThreads.startWebcamThread(slug=botGetTracking(context),
                                name="process_gif", 
                                type="gif", 
                                queryData=queryData)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Generate gif file. Closing keyboard") + "...</b>", 
                 reply_markup=None)
    return ConversationHandler.END

def webcamSendPng(update, context):
    queryData = update.callback_query.data
    botRemTracking()
    botThreads.startWebcamThread(slug=botGetTracking(context),
                                name="process_png", 
                                type="pic", 
                                queryData=queryData)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Get pic. Closing keyboard") + "...</b>", 
                 reply_markup=None)
    return ConversationHandler.END

def quickCommands(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening quick commands") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="quickCommands", 
                 msg=getQuickCommandsText(botGetTracking(context)), 
                 reply_markup=getKeyboard(getQuickCommandsButton(botGetTracking(context))))
    return EIGHT

def prinQuickCommand(update, context):
    queryData = update.callback_query.data
    botRemTracking()
    sendQuickCommand(botGetTracking(context),queryData)
    sendMsgToBot(botGetTracking(context), 
                 "quickCommands", 
                 removeMsg=True)
    return ConversationHandler.END

def settings(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    return FIVE

def settingsBack(update,context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context)))) 
    remAllExtraMsgs(botGetTracking(context))
    return FIVE

def extrSetLimit(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening extruder set limit") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="extrSetLimit", 
                 msg=getExtrSetLimitText(botGetTracking(context)), 
                 reply_markup=getKeyboard())
    return SIX

def extrSetLimitValue(update, context):
    messageData = update.message
    sendMsgToBot(botGetTracking(context), 
                 "extrSetLimit", 
                 removeMsg=True)
    setExtrSetLimit(botGetTracking(context),messageData.text)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtExtrSetLimitValue", 
                 message_id=messageData.message_id)
    return FIVE

def prinExtCommOff(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening extruder command at set limit") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="prinExtComm", 
                 msg=getPrinExtCommText(botGetTracking(context)), 
                 reply_markup=getKeyboard(getExtComAndDisableButton()))
    return SEVEN

def prinExtCommOffItem(update, context):
    queryMessage = update.callback_query.message
    queryData = update.callback_query.data
    setPrinExtComm(botGetTracking(context),queryData)
    sendMsgToBot(botGetTracking(context), 
                 "prinExtComm", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    return FIVE

def heatbSetLimit(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening heatbed set limit") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="heatbSetLimit", 
                 msg=getHeatbSetLimitText(botGetTracking(context)), 
                 reply_markup=getKeyboard())
    return ELEVEN

def heatbSetLimitValue(update, context):
    messageData = update.message
    sendMsgToBot(botGetTracking(context), 
                 "heatbSetLimit", 
                 removeMsg=True)
    setHeatbSetLimit(botGetTracking(context),messageData.text)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtheatbSetLimitValue", 
                 message_id=messageData.message_id)
    return FIVE

def prinHeatbCommOff(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening heatbed command at set limit") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="prinHeatbComm", 
                 msg=getPrinExtCommText(botGetTracking(context)), 
                 reply_markup=getKeyboard(getExtComAndDisableButton()))
    return TWELVE

def prinHeatbCommOffItem(update, context):
    queryMessage = update.callback_query.message
    queryData = update.callback_query.data
    setPrinHeatbComm(botGetTracking(context),queryData)
    sendMsgToBot(botGetTracking(context), 
                 "prinHeatbComm", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    return FIVE

def afterPrintTime(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening after print send picture time delay") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="afterPrintTime", 
                 msg=getAfterPrintTimeText(botGetTracking(context)), 
                 reply_markup=getKeyboard())
    return NINE

def afterPrintTimeValue(update, context):
    messageData = update.message
    sendMsgToBot(botGetTracking(context), 
                 "afterPrintTime", 
                 removeMsg=True)
    setAfterPrintTimeValue(botGetTracking(context),messageData.text)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtAfterPrintTimeValue", 
                 message_id=messageData.message_id)
    return FIVE

def afterPrintWebcam(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening after print send picture select webcam") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="afterPrintWebcam", 
                 msg=getAfterPrintWebcamText(botGetTracking(context)), 
                 reply_markup=getKeyboard(getAfterPrintWebcamAndDisableButton(botGetTracking(context))))
    return TEN

def afterPrintWebcamItem(update, context):
    queryMessage = update.callback_query.message
    queryData = update.callback_query.data
    setAfterPrintWebcam(botGetTracking(context),queryData)
    sendMsgToBot(botGetTracking(context), 
                 "afterPrintWebcam", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    return FIVE

def zHeightPrintPicHeight(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening z height picture") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="zHeightPrintPicHeight", 
                 msg=getZHeightPrintPicText(botGetTracking(context)), 
                 reply_markup=getKeyboard())
    return THIRTEEN

def zHeightPrintPicValue(update, context):
    messageData = update.message
    sendMsgToBot(botGetTracking(context), 
                 "zHeightPrintPicHeight", 
                 removeMsg=True)
    setZHeightValue(botGetTracking(context),messageData.text)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtZHeightPrintPicValue", 
                 message_id=messageData.message_id)
    return FIVE

def zHeightPrintPicCamSelect(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening z height picture select webcam") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="zHeightPrintPicCam", 
                 msg=getZHeightPrintPicCamText(botGetTracking(context)), 
                 reply_markup=getKeyboard(getZHeightPrintWebcamAndDisableButton(botGetTracking(context))))
    return FOURTEEN

def zHeightPrintPicCamSelectItem(update, context):
    queryMessage = update.callback_query.message
    queryData = update.callback_query.data
    setZHeightPrintPicCam(botGetTracking(context),queryData)
    sendMsgToBot(botGetTracking(context), 
                 "zHeightPrintPicCam", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    return FIVE

def timeBasedPrintPic(update, context):
    queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening time based pic") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="timeBasedPrintPic", 
                 msg=getTimeBasedPrintPicText(botGetTracking(context)), 
                 reply_markup=getKeyboard())
    return FIFTEEN

def timeBasedPrintPicValue(update, context):
    messageData = update.message
    sendMsgToBot(botGetTracking(context), 
                 "timeBasedPrintPic", 
                 removeMsg=True)
    setTimeBasedPrintPic(botGetTracking(context),messageData.text)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAttimeBasedPrintPicValue", 
                 message_id=messageData.message_id)
    return FIVE

def timeBasedPrintPicCamSelect(update, context):
    #queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening after print send picture select webcam") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="timeBasedPrintPicCam", 
                 msg=getTimeBasedPrintPicCamText(botGetTracking(context)), 
                 reply_markup=getKeyboard(getTimeBasedPrintWebcamAndDisableButton(botGetTracking(context))))
    return SIXTEEN

def timeBasedPrintPicCamSelectItem(update, context):
    #queryMessage = update.callback_query.message
    queryData = update.callback_query.data
    setTimeBasedPrintPicCam(botGetTracking(context),queryData)
    sendMsgToBot(botGetTracking(context), 
                 "timeBasedPrintPicCam", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening settings") + "...</b>", 
                 reply_markup=getKeyboard(getSettingsButton(botGetTracking(context))))
    return FIVE

def handlePrint(update, context):
    remAllExtraMsgs(botGetTracking(context))
    listPrinters = botThreads.getPrinterDataStorage(botGetTracking(context), "listPrinter")
    if listPrinters['job'] == "none":
        sendMsgToBot(slug=botGetTracking(context), 
                     function="printer", 
                     msg="<b>🔜 " + _("Opening printer control") + "...</b>", 
                     reply_markup=getKeyboard(getStartPrintButton(botGetTracking(context))))
        return SEVENTEEN
    else:
        sendMsgToBot(slug=botGetTracking(context), 
                     function="printer", 
                     msg="<b>🔜 " + _("Opening print handling") + "...</b>", 
                     reply_markup=getKeyboard(getHandlePrintButton(botGetTracking(context))))
        return EIGHTTEEN

def handlePrintQueue(update,context):
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening printer queue") + "...</b>", 
                 reply_markup=None)
    msgText = getPrintQueueText(botGetTracking(context),0)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintQueue", 
                 msg=msgText, 
                 reply_markup=getKeyboard(getPrintQueueButton(botGetTracking(context),0)))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintQueue", 
                 msg=getPreviewPicSetting(msgText),
                 delTime=1,
                 vidPic=None,
                 reply_markup=getKeyboard(getPrintQueueButton(botGetTracking(context),0)),
                 modMsg="print_pic")
    return TWENTYONE

def movePrintQueue(update,context):
    queryMessageData = update.callback_query.data
    pos = int(queryMessageData.split()[1])
    print(pos)
    msgText = getPrintQueueText(botGetTracking(context),pos)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintQueue", 
                 msg=msgText, 
                 reply_markup=getKeyboard(getPrintQueueButton(botGetTracking(context),pos)))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintQueue", 
                 msg=getPreviewPicSetting(msgText),
                 delTime=1,
                 vidPic=None,
                 reply_markup=getKeyboard(getPrintQueueButton(botGetTracking(context),pos)),
                 modMsg="print_pic")
    return TWENTYONE

def handlePrintSelection(update,context):
    queryMessageData = update.callback_query.data
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintQueue", 
                 msg="<b>🔜 " + _("Opening printer file") + "...</b>", 
                 reply_markup=None)
    msgText, fileID = getPrintSelectData(botGetTracking(context),queryMessageData)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintQueue", 
                 msg=msgText, 
                 reply_markup=getKeyboard(getPrintSelectionButton(botGetTracking(context),fileID)))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintQueue", 
                 msg=msgText,
                 delTime=1,
                 vidPic=None,
                 reply_markup=getKeyboard(getPrintSelectionButton(botGetTracking(context),fileID)),
                 modMsg="print_pic")
    return TWENTYTWO

def startSelectedPrint(update, context):
    queryMessageData = update.callback_query.data
    sendStartPrint(botGetTracking(context), queryMessageData)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintQueue", 
                 msg="<i>🔜 " + _("Closing keyboard") + "...</i>", 
                 reply_markup=None)
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintQueue", 
                 removeMsg=True)
    botRemTracking()
    remAllExtraMsgs(botGetTracking(context))
    logger.info("Bot start print: %s (%s): %s, %s" 
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

def handlePrintCancel(update,context):
    #queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening cancel print confirmation") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintCancel", 
                 msg="<b>⚠️ " + _("Do you really want to cancel the print?") + "</b>", 
                 reply_markup=getKeyboard(getOKButton()))
    return NINETEEN

def handlePrintCancelAction(update, context):
    sendCancelPrint(botGetTracking(context))
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintCancel", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Closing cancel message") + "...</b>", 
                 reply_markup=getStartKeyboard(checkStartKeys(botGetTracking(context))))
    return ONE

def handlePrintFMultiply(update,context):
    #queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening flow multiplier") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintFMultiply", 
                 msg=getFMultiplyText(botGetTracking(context)), 
                 reply_markup=getKeyboard(setFMultiplyButton()))
    return TWENTY

def handlePrintFMultiplyActionText(update, context):
    messageData = update.message
    setFMultiply(botGetTracking(context),messageData.text)
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintFMultiply", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Closing flow multiplier") + "...</b>", 
                 reply_markup=getStartKeyboard(checkStartKeys(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtHandlePrintFMultiplyAction", 
                 message_id=messageData.message_id)
    return ONE

def handlePrintFMultiplyActionButton(update, context):
    queryMessageData = update.callback_query.data
    print(queryMessageData)
    setFMultiply(botGetTracking(context),queryMessageData,False)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintFMultiply", 
                 msg="<b>🔜 " + _("Waiting for flow update") + "...</b>", 
                 reply_markup=None)
    sendDelayMessage(botGetTracking(context),"handlePrintFMultiply",None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintFMultiply", 
                 msg=getFMultiplyText(botGetTracking(context)), 
                 reply_markup=getKeyboard(setFMultiplyButton()))
    return TWENTY

def handlePrintSMultiply(update,context):
    #queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening speed multiplier") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintSMultiply", 
                 msg=getSMultiplyText(botGetTracking(context)), 
                 reply_markup=getKeyboard(setFMultiplyButton()))
    return TWENTYFOUR

def handlePrintSMultiplyActionText(update, context):
    messageData = update.message
    setSMultiply(botGetTracking(context),messageData.text)
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintSMultiply", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Closing speed multiplier") + "...</b>", 
                 reply_markup=getStartKeyboard(checkStartKeys(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtHandlePrintSMultiplyAction", 
                 message_id=messageData.message_id)
    return ONE

def handlePrintSMultiplyActionButton(update, context):
    queryMessageData = update.callback_query.data
    print(queryMessageData)
    setSMultiply(botGetTracking(context),queryMessageData,False)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintSMultiply", 
                 msg="<b>🔜 " + _("Waiting for speed update") + "...</b>", 
                 reply_markup=None)
    sendDelayMessage(botGetTracking(context),"handlePrintSMultiply",None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintSMultiply", 
                 msg=getSMultiplyText(botGetTracking(context)), 
                 reply_markup=getKeyboard(setFMultiplyButton()))
    return TWENTYFOUR

def handlePrintFSpeed(update,context):
    queryMessageData = update.callback_query.data
    botSetSpecialData(context,int(queryMessageData.split()[1]))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening fan speed") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintFSpeed", 
                 msg=getPrintFSpeedText(botGetTracking(context),queryMessageData), 
                 reply_markup=getKeyboard(setPrintFSpeedButton(queryMessageData)))
    return TWENTYFIVE

def handlePrintFSpeedActionText(update, context):
    messageData = update.message
    setFSpeed(botGetTracking(context),messageData.text,typedValue=True,fanID=botGetSpecialData(context))
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintFSpeed", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Closing fan speed") + "...</b>", 
                 reply_markup=getStartKeyboard(checkStartKeys(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtHandlePrintFSpeedAction", 
                 message_id=messageData.message_id)
    return ONE

def handlePrintFSpeedActionButton(update, context):
    queryMessageData = update.callback_query.data
    setFSpeed(botGetTracking(context),queryMessageData)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintFSpeed", 
                 msg="<b>🔜 " + _("Waiting for fan speed update") + "...</b>", 
                 reply_markup=None)
    sendDelayMessage(botGetTracking(context),"handlePrintFSpeed",None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintFSpeed", 
                 msg=getPrintFSpeedText(botGetTracking(context),queryMessageData), 
                 reply_markup=getKeyboard(setPrintFSpeedButton(queryMessageData)))
    return TWENTYFIVE

def handlePrintETemp(update,context):
    queryMessageData = update.callback_query.data
    botSetSpecialData(context,int(queryMessageData.split()[1]))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening extruder temperature") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintETemp", 
                 msg=getPrintETempText(botGetTracking(context),botGetSpecialData(context)), 
                 reply_markup=getKeyboard(setETempButton()))
    return TWENTYSIX

def handlePrintETempActionText(update, context):
    messageData = update.message
    setETemp(botGetTracking(context),messageData.text,typedValue=True,extrID=botGetSpecialData(context))
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintETemp", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Closing extruder temperature") + "...</b>", 
                 reply_markup=getStartKeyboard(checkStartKeys(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtHandlePrintETempAction", 
                 message_id=messageData.message_id)
    return ONE

def handlePrintETempActionButton(update, context):
    queryMessageData = update.callback_query.data
    setETemp(botGetTracking(context),queryMessageData,typedValue=False,extrID=botGetSpecialData(context))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintETemp", 
                 msg="<b>🔜 " + _("Waiting for extruder temperature update") + "...</b>", 
                 reply_markup=None)
    sendDelayMessage(botGetTracking(context),"handlePrintETemp",None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintETemp", 
                 msg=getPrintETempText(botGetTracking(context),botGetSpecialData(context)), 
                 reply_markup=getKeyboard(setETempButton()))
    return TWENTYSIX

def handlePrintBTemp(update,context):
    queryMessageData = update.callback_query.data
    botSetSpecialData(context,int(queryMessageData.split()[1]))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening heatbed temperature") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintBTemp", 
                 msg=getPrintBTempText(botGetTracking(context),botGetSpecialData(context)), 
                 reply_markup=getKeyboard(setBTempButton()))
    return TWENTYSEVEN

def handlePrintBTempActionText(update, context):
    messageData = update.message
    setBTemp(botGetTracking(context),messageData.text,typedValue=True,heatbID=botGetSpecialData(context))
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintBTemp", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Closing heatbed temperature") + "...</b>", 
                 reply_markup=getStartKeyboard(checkStartKeys(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtHandlePrintBTempAction", 
                 message_id=messageData.message_id)
    return ONE

def handlePrintBTempActionButton(update, context):
    queryMessageData = update.callback_query.data
    setBTemp(botGetTracking(context),queryMessageData,typedValue=False,heatbID=botGetSpecialData(context))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintBTemp", 
                 msg="<b>🔜 " + _("Waiting for heatbed temperature update") + "...</b>", 
                 reply_markup=None)
    sendDelayMessage(botGetTracking(context),"handlePrintBTemp",None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintBTemp", 
                 msg=getPrintBTempText(botGetTracking(context),botGetSpecialData(context)), 
                 reply_markup=getKeyboard(setBTempButton()))
    return TWENTYSEVEN

def handlePrintCTemp(update,context):
    queryMessageData = update.callback_query.data
    botSetSpecialData(context,int(queryMessageData.split()[1]))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening chamber temperature") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintCTemp", 
                 msg=getPrintCTempText(botGetTracking(context),botGetSpecialData(context)), 
                 reply_markup=getKeyboard(setBTempButton()))
    return TWENTYEIGHT

def handlePrintCTempActionText(update, context):
    messageData = update.message
    setBTemp(botGetTracking(context),messageData.text,typedValue=True,heatbID=botGetSpecialData(context))
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintCTemp", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Closing chamber temperature") + "...</b>", 
                 reply_markup=getStartKeyboard(checkStartKeys(botGetTracking(context))))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtHandlePrintCTempAction", 
                 message_id=messageData.message_id)
    return ONE

def handlePrintCTempActionButton(update, context):
    queryMessageData = update.callback_query.data
    setBTemp(botGetTracking(context),queryMessageData,typedValue=False,heatbID=botGetSpecialData(context))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintCTemp", 
                 msg="<b>🔜 " + _("Waiting for chamber temperature update") + "...</b>", 
                 reply_markup=None)
    sendDelayMessage(botGetTracking(context),"handlePrintCTemp",None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintCTemp", 
                 msg=getPrintCTempText(botGetTracking(context),botGetSpecialData(context)), 
                 reply_markup=getKeyboard(setBTempButton()))
    return TWENTYEIGHT

def handlePrintEStop(update,context):
    #queryMessageData = update.callback_query.message
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Opening emergency stop confirmation") + "...</b>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="handlePrintEStop", 
                 msg="<b>⚠️ " + _("Do you really want to emergency stop the printer?") + "</b>", 
                 reply_markup=getKeyboard(getOKButton()))
    return TWENTY

def handleEmStopAction(update, context):
    sendEmStop(botGetTracking(context))
    sendMsgToBot(botGetTracking(context), 
                 "handlePrintEStop", 
                 removeMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<b>🔜 " + _("Closing emergency stop message") + "...</b>", 
                 reply_markup=getKeyboard(getHandlePrintButton(botGetTracking(context))))
    return EIGHTTEEN

def exitBot(update, context):
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg="<i>🔜 " + _("Closing keyboard") + "...</i>", 
                 reply_markup=None)
    botRemTracking()
    remAllExtraMsgs(botGetTracking(context))
    logger.info("Bot finished conversation: %s (%s): %s, %s" 
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

def unknownCommand(update, context):  
    botRemTracking()
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg= "<i>" + _("Closing keyboard") + "...</i>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="unknownCommand", 
                 msg= "<b>🚫 " + _("Didn´t get ya, maaaaan...What is") + " \"<i>%s</i>\" ⁉️</b>" % update.message.text, 
                 reply_markup=None,
                 singleMsg=True)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtUnknownCommand", 
                 message_id=update.message.message_id)
    logger.info("unknownCommand: Bot doesn´t know the answer: %s" % update.message.text)
    return ConversationHandler.END

def botTimeout(update, context):
    botRemTracking()
    sendMsgToBot(slug=botGetTracking(context), 
                 function="printer", 
                 msg= "<i>" + _("Closing keyboard") + "...</i>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="botTimeout", 
                 msg= "<b>📣 " + _("Don´t sleep, please...wake up") + ", %s</b>" % update.effective_chat.first_name, 
                 reply_markup=None,
                 singleMsg=True)
    remAllExtraMsgs(botGetTracking(context))
    logger.info("Conversations timeout")
    return ConversationHandler.END

def exitMessageBot(update, context):
    sendMsgToBot(slug=botGetTracking(context), 
                 function="messages", 
                 msg="<i>🔜 " + _("Closing keyboard") + "...</i>", 
                 reply_markup=None)
    botRemTracking()
    remAllExtraMsgs(botGetTracking(context))
    logger.debug("Bot finished conversation: %s (%s): %s, %s" 
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

def botMessagesTimeout(update, context):   
    botRemTracking()
    sendMsgToBot(slug=botGetTracking(context), 
                 function="messages", 
                 msg= "<i>" + _("Closing keyboard") + "...</i>", 
                 reply_markup=None)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="botMessagesTimeout", 
                 msg= "<b>📣 " + _("Don´t sleep, please...wake up") + ", %s</b>" % update.effective_chat.first_name, 
                 reply_markup=None,
                 singleMsg=True)
    remAllExtraMsgs(botGetTracking(context))
    logger.info("Conversations timeout")
    return ConversationHandler.END

def resetMsgs(update, context):
    sendMsgToBot(slug="bot", 
                 function="resetMsgs", 
                 message_id=update.message.message_id)
    for item in botThreads.botData['bot']['messageID']:
        with botThreads.threadLock:
            item['dailyRenew'] = True
    sendMsgToBot(slug="bot", 
                 function="resetMsgs", 
                 msg= "<b>📣 " + _("Reset, reset") + "🎶...🎶 " + _("everyone comes back") + "🎵... 🎵" + _("hopefully") + ", %s</b>" % update.effective_chat.first_name, 
                 reply_markup=None,
                 singleMsg=True)
    return ConversationHandler.END

def remAllExtraMsgs(slug):
    for message in botThreads.botData['bot']['messageID']:
        if message['function'] != "printer" and message['function'] != "server" and message['function'] != "messages":
            botThreads.remMsgFromBot(slug, message['function'])

# Remove Printer from Bot manually

def remPrinterFromBot(telegramDispatcher):
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("remove", remPrintFromBotContext)
                    ],
    states={
        ONE: [CallbackQueryHandler(exitRemPrintFromBotContext, pattern="^End$"), # Start conversation database
              CallbackQueryHandler(removePrinter)
                ],
        ConversationHandler.TIMEOUT:[MessageHandler(Filters.all, timeoutRemPrintFromBotContext)],       
            },
    fallbacks=[MessageHandler(Filters.all, exitRemPrintFromBotContext)],
    allow_reentry=False,
    conversation_timeout=60,
    name="Repetier-Server-RemPrinter"
    )
    telegramDispatcher.add_handler(conv_handler)
    logger.info("addHandler: Added handler remove printer handler")

def remPrintFromBotContext(update, context):
    if not checkUserIDValid(update,chatID=CHATID):
        logger.critical("Bot answered to an unknown user: %s / %s: %s, %s" % (update.effective_chat.username, 
                                                                                      update.effective_chat.id, 
                                                                                      update.effective_chat.last_name, 
                                                                                      update.effective_chat.first_name)
                        )
        msgTelegram = "Unauthorized access (ID: %s) from user %s, %s %s" % (update.effective_chat.id,
                                                                                 update.effective_chat.username, 
                                                                                 update.effective_chat.first_name, 
                                                                                 update.effective_chat.last_name
                                                                                )
        telegramSendMsg(msgTelegram,reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
    
        update.message.reply_text(_('Access denied!'))
        return ConversationHandler.END
    botAddTracking(slug=getBotSlug(update.message.text), 
                   function="remPrinterFromBot", 
                   context=context)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtEntry", 
                 message_id=update.message.message_id)
    logger.debug("Starting remove printer conversation messageID: %s" % (update.message.message_id))
    sendMsgToBot(slug=getBotSlug(update.message.text), 
                 function="remPrinterFromBot", 
                 msg=_("Please choose printer to remove from Bot :"), 
                 reply_markup=getStartKeyboard(getRemPrinterFromBotKeyboard()))
    return ONE 

def removePrinter(update, context):
    selectedPrinter = update.callback_query.data
    logger.info("removePrinter request remove printer: %s" % (selectedPrinter))
    for printer in botThreads.botData['printers']:
        if selectedPrinter == printer:
            sendMsgToBot(slug=printer, 
                        function="removePrinterInfo", 
                        msg="<i>" + _("Removing %s printer from bot") % (printer) + "</i>", 
                        reply_markup=None,
                        singleMsg=True,
                        delTime=5)
            printerData = botThreads.botData['printers'][printer]
            for printThread in botThreads.botData['printers'][printer]['threads']:
                botThreads.botData['printers'][printer]['threads'][printThread].stop()
            for printMsg in botThreads.botData['bot']['messageID']:
                if printMsg['slug'] == printer:
                    sendMsgToBot(slug=printMsg['slug'],function=printMsg['function'],message_id=printMsg['message_id'])                    
            botThreads.savePrinterConfigFile()
    sendMsgToBot(botGetTracking(context), "remPrinterFromBot", removeMsg=True)
    botRemTracking()
    logger.debug("Bot ends remove printer conversation: %s (%s): %s, %s"
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

    #for file in os.listdir(LOGFILEFOLDER):
    #    if file.startswith(fileStart):
    #        sendMsgToBot(botGetTracking(context), file, path=os.path.join(LOGFILEFOLDER, file), caption=file, vidPic="file",)
    #caption = "<i>" + _("Actual system configuration") + "</i>\n<strong>" + _("Please check the system configuration. Otherwise modify or delete items which you won´t distribute to third persons!") + "</strong>\n\n" + _("Please send files to telegram group for support: ") + "\n\n<a href=\"https://t.me/Repetier_S_Telegram_Bot_Support\">Telegram Bot Support Group</a>"
    #sendMsgToBot(slug=botGetTracking(context), function=file, path=getSystemDebugConfig(), caption=caption, vidPic="file",)
    #return ONE

def exitRemPrintFromBotContext(update, context):
    sendMsgToBot(botGetTracking(context), "remPrinterFromBot", removeMsg=True)
    botRemTracking()
    logger.debug("Bot ends remove printer conversation: %s (%s): %s, %s"
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

def timeoutRemPrintFromBotContext(update, context):
    sendMsgToBot(botGetTracking(context), "remPrinterFromBot", removeMsg=True)
    botRemTracking()
    logger.debug("Bot timeout remove printer conversation: %s (%s): %s, %s" 
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

# Bot & Repetier Server stats

def repetierBotStats(telegramDispatcher):
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("stats", repetierBotStatsContext)
                    ],
    states={
        ONE: [CallbackQueryHandler(exitRepetierBotStatsContext, pattern="^End$"), # Start conversation database
              CallbackQueryHandler(switchStatsYear)
                ],
        ConversationHandler.TIMEOUT:[MessageHandler(Filters.all, timeoutDebugFileUpload)],       
            },
    fallbacks=[MessageHandler(Filters.all, timeoutRepetierBotStatsContext)],
    allow_reentry=False,
    conversation_timeout=60,
    name="Repetier-Server-Stats"
    )
    telegramDispatcher.add_handler(conv_handler)
    logger.info("addHandler: Added handler stats handler")

def repetierBotStatsContext(update, context):
    if not checkUserIDValid(update,chatID=CHATID):
        logger.critical("Bot answered to an unknown user: %s / %s: %s, %s" % (update.effective_chat.username, 
                                                                                      update.effective_chat.id, 
                                                                                      update.effective_chat.last_name, 
                                                                                      update.effective_chat.first_name)
                        )
        msgTelegram = "Unauthorized access (ID: %s) from user %s, %s %s" % (update.effective_chat.id,
                                                                                 update.effective_chat.username, 
                                                                                 update.effective_chat.first_name, 
                                                                                 update.effective_chat.last_name
                                                                                )
        telegramSendMsg(msgTelegram,reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
    
        update.message.reply_text(_('Access denied!'))
        return ConversationHandler.END
    botAddTracking(slug=getBotSlug(update.message.text), 
                   function="repetierBotStats", 
                   context=context)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtEntry", 
                 message_id=update.message.message_id)
    logger.debug("Starting statistic conversation messageID: %s" % (update.message.message_id))
    sendMsgToBot(slug=getBotSlug(update.message.text), 
                 function="repetierBotStats", 
                 msg="<i>" + _("Load statistics from Bot :") + "</i>", 
                 reply_markup=None)
    date = arrow.now()
    sendMsgToBot(slug=getBotSlug(update.message.text), 
                 function="repetierBotStats", 
                 msg=getStatisticEntryText(date.year), 
                 reply_markup=getStartKeyboard(getRepetierBotStatsKeyboard()))
    return ONE 

def switchStatsYear(update, context):
    selectedYear = update.callback_query.data
    logger.info("switch stats year to: %s" % (selectedYear))
    sendMsgToBot(slug=botGetTracking(context), 
                 function="repetierBotStats", 
                 msg=getStatisticEntryText(selectedYear), 
                 reply_markup=getStartKeyboard(getRepetierBotStatsKeyboard()))
    return ONE

    for file in os.listdir(LOGFILEFOLDER):
        if file.startswith(fileStart):
            sendMsgToBot(botGetTracking(context), file, path=os.path.join(LOGFILEFOLDER, file), caption=file, vidPic="file",)
    caption = "<i>" + _("Actual system configuration") + "</i>\n<strong>" + _("Please check the system configuration. Otherwise modify or delete items which you won´t distribute to third persons!") + "</strong>\n\n" + _("Please send files to telegram group for support: ") + "\n\n<a href=\"https://t.me/Repetier_S_Telegram_Bot_Support\">Telegram Bot Support Group</a>"
    sendMsgToBot(slug=botGetTracking(context), function=file, path=getSystemDebugConfig(), caption=caption, vidPic="file",)
    return ONE

def exitRepetierBotStatsContext(update, context):
    sendMsgToBot(botGetTracking(context), "repetierBotStats", removeMsg=True)
    botRemTracking()
    logger.debug("Bot ends statistic conversation: %s (%s): %s, %s"
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

def timeoutRepetierBotStatsContext(update, context):
    sendMsgToBot(botGetTracking(context), "repetierBotStats", removeMsg=True)
    botRemTracking()
    logger.debug("Bot timeout statistic conversation: %s (%s): %s, %s" 
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

# Support 

def addDebugHandler(telegramDispatcher):
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("debug", debugFileUpload)
                    ],
    states={
        ONE: [CallbackQueryHandler(exitDebugFileUpload, pattern="^End$"), # Start conversation database
              CallbackQueryHandler(uploadDebugDatabaseUpload, pattern="^database$"),
              CallbackQueryHandler(uploadDebugActiveThreads, pattern="^threads$"),
              CallbackQueryHandler(uploadDebugFileUpload)
             ],
        ConversationHandler.TIMEOUT:[MessageHandler(Filters.all, timeoutDebugFileUpload)],       
            },
    fallbacks=[MessageHandler(Filters.all, exitDebugFileUpload)],
    allow_reentry=False,
    conversation_timeout=60,
    name="Repetier-Server-Debug"
    )
    telegramDispatcher.add_handler(conv_handler)
    logger.info("addHandler: Added handler debug handler")

def debugFileUpload(update, context):
    if not checkUserIDValid(update,chatID=CHATID):
        logger.critical("Bot answered to an unknown user: %s / %s: %s, %s" % (update.effective_chat.username, 
                                                                                      update.effective_chat.id, 
                                                                                      update.effective_chat.last_name, 
                                                                                      update.effective_chat.first_name)
                        )
        msgTelegram = "Unauthorized access (ID: %s) from user %s, %s %s" % (update.effective_chat.id,
                                                                                 update.effective_chat.username, 
                                                                                 update.effective_chat.first_name, 
                                                                                 update.effective_chat.last_name
                                                                                )
        telegramSendMsg(msgTelegram,reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
    
        update.message.reply_text(_('Access denied!'))
        return ConversationHandler.END
    botAddTracking(slug=getBotSlug(update.message.text), 
                   function="debugFileUpload", 
                   context=context)
    sendMsgToBot(slug=botGetTracking(context), 
                 function="RemoveAtEntry", 
                 message_id=update.message.message_id)
    logger.debug("Starting debug conversation messageID: %s" % (update.message.message_id))
    sendMsgToBot(slug=getBotSlug(update.message.text), 
                 function="logfileUpload", 
                 msg=_("Please choose file to upload :"), 
                 reply_markup=getStartKeyboard(getLogfilesKeyboard()))
    return ONE 
    
def uploadDebugFileUpload(update, context):
    selectedLog = update.callback_query.data
    logger.info("uploadDebugFileUpload request file: %s" % (selectedLog))
    fileStart = selectedLog.replace(FILENAME_NO_EXTENSION + '.log', "")
    for file in os.listdir(LOGFILEFOLDER):
        if file.startswith(fileStart):
            sendMsgToBot(botGetTracking(context), file, path=os.path.join(LOGFILEFOLDER, file), caption=file, vidPic="file",)
    caption = "<i>" + _("Actual system configuration") + "</i>\n<strong>" + _("Please check the system configuration. Otherwise modify or delete items which you won´t distribute to third persons!") + "</strong>\n\n" + _("Please send files to telegram group for support: ") + "\n\n<a href=\"https://t.me/Repetier_S_Telegram_Bot_Support\">Telegram Bot Support Group</a>"
    sendMsgToBot(slug=botGetTracking(context), function=file, path=getSystemDebugConfig(), caption=caption, vidPic="file",)
    return ONE

def uploadDebugDatabaseUpload(update, context):
    logger.info("uploadDebugDatabaseUpload request database")
    DATABASEFILENAME = os.path.join(LOGFILEFOLDER, Uhrzeit.format(now) + "_" + FILENAME_NO_EXTENSION + '.dbase')
    with open(DATABASEFILENAME, 'w') as outfile:
            json.dump(botThreads.botData, outfile, default=lambda o: '<not serializable>')
    try:
        caption = "<i>" + _("Actual database") + "</i>"
        sendMsgToBot(slug=botGetTracking(context), function="Actual database", path=DATABASEFILENAME, caption=caption, vidPic="file",)
    except:
            logger.error("Configuration file could not be saved")
    return ONE

def uploadDebugActiveThreads(update, context):
    logger.info("Debug check threads. Active threads: %d / %s" % (threading.active_count(), threading.enumerate()))
    msg="<b>"+_("Active threads")+": %d</b>\n" % (threading.active_count())
    for actThreads in threading.enumerate():
        strThread=str(actThreads)
        msg+="<b>*</b> <code>" + str(strThread[1:-1]) + "</code>\n"
    sendMsgToBot(slug="Bot", 
                function="activeThreads", 
                msg=msg, 
                reply_markup=None,
                singleMsg=True,
                delTime=20)
    return ONE

def exitDebugFileUpload(update, context):
    sendMsgToBot(botGetTracking(context), "RemoveAtExit", message_id=update.callback_query.message.message_id)
    sendMsgToBot(botGetTracking(context), "logfileUpload", removeMsg=True)
    botRemTracking()
    logger.debug("Bot ends debug conversation: %s (%s): %s, %s"
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
    return ConversationHandler.END

def timeoutDebugFileUpload(update, context):
    sendMsgToBot(botGetTracking(context), "logfileUpload", removeMsg=True)
    botRemTracking()
    logger.debug("Bot timeout debug conversation: %s (%s): %s, %s" 
                 % (update.effective_chat.username, update.effective_chat.id, update.effective_chat.last_name, update.effective_chat.first_name))
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

# Threading

class ProgramKilled(Exception):
    pass

def signal_handler(signum, frame):
    raise ProgramKilled

class dataHdlThread(threading.Thread):
    def __init__(self, interval, execute, name, addData = None, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = timedelta(seconds=interval)
        self.execute = execute
        self.name = name
        self.addData = addData
        self.args = args
        self.kwargs = kwargs
        loggerWS.info("Thread init: %s" % self.name)

        self.threadInterval = interval
        self.threadState = None
        self.updateTime = arrow.now()
        
    def stop(self):
        self.stopped.set()
        self.join()        
        loggerWS.info("Thread %s terminated - Ident: %s / ID: %s" % (self.getName(), self.ident, self.native_id))
        
    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)

    def updateReferenceTime(self):
        self.updateTime = arrow.now()
        loggerWS.debug("Action thread %s update reference time: %s" % (self.getName(), self.updateTime))
     

    def modifyInterval(self, newInterval): # interval in seconds
        if newInterval != self.threadInterval:
            self.interval = timedelta(seconds=newInterval)
            self.threadInterval = newInterval
            loggerWS.info("Thread %s interval changed to: %s - Ident: %s / ID: %s" % (self.getName(), self.interval, self.ident, self.native_id)) 

class actionThread(threading.Thread):
    def __init__(self, interval, execute, name, slug, function, threadFlex=True, addData = None, messageID = None, chatID = CHATID, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = timedelta(seconds=interval)
        self.execute = execute
        self.threadFlex = threadFlex
        self.name = name
        self.slug = slug
        self.function = function
        self.addData = addData
        self.messageID = messageID
        self.chatID = chatID
        self.args = args
        self.kwargs = kwargs
        
        self.threadInterval = interval
        self.threadState = None
        self.updateTime = arrow.now()
        loggerWS.info("Action thread init: %s / %s" % (self.name, self.function))
        
    def stop(self):
        self.stopped.set()
        self.join()        
        loggerWS.info("Action thread %s / %s terminated: Ident: %s / ID: %s" % (self.getName(),self.function, self.ident, self.native_id))
        
    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            if not self.execute(*self.args, **self.kwargs): # Requires return value
                self.stopped.set()

    def modifyInterval(self, newInterval): # interval in seconds
        if newInterval != self.threadInterval:
            self.interval = timedelta(seconds=newInterval)
            self.threadInterval = newInterval
            loggerWS.info("Thread %s interval changed to: %s - Ident: %s / ID: %s" % (self.getName(), self.interval, self.ident, self.native_id))       

    def updateReferenceTime(self):
        self.updateTime = arrow.now()
        loggerWS.debug("Action thread %s / %s update reference time: %s" % (self.getName(),self.function, self.updateTime))
        
        
class timeDelThread(threading.Thread):
    def __init__(self, feedbackMsg = None, messageID = 0, chatID = CHATID, delayTimeSelect = 15, printer = None, function = None, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.feedbackMsg = feedbackMsg
        self.messageID = messageID
        self.chatID = chatID
        self.delayTimeSelect = timedelta(seconds=delayTimeSelect)
        self.printer = printer
        self.function = function
        self.args = args
        self.kwargs = kwargs

        if self.feedbackMsg != None:
            self.messageID = self.feedbackMsg['message_id']
            self.name = _("Message: %s") % self.messageID        
            self.chatID = self.feedbackMsg['chat']['id']
            logger.info("timeDelThread: Thread initialized for single delayed messageID: %s runtime: %ss" % (self.messageID, self.delayTimeSelect))
        else:
            self.name = self.messageID                
            if self.printer != None:
                logger.info("timeDelThread: Thread initialized for printer: %s and MessageID: %s runtime: %ss" % (printer, self.messageID, self.delayTimeSelect))
            else:
                logger.info("timeDelThread: Thread initialized for messageID: %s runtime: %ss" % (self.messageID, self.delayTimeSelect))
        self.start()
        
    def stop(self):
        self.join()        
        logger.info("timeDelThread: Thread message deleted ends for messageID %s: Ident: %s / ID: %s" % (self.messageID, self.ident, self.native_id))
        
    def run(self):
        self.stopped.wait(self.delayTimeSelect.total_seconds())
        self.delMessage(*self.args, **self.kwargs)

    def delMessage(self):
        if self.delayTimeSelect != 0:
            try:
                self.telegramDelMsg(self.messageID, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
            except:
                loggerWS.error("Could not delMessage method send telegramDelMsg to messageID: %s" % self.messageID)
            logger.debug("delMessage: messageID %s from chatID %s deleted" % (self.messageID, self.chatID))

    def telegramDelMsg(self, message_id, chat_id, token = MY_TELEGRAM_TOKEN):
        bot = telegram.Bot(token=token)
        return bot.deleteMessage(chat_id=chat_id, message_id=message_id)

class vidGifThread(threading.Thread):
    def __init__(self, execute, name, slug, type, queryData = None, webcamSelect = None, captionSelect = None, captionText = None, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.execute = execute
        self.name = name
        self.slug = slug
        self.type = type # "png" / "gif" / "vid"
        self.queryData = queryData
        self.webcamSelect = webcamSelect
        self.captionSelect = captionSelect
        self.captionText = captionText
        self.args = args
        self.kwargs = kwargs

        loggerWS.info("vidGifThread: Thread init: %s/%s" % (self.name, self.type))
        
    def stop(self):
        self.stopped.set()
        self.join()        
        loggerWS.info("vidGifThread: Thread %s terminated: Ident: %s / ID: %s" % (self.getName(), self.ident, self.native_id))
        
    def run(self):
        self.execute(*self.args, **self.kwargs)

class botThreadHdl(dataHdlThread):
    def __init__(self, telegramDispatcher, configFile, *args, **kwargs):
        self.telegramDispatcher = telegramDispatcher
        self.botHandlers = []
        self.webserver = "ws://" + RepetierServerIP + ":" + RepetierServerPort + "/socket/?lang=de&&apikey=" + MY_REPETIER_SERVER_API_KEY
        self.restartWsSend = 0
        self.restartWsReceive = 0
        self.restartOrderData = 0
        self.restartbotCom = 0
        self.restartThdMan = 0
        self.restartModelManager = 0
        self.sendCommand = self.encCommand()
        self.configFile = configFile
        self.botData = {}
        self.threadLock = threading.Lock()
        self.programStart = arrow.now()
        self.nextMsgRenew = self.programStart.shift(days=1)
        self.nextRSTimeoutMsg = None
        self.nextOrgMsgOrder = self.programStart.shift(seconds=30)
        loggerWS.info("Update all long term messages at: %s" % self.nextMsgRenew.format('DD.MM.YYYY - HH:mm'))
        self.wsThreadSend = dataHdlThread(interval=THRDSEND, execute=self.ThreadSend, name="Repetier-Server-Send")
        self.wsThreadRec = dataHdlThread(interval=THRDRECEIVE, execute=self.ThreadRec, name="Repetier-Server-Receive")
        self.wsThreadOrderData = dataHdlThread(interval=THRDORDERDATA, execute=self.ThreadHdlOrderData, name="Repetier-Server-Order-Data")
        self.botCommunicator = dataHdlThread(interval=THRDBOTCOM, execute=self.ThreadHdlBot, name="Repetier-Server-Bot-Communication-Threads")
        self.threadManager = dataHdlThread(interval=THRDMANAGER, execute=self.ThreadManager, name="Repetier-Server-Thread-Manager")
        self.modelManager = dataHdlThread(interval=THRDMODELMAN, execute=self.ModelManager, name="Repetier-Server-Model-Manager")
        self.wsThreadRestart = dataHdlThread(interval=THRDRESTART, execute=self.ThreadHdlRestart, name="Repetier-Server-Restart-Threads")

    def start(self):
        self.initDatastructure()
        self.initPrinterConfigActions()
        self.addMsgToBot(slug="Bot",
                             function="startMessage",
                             msg="<b>"+_("Welcome to Repetier-Server telegram bot!")+"</b>\n<b>"+_("from")+"</b>\nhttps://github.com/DanJunior78/Repetier-Server-Telegram-Bot\n<i>"+_("Version: ") + "%s</i>"% SW_VERSION,
                             reply_markup=None,
                             vidPic=None,
                             priority=False,
                             botMsg=True,
                             singleMsg=True, 
                             delTime=30
                             ) 
        self.sendLanguage()
        while self.wsWebsocket() == 'Error':
            loggerWS.error("start: Could not establish websocket at start up")
        else:
            loggerWS.info("start: Continues after successful repetier server connection")
        self.initServerActions()
        self.wsThreadSend.start()
        self.wsThreadRec.start()
        self.wsThreadOrderData.start()
        time.sleep(5)
        self.initModels()
        self.threadManager.start()
        self.botCommunicator.start()
        time.sleep(2)
        self.modelManager.start()
        self.wsThreadRestart.start()
        loggerWS.debug("Threads %s started" % self.getNames())

    def stop(self):
        self.wsThreadRestart.stop()
        self.wsThreadOrderData.stop()
        self.threadManager.stop()
        self.modelManager.stop()
        time.sleep(2)
        self.stopPrinterThreads()
        self.stopServerThreads()
        self.botCommunicator.stop()
        time.sleep(2)
        self.wsThreadRec.stop()
        time.sleep(2)
        self.wsThreadSend.stop()
        self.botData['server']['websocket']['actWS'].close()
        loggerWS.debug("Threads %s stopped and websocket closed" % self.getNames())
        return None

    def initDatastructure(self):# has to be called after generating instance
        loggerWS.info("initDatastructure for argv: %s " % sys.argv)
        self.botData = self.initBotData(self.configFile)
        if len(sys.argv) > 1:
            if sys.argv[1] == "":    # future implementation
                loggerWS.critical("initDatastructure...")
        else:
            loggerWS.info("initDatastructure no argv at startup")
       
    def initBotData(self, configFile):
        botDataSet = {}
        botDataSet['server'] = self.initServerRoot(configFile['server'])
        botDataSet['printers'] = self.initPrinterRoot(configFile['printers'])
        botDataSet['bot'] = self.initBotRoot()
        botDataSet['gui'] = self.initGuiRoot(configFile['gui'])        
        return botDataSet

    def initServerRoot(self, configFileServer):
        initServer = {}
        initServer['config'] = configFileServer
        initServer['websocket'] = {}
        initServer['websocket']['actWS'] = None
        initServer['websocket']['actSession'] = None
        initServer['websocket']['timeout'] = None
        initServer['websocket']['msgCnt'] = 10000
        initServer['websocket']['msgCntHandler'] = []
        initServer['websocket']['dataSendBuffer'] = []
        initServer['websocket']['dataReceiveBuffer'] = []
        initServer['threads'] = {}
        initServer['dataRepetier'] = {}
        initServer['statistic'] = {}
        initServer['statistic']['prints'] = []
        initServer['statistic']['summary'] = []
        return initServer

    def initPrinterRoot(self, configFilePrinters):
        initPrinters = {}
        for printer in configFilePrinters:
            initPrinters[printer['slug']] = {}
            initPrinters[printer['slug']]['config'] = printer
            initPrinters[printer['slug']]['threads'] = {}
            initPrinters[printer['slug']]['dataRepetier'] = {}
            initPrinters[printer['slug']]['dataRepetier']['newRenderImage'] = {}
            initPrinters[printer['slug']]['dataRepetier']['newRenderImage']['id'] = None
        return initPrinters

    def initBotRoot(self):
        initBot = {}
        initBot['handler'] = {}
        initBot['messages'] = []
        initBot['prioMessages'] = []
        initBot['messageID'] = []
        initBot['toDelete'] = []
        initBot['actConv'] = None # if used {}
        initBot['messageBot'] = []
        return initBot

    def initGuiRoot(self, configFilePrinters):
        initGui = {}
        initGui = configFilePrinters
        return initGui

    def sendLanguage(self):
        msg = "<i>" + _("Language set to") + " </i>"
        if LANGUAGE == "en":
            msg += "🇬🇧"
        elif LANGUAGE == "de":
            msg += "🇩🇪"
        elif LANGUAGE == "es":
            msg += "🇪🇸"
        else:
            msg += "🇬🇧"
        self.addMsgToBot(slug="Bot",
                             function="languageInfo",
                             msg=msg,
                             reply_markup=None,
                             vidPic=None,
                             priority=False,
                             botMsg=True,
                             singleMsg=True, 
                             delTime=5
                             )

    def stopPrinterThreads(self):
        for printer in self.botData['printers']:
            loggerWS.info("stopPrinterThreads - have to stop %s threads for printer %s" % (len(self.botData['printers'][printer]['threads']), printer))
            for thread in self.botData['printers'][printer]['threads']:
                self.botData['printers'][printer]['threads'][thread].stop()
                loggerWS.info("stopPrinterThreads - Stop thread %s from printer %s" % (thread, printer))

    def stopServerThreads(self):
        loggerWS.info("stopServerThreads - have to stop %s threads" % (len(self.botData['server']['threads'])))
        for thread in self.botData['server']['threads']:
            self.botData['server']['threads'][thread].stop()
            loggerWS.info("stopServerThreads - Stop thread %s from server" % (thread))
            
    def startActionThread(self, name, slug, execute, function, interval, threadFlex=True, addData = None):
        x = actionThread(interval=interval,
                         execute=execute,
                         name=name,
                         slug=slug,
                         function=function,
                         addData=addData, 
                         threadFlex=threadFlex)
        x.start()
        return x

    def startWebcamThread(self, slug, name, type, queryData=None, webcamSelect = None, captionSelect = None, captionText = None):
        x = vidGifThread(execute=self.webcamHandler,
                          slug=slug, 
                          name=name,
                          type=type, 
                          queryData=queryData,
                          webcamSelect=webcamSelect,
                          captionSelect=captionSelect,
                          captionText=captionText)
        x.start()

    def delPrinterMsg(self):
        for messages in self.botData['bot']['messageID']:
            timeDelThread(messageID=messages['message_id'],delayTimeSelect=1)
            loggerWS.info("delPrinterMsg: Message from messageID %s/%s with messageID %s will be removed" % (messages['slug'], messages['function'], messages['message_id']))
        for messages in self.botData['bot']['toDelete']:
            timeDelThread(messageID=messages['message_id'],delayTimeSelect=1)
            loggerWS.info("delPrinterMsg: Message from toDelete %s/%s with messageID %s will be removed" % (messages['slug'], messages['function'], messages['message_id']))

    def addHandler(self, item, hdlType=None): # Types: printer / messages /
        if hdlType == "printer":
            conv_handler = ConversationHandler(
            entry_points=[CommandHandler(item, mainMenu)
                          ],
            states={
                ONE: [CallbackQueryHandler(exitBot, pattern="^End$"), # Start conversation
                      CallbackQueryHandler(extCommands, pattern="^ExtCommands$"),
                      CallbackQueryHandler(webcams, pattern="Webcam*"),
                      CallbackQueryHandler(quickCommands, pattern="^QuickCommands"),
                      CallbackQueryHandler(handlePrint, pattern="^HandlePrinter"),
                      CallbackQueryHandler(settings, pattern="Settings*")
                      ],
                TWO: [CallbackQueryHandler(exitBot, pattern="^End$"), # ExtCommand conversation
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"), 
                      CallbackQueryHandler(extCommandsChoosen)
                      ],
                THREE: [CallbackQueryHandler(exitBot, pattern="^End$"), # ExtCommand conversation
                      CallbackQueryHandler(extCommands, pattern="^Back$"), 
                      CallbackQueryHandler(extCommandAction, pattern="^OK$")
                      ],
                FOUR: [CallbackQueryHandler(exitBot, pattern="^End$"), # Webcam conversation
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"), 
                      CallbackQueryHandler(webcamSendVideo, pattern="Send Video*"),
                      CallbackQueryHandler(webcamSendGif, pattern="Send Gif*"),
                      CallbackQueryHandler(webcamSendPng, pattern="Send Png*")
                      ],
                FIVE: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"), 
                      CallbackQueryHandler(extrSetLimit, pattern="Extruder Temp Limit*"), # Extruder Temp Limit
                      CallbackQueryHandler(prinExtCommOff, pattern="ExtCommand Temp Limit*"), 
                      CallbackQueryHandler(heatbSetLimit, pattern="Heatbed Temp Limit*"), # Heatbed Temp Limit
                      CallbackQueryHandler(prinHeatbCommOff, pattern="HeatbCommand Temp Limit*"), 
                      CallbackQueryHandler(afterPrintTime, pattern="Print after time*"), # Pic after print
                      CallbackQueryHandler(afterPrintWebcam, pattern="Send Png*"),
                      CallbackQueryHandler(zHeightPrintPicHeight, pattern="zHeight Value*"), # Pic zHeight
                      CallbackQueryHandler(zHeightPrintPicCamSelect, pattern="Send zHeight Png*"),
                      CallbackQueryHandler(timeBasedPrintPic, pattern="Print time based time*"), # Pic after time
                      CallbackQueryHandler(timeBasedPrintPicCamSelect, pattern="Send time based Png*")
                      ],
                SIX: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation extrSetLimit
                      CallbackQueryHandler(settingsBack, pattern="^Back$"),
                      MessageHandler(Filters.all, extrSetLimitValue)
                      ],
                SEVEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation prinExtCommOff
                      CallbackQueryHandler(settingsBack, pattern="^Back$"),
                      CallbackQueryHandler(prinExtCommOffItem)
                      ],
                EIGHT: [CallbackQueryHandler(exitBot, pattern="^End$"), # QuickCommands conversation prinQuickCommand
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"),
                      CallbackQueryHandler(prinQuickCommand)
                      ],
                NINE: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation afterPrintTime
                      CallbackQueryHandler(settingsBack, pattern="^Back$"),
                      MessageHandler(Filters.all, afterPrintTimeValue)
                      ],
                TEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation afterPrintWebcam
                      CallbackQueryHandler(settingsBack, pattern="^Back$"),
                      CallbackQueryHandler(afterPrintWebcamItem)
                      ],
                ELEVEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation extrSetLimit
                      CallbackQueryHandler(settingsBack, pattern="^Back$"),
                      MessageHandler(Filters.all, heatbSetLimitValue)
                      ],
                TWELVE: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation prinExtCommOff
                      CallbackQueryHandler(settingsBack, pattern="^Back$"),
                      CallbackQueryHandler(prinHeatbCommOffItem)
                      ],
                THIRTEEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation zHeightPrintPic
                      CallbackQueryHandler(settingsBack, pattern="^Back$"),
                      MessageHandler(Filters.all, zHeightPrintPicValue)
                      ],
                FOURTEEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation zHeightPrintPicCamSelect
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"),
                      CallbackQueryHandler(zHeightPrintPicCamSelectItem)
                      ],
                FIFTEEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation timeBasedPrintPic
                      CallbackQueryHandler(settingsBack, pattern="^Back$"),
                      MessageHandler(Filters.all, timeBasedPrintPicValue)
                      ],
                SIXTEEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Settings conversation timeBasedPrintPicCamSelect
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"),
                      CallbackQueryHandler(timeBasedPrintPicCamSelectItem)
                      ],
                SEVENTEEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Start print
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"),
                      CallbackQueryHandler(handlePrintFSpeed, pattern="^FanSpeed*"),
                      CallbackQueryHandler(handlePrintETemp, pattern="^ExtruderTemperature*"),
                      CallbackQueryHandler(handlePrintBTemp, pattern="^BedTemperature*"),
                      CallbackQueryHandler(handlePrintCTemp, pattern="^ChamberTemperature*"),
                      CallbackQueryHandler(handlePrintQueue, pattern="^Queue$")
                      ],
                EIGHTTEEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Handle print
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"),
                      CallbackQueryHandler(handlePrintCancel, pattern="^Cancel$"),
                      CallbackQueryHandler(handlePrintSMultiply, pattern="^SpeedMultiply$"),
                      CallbackQueryHandler(handlePrintFSpeed, pattern="^FanSpeed*"),
                      CallbackQueryHandler(handlePrintETemp, pattern="^ExtruderTemperature*"),
                      CallbackQueryHandler(handlePrintBTemp, pattern="^BedTemperature*"),
                      CallbackQueryHandler(handlePrintCTemp, pattern="^ChamberTemperature*"),
                      CallbackQueryHandler(handlePrintFMultiply, pattern="^FlowMultiply$")
                      ],
                NINETEEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Cancel Print confirmation
                      CallbackQueryHandler(handlePrint, pattern="^Back$"), 
                      CallbackQueryHandler(handlePrintCancelAction, pattern="^OK$")
                      ],
                TWENTY: [CallbackQueryHandler(exitBot, pattern="^End$"), # Flow Multipy
                      CallbackQueryHandler(handlePrint, pattern="^Back$"), 
                      CallbackQueryHandler(handlePrintFMultiplyActionButton, pattern="^plus10$"), 
                      CallbackQueryHandler(handlePrintFMultiplyActionButton, pattern="^plus5$"), 
                      CallbackQueryHandler(handlePrintFMultiplyActionButton, pattern="^plus1$"), 
                      CallbackQueryHandler(handlePrintFMultiplyActionButton, pattern="^minus1$"), 
                      CallbackQueryHandler(handlePrintFMultiplyActionButton, pattern="^minus5$"), 
                      CallbackQueryHandler(handlePrintFMultiplyActionButton, pattern="^minus10$"), 
                      MessageHandler(Filters.all, handlePrintFMultiplyActionText)
                      ],
                TWENTYONE: [CallbackQueryHandler(exitBot, pattern="^End$"), # Print Queue Selection
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"),
                      CallbackQueryHandler(movePrintQueue, pattern="<<*"),
                      CallbackQueryHandler(movePrintQueue, pattern=">>*"),
                      CallbackQueryHandler(handlePrintSelection)
                      ],
                TWENTYTWO: [CallbackQueryHandler(exitBot, pattern="^End$"), # Start Print
                      CallbackQueryHandler(extCommandsBack, pattern="^Back$"),
                      CallbackQueryHandler(startSelectedPrint) 
                      ],
                TWENTYTHREE: [CallbackQueryHandler(exitBot, pattern="^End$"), # Emergency stop confirmation
                      CallbackQueryHandler(handlePrint, pattern="^Back$"), 
                      CallbackQueryHandler(handleEmStopAction, pattern="^OK$")
                      ],
                TWENTYFOUR: [CallbackQueryHandler(exitBot, pattern="^End$"), # Speed Multipy
                      CallbackQueryHandler(handlePrint, pattern="^Back$"), 
                      CallbackQueryHandler(handlePrintSMultiplyActionButton, pattern="^plus10$"), 
                      CallbackQueryHandler(handlePrintSMultiplyActionButton, pattern="^plus5$"), 
                      CallbackQueryHandler(handlePrintSMultiplyActionButton, pattern="^plus1$"), 
                      CallbackQueryHandler(handlePrintSMultiplyActionButton, pattern="^minus1$"), 
                      CallbackQueryHandler(handlePrintSMultiplyActionButton, pattern="^minus5$"), 
                      CallbackQueryHandler(handlePrintSMultiplyActionButton, pattern="^minus10$"), 
                      MessageHandler(Filters.all, handlePrintSMultiplyActionText)
                      ],
                TWENTYFIVE: [CallbackQueryHandler(exitBot, pattern="^End$"), # Fan speed
                      CallbackQueryHandler(handlePrint, pattern="^Back$"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^100*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^90*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^80*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^70*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^60*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^50*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^40*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^30*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^20*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^10*"), 
                      CallbackQueryHandler(handlePrintFSpeedActionButton, pattern="^0*"), 
                      MessageHandler(Filters.all, handlePrintFSpeedActionText)
                      ],
                TWENTYSIX: [CallbackQueryHandler(exitBot, pattern="^End$"), # Extruder temperature
                      CallbackQueryHandler(handlePrint, pattern="^Back$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^plus10$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^plus5$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^plus1$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^minus1$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^minus5$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^minus10$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^200$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^210$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^220$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^230$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^240$"), 
                      CallbackQueryHandler(handlePrintETempActionButton, pattern="^0$"), 
                      MessageHandler(Filters.all, handlePrintETempActionText)
                      ],
                TWENTYSEVEN: [CallbackQueryHandler(exitBot, pattern="^End$"), # Heatbed temperature
                      CallbackQueryHandler(handlePrint, pattern="^Back$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^plus10$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^plus5$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^plus1$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^minus1$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^minus5$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^minus10$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^50$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^60$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^70$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^80$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^90$"), 
                      CallbackQueryHandler(handlePrintBTempActionButton, pattern="^0$"), 
                      MessageHandler(Filters.all, handlePrintBTempActionText)
                      ],
                TWENTYEIGHT: [CallbackQueryHandler(exitBot, pattern="^End$"), # Chamber temperature
                      CallbackQueryHandler(handlePrint, pattern="^Back$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^plus10$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^plus5$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^plus1$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^minus1$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^minus5$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^minus10$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^50$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^60$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^70$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^80$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^90$"), 
                      CallbackQueryHandler(handlePrintCTempActionButton, pattern="^0$"), 
                      MessageHandler(Filters.all, handlePrintCTempActionText)
                      ],
                ConversationHandler.TIMEOUT:[MessageHandler(Filters.all, botTimeout)],      
                    },
            fallbacks=[MessageHandler(Filters.all, unknownCommand)],
            allow_reentry=True,
            conversation_timeout=60,
            name="Repetier-Server-Bot"
            )
        elif hdlType == "messages":
            conv_handler = ConversationHandler(
            entry_points=[CommandHandler(_("Messages"), mainServerMenu)
                          ],
            states={
                ONE: [CallbackQueryHandler(exitMessageBot, pattern="^End$"), # Start conversation
                      CallbackQueryHandler(delServerMessage)
                      ],
                ConversationHandler.TIMEOUT:[MessageHandler(Filters.all, botMessagesTimeout)],         
                    },
            fallbacks=[MessageHandler(Filters.all, unknownCommand)],
            allow_reentry=True,
            conversation_timeout=60,
            name="Repetier-Server-Bot-Messages"
            )
        else:
            logger.info("addHandler: No handler activated: %s" % item)
        if hdlType != None:
            self.botData['bot']['handler'][item] = conv_handler
            self.telegramDispatcher.add_handler(conv_handler)
            loggerWS.info("addHandler: Added handler %s" % item)

    def removeHandler(self, item, hdlType=None): # remove_handler(handler)
        if hdlType != None:
            handler = self.botData['bot']['handler'].pop(item)
            self.telegramDispatcher.remove_handler(handler)

    def rConfigFile(self):
        try:
            with open(CFGFILENAME) as json_file:
                data = json.load(json_file)
        except:
            logger.error("rConfigFile: Configuration file not found: %s" % CFGFILENAME)
            return "Error"
        return data

    def wConfigFile(self, data):
        try:
            with open(CFGFILENAME, 'w') as outfile:
                json.dump(data, outfile) 
        except:
                logger.error("wConfigFile: Configuration file could not be written")

    def savePrinterConfigFile(self):
        data = self.rConfigFile()
        if data != "Error":
            data['printers'] = []
            for printer in self.botData['printers']:
                data['printers'].append(self.botData['printers'][printer]['config'])
            self.wConfigFile(data)
            return True
        else:
            logger.error("saveConfigFile: Skip saving configuration due to failing rConfigFile.")
            return False

    def getNames(self):
        return {self.wsThreadSend.getName(), 
                self.wsThreadRec.getName(), 
                self.wsThreadOrderData.getName(), 
                self.botCommunicator.getName(), 
                self.threadManager.getName(), 
                self.modelManager.getName(), 
                self.wsThreadRestart.getName()}

    def are_alive(self):
        return {self.wsThreadSend.is_alive(), 
                self.wsThreadRec.is_alive(), 
                self.wsThreadOrderData.is_alive(), 
                self.botCommunicator.is_alive(), 
                self.threadManager.is_alive(), 
                self.modelManager.is_alive(), 
                self.wsThreadRestart.is_alive()}

    def idents(self):
        return {self.wsThreadSend.ident, 
                self.wsThreadRec.ident, 
                self.wsThreadOrderData.ident, 
                self.botCommunicator.ident, 
                self.threadManager.ident, 
                self.modelManager.ident, 
                self.wsThreadRestart.ident}

    def native_ids(self):
        return {self.wsThreadSend.native_id, 
                self.wsThreadRec.native_id, 
                self.wsThreadOrderData.native_id, 
                self.botCommunicator.native_id, 
                self.threadManager.native_id, 
                self.modelManager.native_id, 
                self.wsThreadRestart.native_id}

    def encCommand(self, action = "ping", callback_id = -1, printer = "My Printer", data = {}):
        command = {}
        command['action'] = action
        command['data'] = data
        command['printer'] = printer
        command['callback_id'] = callback_id
        command = json.dumps(command)
        return command
    
    def wsWebsocket(self):
        try:
            websocket = create_connection(self.webserver)
        except OSError:
            loggerWS.error("wsWebsocket: Response to open websocket: %s, Unexpected Error: %s" % (self.webserver, sys.exc_info()[1]))
            if self.botData['server']['websocket']['timeout'] == None:
                self.botData['server']['websocket']['timeout'] = arrow.now()
            return "Error"
        except:
            loggerWS.error("wsWebsocket: Response to open websocket: %s, Unexpected Error: %s" % (self.webserver, sys.exc_info()[0]))
            if self.botData['server']['websocket']['timeout'] == None:
                self.botData['server']['websocket']['timeout'] = arrow.now()
                self.botData['server']['websocket']['actSession'] = None
            return "Error"
        self.botData['server']['websocket']['actWS'] = websocket
        self.botData['server']['websocket']['timeout'] = None
        loggerWS.info("Websocket established: %s" % self.botData['server']['websocket']['actWS'].connected)
        return websocket

    def remMsgFromBot(self, slug, function, message_id=None):
        if message_id != None:
            message={}
            message['slug'] = slug
            message['function'] = function
            message['message_id'] = message_id
            with self.threadLock:
                self.botData['bot']['toDelete'].append(message)
            loggerWS.info("remMsgFromBot found and removed message with id %s"%(message_id))
        else:
            for i in range(0,len(self.botData['bot']['messageID'])):
                message = self.botData['bot']['messageID'][i]
                if message['slug'] == slug and message['function'] == function:
                    self.botData['bot']['toDelete'].append(message)
                    elementPop = self.botData['bot']['messageID'].pop(i)
                    loggerWS.info("remMsgFromBot found and removed message from %s/%s with message id: %s"%(slug,function, elementPop['message_id']))
            loggerWS.info("remMsgFromBot removed message from %s/%s"%(slug,function)) # message_id
                                
    def remMsgFromBuffer(self, slug, function):
        try:
            for i in range(0,len(self.botData['bot']['prioMessages'])):
                message = self.botData['bot']['prioMessages'][i]
                if message['slug'] == slug and message['function'] == function:
                    elementPop = self.botData['bot']['prioMessages'].pop(i)
                    loggerWS.info("remMsgFromBuffer found and removed in prio Messages message from %s/%s with message id: %s"%(slug,function, elementPop['message_id']))
            loggerWS.info("remMsgFromBuffer removed in prio Messages message from %s/%s"%(slug,function)) # message_id
        except:
            loggerWS.error("remMsgFromBuffer index not existing in prio Messages message from %s/%s"%(slug,function)) # message_id
        try:
            for i in range(0,len(self.botData['bot']['messages'])):
                message = self.botData['bot']['messages'][i]
                if message['slug'] == slug and message['function'] == function:
                    self.botData['bot']['messages'].pop(i)
                    loggerWS.info("remMsgFromBuffer found and removed in normal Messages message from %s/%s"%(slug,function))
            loggerWS.info("remMsgFromBuffer removed in normal Messages message from %s/%s"%(slug,function)) # message_id
        except:
            loggerWS.error("remMsgFromBuffer index not existing in normal Messages message from %s/%s"%(slug,function)) # message_id
                                
    def addMsgToBot(self, slug, function, msg, reply_markup=None, vidPic=None, priority=False, botMsg=False, singleMsg=False, delTime=15, modMsg=None, printInfo=None):
        if botMsg: # modMsg: modify message replay by "reply_markup" / modify printer pic "print_pic"
            with self.threadLock:
                self.botData['bot']['messageBot'].append(self.setNewBotMsg(slug, function, msg, reply_markup, vidPic, singleMsg, delTime, modMsg, printInfo))
        else:
            if not priority:
                dataAvailable = False
                for message in self.botData['bot']['messages']:
                    if message['slug'] == slug and message['function'] == function:
                        loggerWS.debug("addMsgToBot - Edit Bot Message Entry: %s to %s" % (message['msg'], msg))
                        with self.threadLock:
                            message['msg'] = msg
                            message['updTime'] = arrow.now()
                        dataAvailable = True  
                if not dataAvailable:
                    loggerWS.debug("addMsgToBot - New Bot message entry")
                    with self.threadLock:
                        self.botData['bot']['messages'].append(self.setNewBotMsg(slug, function, msg, reply_markup, vidPic, singleMsg, delTime, modMsg, printInfo))
            else:
                loggerWS.debug("addMsgToBot - New Bot priority message entry")
                with self.threadLock:
                    self.botData['bot']['prioMessages'].append(self.setNewBotMsg(slug, function, msg, reply_markup, vidPic, singleMsg, delTime, modMsg, printInfo))

    def setNewBotMsg(self, slug, function, msg, reply_markup=None, vidPic=None, singleMsg=False, delTime=15, modMsg=None, printInfo=None):
        newEntry = {}
        newEntry['slug'] = slug
        newEntry['function'] = function
        newEntry['msg'] = msg
        newEntry['reply_markup'] = reply_markup
        newEntry['singleMsg'] = singleMsg
        newEntry['delTime'] = delTime
        newEntry['vidPic'] = vidPic # video = "vid" / pic = "pic" / gif = "gif"
        newEntry['printInfo'] = printInfo
        newEntry['modMsg'] = modMsg
        newEntry['updTime'] = arrow.now()
        newEntry['dailyRenew'] = False
        loggerWS.debug("setNewBotMsg - New Bot Message Entry: %s" % newEntry) 
        return newEntry

    def setNewMsgToMsgID(self, msg, feedbackBot):
        msg['message_id'] = feedbackBot['message_id'] # newMessageID
        msg['newMessageID'] = False
        return msg

    def setNewPrintInfo(self, msg, id=None, actPrint=None):
        msg['printInfo'] = {}
        msg['printInfo']['id'] = id # RS model ID
        msg['printInfo']['actPrint'] = actPrint # RS model name
        return msg

    def resetPrintInfo(self, msg):
        msg['printInfo'] = None
        return msg

    def pushAllMsgToFront(self):
        for item in self.botData['bot']['messageID']:
            with botThreads.threadLock:
                item['dailyRenew'] = True

    def ThreadManager(self):
        threadItem = threading.current_thread()
        self.threadWishState("active",threadItem)
        if self.botData['bot']['actConv'] != None:
            botConvActive = True
            slug = self.botData['bot']['actConv']['slug']
            function = self.botData['bot']['actConv']['function']
            loggerWS.debug("Conversation handler is active for: %s/%s" % (slug,function))
        else: 
             botConvActive = False
             loggerWS.debug("Conversation handler is inactive")
        printers = self.botData['printers']
        for printer in printers.copy():
            for functions in printers[printer]['threads']:
                if botConvActive:
                    if function == functions:
                        if slug == printers[printer]['threads'][functions].slug:
                            self.activateThreadState(thread=printers[printer]['threads'][functions], convAct=True, threadConv=True)
                        else:
                            self.activateThreadState(thread=printers[printer]['threads'][functions], convAct=True)
                else:
                    self.activateThreadState(thread=printers[printer]['threads'][functions])
        threadList = self.botData['server']['threads']
        for activities in threadList.copy():
            if botConvActive:
                if function == activities:
                    self.activateThreadState(thread=threadList[activities], convAct=True, threadConv=True)
                else:
                    self.activateThreadState(thread=threadList[activities], convAct=True)
            else:
                self.activateThreadState(thread=threadList[activities])

    def activateThreadState(self, thread, convAct=False, threadConv=False):
        # Cycle pre defined types:
        # THRDSLOW = 10, THRDSTANDBY = 5, THRDIDLE = 2, THRDACTIVE = 1, THRDNOW = 0, 
        # THRDSEND = 2, THRDRECEIVE = 0.2, THRDORDERDATA = 1, 
        # THRDBOTCOM = 1, THRDMANAGER = 1, THRDRESTART = 10, THRDMODELMAN = 2
        # states: off, idle, active
        #print("thread: %s ist convAct: %s, threadConv: %s, threadFlex: %s mit interval: %s"%(thread.name,convAct,threadConv,thread.threadFlex,thread.threadInterval))
        if threadConv:
            if thread.threadFlex:
                thread.modifyInterval(THRDACTIVE)
        else:
            if convAct:
                if thread.threadFlex:
                    if thread.threadState == "off":
                        thread.modifyInterval(THRDSLOW)
                    else:
                        thread.modifyInterval(THRDSTANDBY)
            else:
                if thread.threadFlex:
                    if thread.threadState == "off":
                        thread.modifyInterval(THRDSLOW)
                    elif thread.threadState == "standby":
                        thread.modifyInterval(THRDSTANDBY)
                    elif thread.threadState == "idle":
                        thread.modifyInterval(THRDIDLE)
                    elif thread.threadState == "active":
                        thread.modifyInterval(THRDACTIVE)
                    elif thread.threadState == None:
                        loggerWS.info("activateThreadState - Thread state: Waiting for first initialization %s/%s" % (thread.slug, thread.function))
                    else:
                        loggerWS.error("activateThreadState - Thread state: %s unknown for %s/%s" % (thread.threadState, thread.slug, thread.function))
        
    def threadWishState(self, state, thread):
        thread.threadState = state
        thread.updateReferenceTime()
            
    def isMyThreadActive(self, thread):
        if self.botData['bot']['actConv'] != None:
            slug = self.botData['bot']['actConv']['slug']
            function = self.botData['bot']['actConv']['function']
            if thread.slug==slug and thread.function==function:
                loggerWS.debug("Conversation handler is active for: %s/%s" % (thread.slug, thread.function))
                return True
            else:
                loggerWS.debug("Another conversation handler is active not: %s/%s" % (thread.slug, thread.function))
                return False
        else: 
            loggerWS.debug("Conversation handler for %s/%s is inactive" % (thread.slug, thread.function))
            return False
            
    def ThreadHdlBot(self):
        threadItem = threading.current_thread()
        msgDebugIn = None
        msgToSend = None
        msgToDel = None
        msgFromPrio = False
        msgBot = self.botData['bot']['messageBot']
        msgPrio = self.botData['bot']['prioMessages']
        msgDel = self.botData['bot']['toDelete']
        msgNormal = self.botData['bot']['messages']
        self.organizeMessageOrder()
        if len(msgBot) > 0:
            with self.threadLock:
                loggerWS.debug("ThreadHdlBot msgBot length: %d"%len(msgBot))
                msgToSend = msgBot.pop(0)
        elif len(msgDel) > 0:
            with self.threadLock:
                loggerWS.debug("ThreadHdlBot msgDel length: %d"%len(msgDel))
                msgToDel = msgDel.pop(0)
                loggerWS.debug("ThreadHdlBot msgToDel id: %s"%msgToDel['message_id'])
        elif len(msgPrio) > 0:
            with self.threadLock:
                loggerWS.debug("ThreadHdlBot msgPrio length: %d"%len(msgPrio))
                msgToSend = msgPrio.pop(0)
            msgFromPrio = True
        elif len(msgNormal) > 0:
            with self.threadLock:
                loggerWS.debug("ThreadHdlBot msgNormal length: %d"%len(msgNormal))
                if self.botData['server']['websocket']['timeout'] == None:
                    msgToSend = msgNormal.pop(0)
        else:
            loggerWS.debug("No message to send to bot")
            self.threadWishState("idle",threadItem)
        if msgToSend != None: #messageID
            msgDebugIn = msgToSend
            if msgToSend['singleMsg']:
                if msgToSend['delTime'] == 0:
                    try:
                        fdback = telegramSendMsg(msg=msgToSend['msg'], 
                                                 reply_markup=None, 
                                                 chat_id=CHATID, 
                                                 token=MY_TELEGRAM_TOKEN, 
                                                 parse_mode=telegram.ParseMode.HTML)
                    except:
                        loggerWS.error("ThreadHdlBot - Could not send single message without delay time: %s/%s" % (msgToSend['slug'], msgToSend['function']))
                else:
                    try:
                        timeDelThread(feedbackMsg=telegramSendMsg(msgToSend['msg'],
                                                                  reply_markup=None, 
                                                                  chat_id=CHATID, 
                                                                  token=MY_TELEGRAM_TOKEN
                                                                  ),
                                    delayTimeSelect=msgToSend['delTime'])
                    except:
                        loggerWS.error("ThreadHdlBot - Could not send single message with delay time: %s/%s" % (msgToSend['slug'], msgToSend['function']))
            elif msgToSend['vidPic'] != None: # video = "vid" / pic = "pic" / gif = "gif" / file = "file"
                loggerWS.info("In vidPic: \"%s\" - Info Path/Caption: %s / %s" % (msgToSend['vidPic'], msgToSend['msg']['path'], msgToSend['msg']['caption'])) 
                if msgToSend['vidPic'] == "vid":
                    telegramSendVideo(video=msgToSend['msg']['path'], 
                                      caption=msgToSend['msg']['caption'], 
                                      chat_id=CHATID, token=MY_TELEGRAM_TOKEN, 
                                      parse_mode=telegram.ParseMode.HTML)
                    loggerWS.info("Video send: %s/%s" % (msgToSend['slug'], msgToSend['function'])) 
                if msgToSend['vidPic'] == "preview":
                    telegramSendPic(pic=msgToSend['msg']['path'], 
                                    caption=msgToSend['msg']['caption'], 
                                    chat_id=CHATID, token=MY_TELEGRAM_TOKEN,
                                    reply_markup=msgToSend['reply_markup'],
                                    parse_mode=telegram.ParseMode.HTML)
                    loggerWS.info("Picture send: %s/%s" % (msgToSend['slug'], msgToSend['function'])) 
                if msgToSend['vidPic'] == "pic":
                    telegramSendPic(pic=msgToSend['msg']['path'], 
                                    caption=msgToSend['msg']['caption'], 
                                    chat_id=CHATID, token=MY_TELEGRAM_TOKEN, 
                                    parse_mode=telegram.ParseMode.HTML)
                    loggerWS.info("Picture send: %s/%s" % (msgToSend['slug'], msgToSend['function'])) 
                if msgToSend['vidPic'] == "gif":
                    telegramSendAnimation(anim=msgToSend['msg']['path'], 
                                          caption=msgToSend['msg']['caption'], 
                                          chat_id=CHATID, token=MY_TELEGRAM_TOKEN, 
                                          parse_mode=telegram.ParseMode.HTML)
                    loggerWS.info("Gif send: %s/%s" % (msgToSend['slug'], msgToSend['function']))
                if msgToSend['vidPic'] == "file":
                    telegramSendDocument(file=msgToSend['msg']['path'], 
                                         caption=msgToSend['msg']['caption'], 
                                         chat_id=CHATID, token=MY_TELEGRAM_TOKEN, 
                                         parse_mode=telegram.ParseMode.HTML)
                    loggerWS.info("File send: %s/%s" % (msgToSend['slug'], msgToSend['function']))
            else:
                msgID = self.botData['bot']['messageID']
                msgInList = False
                msgLongShort = ""
                if self.botData['bot']['actConv'] != None:
                    if self.botData['bot']['actConv']['slug'] == msgToSend['slug'] and self.botData['bot']['actConv']['function'] == msgToSend['function']:
                        msgLongShort = msgToSend['msg']['msgLong']
                    else:
                        msgLongShort = msgToSend['msg']['msgShort']
                else:
                    msgLongShort = msgToSend['msg']['msgShort']
                for message in msgID:
                    if message['slug'] == msgToSend['slug'] and message['function'] == msgToSend['function']:
                        msgInList = True
                        with self.threadLock:
                            if msgFromPrio:
                                if msgToSend['modMsg'] == "reply_markup":
                                    message['reply_markup'] = msgToSend['reply_markup']
                                    msgToSend['printInfo'] = message['printInfo']
                                elif msgToSend['modMsg'] == "print_pic":
                                    try:
                                        if msgToSend['msg']['id'] != None:
                                            msgToSend = self.setNewPrintInfo(msgToSend, id=msgToSend['msg']['id'], actPrint=msgToSend['msg']['actPrint'])
                                        else:
                                            msgToSend = self.resetPrintInfo(msgToSend)
                                    except:
                                        loggerWS.critical("Mod message with wrong msg dataset: %s/%s with message ID: %s/%s" % (message['slug'], message['function'], message['message_id'],msgToSend))
                                    msgToSend['reply_markup'] = message['reply_markup']
                                    msgToSend['msg'] = message['msg']
                                    message['newMessageID'] = True
                                elif msgToSend['modMsg'] == "reorder":
                                    message['dailyRenew'] = True
                                else:
                                    msgToSend['printInfo'] = message['printInfo']
                                    loggerWS.info("Message from Prio without modMsg: %s/%s with message ID: %s" % (message['slug'], message['function'], message['message_id']))
                                loggerWS.info("Prio messsage with mod: %s/%s"%(msgToSend['modMsg'],msgToSend['printInfo']))
                            if message['newMessageID'] or message['dailyRenew']:
                                if message['newMessageID']:
                                    loggerWS.info("Bot request message to renew: %s/%s with message ID: %s modMsg: %s/%s" % (message['slug'], 
                                                                                                                message['function'], 
                                                                                                                message['message_id'],
                                                                                                                msgToSend['modMsg'], 
                                                                                                                msgToSend['printInfo']))
                                    if msgToSend['printInfo'] != None:
                                        try:
                                            msgID.append(self.setNewMsgToMsgID(msgToSend, 
                                                                                telegramSendPic(pic=msgToSend['printInfo']['actPrint'],
                                                                                caption=msgLongShort, 
                                                                                reply_markup=msgToSend['reply_markup'], # telegram conversation has to modify message reply markup
                                                                                chat_id=CHATID, 
                                                                                token=MY_TELEGRAM_TOKEN, 
                                                                                parse_mode=telegram.ParseMode.HTML)))
                                            loggerWS.info("Message renewed: %s/%s id: %s" % (msgToSend['slug'], msgToSend['function'],msgToSend['message_id']))
                                            self.botData['bot']['toDelete'].append(message)
                                            self.botData['bot']['messageID'].remove(message)
                                        except:
                                            loggerWS.error("ThreadHdlBot - Picture could not be renewed: %s/%s" % (message['slug'], message['function']))
                                    else:
                                        try:
                                            msgID.append(self.setNewMsgToMsgID(msgToSend, 
                                                                                telegramSendMsg(msg=msgLongShort, 
                                                                                reply_markup=msgToSend['reply_markup'], # telegram conversation has to modify message reply markup
                                                                                chat_id=CHATID, 
                                                                                token=MY_TELEGRAM_TOKEN, 
                                                                                parse_mode=telegram.ParseMode.HTML)))
                                            loggerWS.info("Message renewed: %s/%s id: %s" % (msgToSend['slug'], msgToSend['function'],msgToSend['message_id']))
                                            self.botData['bot']['toDelete'].append(message)
                                            self.botData['bot']['messageID'].remove(message)
                                        except:
                                            loggerWS.error("ThreadHdlBot - Message could not be renewed: %s/%s" % (message['slug'], message['function'])) 
                                if message['dailyRenew']:
                                    loggerWS.info("dailyRenew message to renew: %s/%s with message ID: %s printInfo: %s" % (message['slug'], 
                                                                                                                message['function'], 
                                                                                                                message['message_id'], 
                                                                                                                msgToSend['printInfo']))
                                    message['dailyRenew'] = False
                                    if message['printInfo'] != None:
                                        backupMsg = copy.deepcopy(message)
                                        try:
                                            msgID.append(self.setNewMsgToMsgID(backupMsg, 
                                                                                telegramSendPic(pic=backupMsg['printInfo']['actPrint'],
                                                                                caption=msgLongShort, 
                                                                                reply_markup=backupMsg['reply_markup'], # telegram conversation has to modify message reply markup
                                                                                chat_id=CHATID, 
                                                                                token=MY_TELEGRAM_TOKEN, 
                                                                                parse_mode=telegram.ParseMode.HTML)))
                                            loggerWS.info("Message renewed: %s/%s id: %s" % (backupMsg['slug'], backupMsg['function'],backupMsg['message_id']))
                                            self.botData['bot']['toDelete'].append(message)
                                            self.botData['bot']['messageID'].remove(message)
                                        except:
                                            loggerWS.error("ThreadHdlBot - Picture could not be renewed: %s/%s" % (message['slug'], message['function']))
                                    else:
                                        backupMsg = copy.deepcopy(message)
                                        try:
                                            msgID.append(self.setNewMsgToMsgID(backupMsg, 
                                                                                telegramSendMsg(msg=msgLongShort, 
                                                                                reply_markup=backupMsg['reply_markup'], # telegram conversation has to modify message reply markup
                                                                                chat_id=CHATID, 
                                                                                token=MY_TELEGRAM_TOKEN, 
                                                                                parse_mode=telegram.ParseMode.HTML)))
                                            loggerWS.info("Message renewed: %s/%s id: %s" % (backupMsg['slug'], backupMsg['function'],backupMsg['message_id']))
                                            self.botData['bot']['toDelete'].append(message)
                                            self.botData['bot']['messageID'].remove(message)
                                        except:
                                            loggerWS.error("ThreadHdlBot - Message could not be renewed: %s/%s" % (message['slug'], message['function'])) 
                            else:
                                loggerWS.debug("Message to edit: %s/%s id: %s" % (message['slug'], message['function'], message['message_id']))
                                if message['printInfo'] != None:
                                    try:
                                        telegramEditCapt(caption=msgLongShort, 
                                                        message_id=message['message_id'], 
                                                        reply_markup=message['reply_markup'], # telegram conversation has to modify message reply markup
                                                        chat_id=CHATID, 
                                                        token=MY_TELEGRAM_TOKEN, 
                                                        parse_mode=telegram.ParseMode.HTML)
                                        message['updTime'] = msgToSend['updTime']
                                        loggerWS.debug("Caption edited: %s/%s with message ID: %s" % (msgToSend['slug'], msgToSend['function'],message['message_id']))
                                    except:
                                        loggerWS.info("ThreadHdlBot - Caption could not be edited: %s/%s message_id: %s" % (message['slug'], message['function'], message['message_id']))
                                else:
                                    try:
                                        telegramEditMsg(msg=msgLongShort, 
                                                        message_id=message['message_id'], 
                                                        reply_markup=message['reply_markup'], # telegram conversation has to modify message reply markup
                                                        chat_id=CHATID, 
                                                        token=MY_TELEGRAM_TOKEN, 
                                                        parse_mode=telegram.ParseMode.HTML)
                                        message['updTime'] = msgToSend['updTime']
                                        loggerWS.debug("Message edited: %s/%s with message ID: %s" % (msgToSend['slug'], msgToSend['function'],message['message_id']))
                                    except:
                                        loggerWS.debug("ThreadHdlBot - Message could not be edited: %s/%s message_id: %s" % (message['slug'], message['function'], message['message_id']))
                        break
                if msgInList == False:
                    with self.threadLock:
                        try:
                            msgID.append(self.setNewMsgToMsgID(msgToSend, 
                                                                telegramSendMsg(msg=msgLongShort, 
                                                                reply_markup=msgToSend['reply_markup'], # telegram conversation has to modify message reply markup
                                                                chat_id=CHATID, 
                                                                token=MY_TELEGRAM_TOKEN, 
                                                                parse_mode=telegram.ParseMode.HTML)))
                            loggerWS.debug("Message send: %s/%s and placed for edit to database" % (msgToSend['slug'], msgToSend['function']))
                        except:
                            loggerWS.error("setNewMsgToMsgID - Message could not be added: %s/%s" % (msgToSend['slug'], msgToSend['function']))
        elif msgToDel != None:
            msgDebugIn = msgToDel
            timeDelThread(messageID=msgToDel['message_id'],
                          delayTimeSelect=0)
        self.checkCleanDatabase()
        #self.debugMsgID(msgDebugIn) # ,slug=,function=) # to change for detail debug
        self.threadWishState("active",threadItem)

    def debugMsgID(self, msgDebugIn, slug=None, function=None):
        if msgDebugIn != None:
            loggerWS.info("START")
            loggerWS.info("debugMsg: %s" % (msgDebugIn))
            for message in self.botData['bot']['messageID']:
                if slug == None and function == None:
                    loggerWS.info("debugMsg - Message in database: %s/%s id: %s" % (message['slug'], message['function'], message['message_id']))
                elif slug == msgDebugIn['slug'] and function == msgDebugIn['function']:
                    loggerWS.info("debugMsg - Message in database, special for: %s/%s id: %s" % (message['slug'], message['function'], message['message_id']))
            loggerWS.info("END")
            
    def checkCleanDatabase(self):
        actTime = arrow.now()
        timeLimit = actTime.shift(minutes=-10)
        for msg in self.botData['bot']['messageID']:
            if msg['updTime'] < timeLimit:
                loggerWS.critical("checkCleanDatabase - Remove in database: %s/%s with time %s and limit %s" % (msg['slug'], 
                                                                                                                   msg['function'], 
                                                                                                                   msg['updTime'], 
                                                                                                                   timeLimit)) 
                with self.threadLock:
                    self.botData['bot']['toDelete'].append(msg)
                    self.botData['bot']['messageID'].remove(msg)
        if self.nextMsgRenew < actTime:
            self.nextMsgRenew = self.nextMsgRenew.shift(days=1)
            self.addMsgToBot(slug="Bot",
                             function="renewMessages",
                             msg="⚠️♻️ <b>" + _("Renew message now. Next renew of messages") + " %s</b> ‼️" % self.nextMsgRenew.format('DD.MM.YYYY - HH:mm'),
                             reply_markup=None,
                             vidPic=None,
                             priority=True,
                             botMsg=True,
                             singleMsg=True, 
                             delTime=20
                             ) 
            loggerWS.info("Update all long term messages. Next update at: %s" % self.nextMsgRenew.format('DD.MM.YYYY - HH:mm'))
            for item in self.botData['bot']['messageID']:
                with self.threadLock:
                    item['dailyRenew'] = True

    def checkPrinterInMessageID(self, slug):
        for printer in self.botData['bot']['messageID']:
            if printer['slug'] == slug and printer['function'] == "printer":
                return True
        return False

    def organizeMessageOrder(self):
        actTime = arrow.now()
        if self.nextOrgMsgOrder < actTime:
            loggerWS.debug("organizeMessageOrder - Start checking messages in database")
            if self.botData['bot']['actConv'] == None and len(self.botData['bot']['prioMessages']) == 0 and len(self.botData['bot']['messageBot']) == 0:
                msgSort = {}
                msgSort['off'] = []
                msgSort['idle'] = []
                msgSort['printing'] = []
                msgSort['server'] = []
                for slug in self.botData['printers']:
                    listPrinter = self.botData['printers'][slug]['dataRepetier']['listPrinter']
                    for message in self.botData['bot']['messageID']:
                        if message['slug'] == slug:
                            item = {}
                            item['slug'] = slug
                            item['function'] = message['function']
                            item['message_id'] = message['message_id']
                            if listPrinter['online'] == 0:
                                msgSort['off'].append(item)
                            elif listPrinter['online'] == 1 and listPrinter['job'] == "none":
                                msgSort['idle'].append(item)
                            else:
                                msgSort['printing'].append(item)
                            loggerWS.debug("organizeMessageOrder place printer \"%s\" to list of message, online: %s job: %s" % (slug, listPrinter['online'], listPrinter['job']))
                for message in self.botData['bot']['messageID']:
                    if message['slug'] == _("Messages"):
                        item = {}
                        item['slug'] = _("Messages")
                        item['function'] = message['function']
                        item['message_id'] = message['message_id']
                        msgSort['server'].append(item)
                loggerWS.debug("organizeMessageOrder unsorted list of message IDs: %s" % msgSort)
                msgSort['off'].sort(key=lambda x:x['message_id'])
                msgSort['idle'].sort(key=lambda x:x['message_id'])
                msgSort['printing'].sort(key=lambda x:x['message_id'])
                msgSort['server'].sort(key=lambda x:x['message_id'])
                loggerWS.debug("organizeMessageOrder sorted list of message IDs: %s" % msgSort)
                biggestID = 0
                msgToUpdate = []
                if len(msgSort['off']) != 0:
                    biggestID = msgSort['off'][len(msgSort['off'])-1]['message_id']
                    loggerWS.debug("organizeMessageOrder biggest message ID in \"off\": %s" % biggestID)
                for item in msgSort['idle']:
                    if item['message_id'] < biggestID:
                        loggerWS.debug("organizeMessageOrder renew message ID for: %s" % item['slug'])
                        msgToUpdate.append(item)
                if len(msgSort['idle']) != 0:
                    if biggestID < msgSort['idle'][len(msgSort['idle'])-1]['message_id']:
                        biggestID = msgSort['idle'][len(msgSort['idle'])-1]['message_id']
                        loggerWS.debug("organizeMessageOrder biggest message ID in \"idle\": %s" % biggestID)
                for item in msgSort['printing']:
                    if item['message_id'] < biggestID:
                        loggerWS.debug("organizeMessageOrder renew message ID for: %s" % item['slug'])
                        msgToUpdate.append(item)
                if len(msgSort['printing']) != 0:
                    if biggestID < msgSort['printing'][len(msgSort['printing'])-1]['message_id']:
                        biggestID = msgSort['printing'][len(msgSort['printing'])-1]['message_id']
                        loggerWS.debug("organizeMessageOrder biggest message ID in \"printing\": %s" % biggestID)
                for item in msgSort['server']:
                    if item['message_id'] < biggestID:
                        loggerWS.debug("organizeMessageOrder renew message ID for: %s" % item['slug'])
                        msgToUpdate.append(item)
                if len(msgToUpdate) != 0:
                    loggerWS.debug("organizeMessageOrder biggest ID: %s updated messages: %s"%(biggestID,msgToUpdate))
                    msg = "<i>" + _("Start reorder %d message(s)!") % len(msgToUpdate) + "</i>"
                    self.addMsgToBot(slug="Bot",
                                    function="organizeMessageOrder",
                                    msg=msg,
                                    reply_markup=None,
                                    vidPic=None,
                                    priority=False,
                                    botMsg=True,
                                    singleMsg=True, 
                                    delTime=len(msgToUpdate)+1
                                    )
                for item in msgToUpdate:
                    msg = {}
                    msgText = "<i>" + _("Renew myself %s !") % item['slug'] + "</i>"
                    msg['msgLong'] = msgText
                    msg['msgShort'] = msgText
                    self.addMsgToBot(slug=item['slug'],
                                        function=item['function'],
                                        msg=msg,
                                        reply_markup=None,
                                        vidPic=None,
                                        priority=True,
                                        botMsg=False,
                                        singleMsg=False, 
                                        delTime=5,
                                        modMsg="reorder")
                    loggerWS.info("organizeMessageOrder renew item: %s updated messages: %s"%(item['slug'],item['message_id']))
                self.nextOrgMsgOrder = actTime.shift(seconds=30)
            else:
                self.nextOrgMsgOrder = actTime.shift(seconds=30)

    def msgPrinter(self):
        threadItem = threading.current_thread()
        slug = threadItem.slug
        listPrinters = self.getPrinterDataStorage(slug, "listPrinter")
        if listPrinters != "Error":
            if listPrinters['online'] == 0 or listPrinters['active'] == False:
                msgShort = "<b>/%s" % slug + "</b>\n"
                if listPrinters['active'] == False:
                    msgShort = "<s>/%s" % slug + "</s>\n"
                msgShort += "<code>" + _("Update: %s at %s") % (arrow.now().format('DD.MM.YYYY'), arrow.now().format('HH:mm:ss')) + "</code>\n"
                msgShort += "<pre><code>💤 " + _("Switched off") + "</code></pre>"
                msgLong = msgShort
                self.threadWishState("off",threadItem)
            else:
                msgBasis = "<b>/%s" % slug + "</b>\n"
                msgBasis += "<code>" + _("Update: %s at %s") % (arrow.now().format('DD.MM.YYYY'), arrow.now().format('HH:mm:ss')) + "</code>\n"
                msgLong = ""
                msgShort = msgBasis
                stateLists = self.getPrinterDataStorage(slug, "stateList")
                if stateLists != "Error":
                    if listPrinters['job'] == "none":
                        statExtr, msgExtr = self.getExtruderStatus(slug, stateLists)
                        statHeatb, msgHeatb = self.getHeatbedStatus(slug, stateLists)
                        if statExtr or statHeatb:
                            msgShort += msgExtr
                            msgShort += msgHeatb
                        else:
                            msgShort += "<i>🅿️ " + _("Standby") + "</i>"
                        msgLong = msgShort
                        self.threadWishState("idle",threadItem)
                    else:
                        msgF = self.checkFanssStatus(stateLists['fans'])
                        statusC, msgC = self.checkChambersStatus(stateLists['heatedChambers'])
                        statusHB, msgHB = self.checkHeatedBedsStatus(stateLists['heatedBeds'])
                        statusE, msgE = self.checkExtrudersStatus(stateLists['extruder'])
                        msgLong = msgBasis 
                        if statusC and statusHB and statusE:
                            actTime = arrow.now()
                            restOfPrintTime = int(listPrinters['printTime'])-int(listPrinters['printedTimeComp'])
                            msgLong += "<u><b>" + _("Print file") + ":</b></u>\n"
                            msgLong += "<b>\"%s\"</b>\n" % listPrinters['job'] 
                            msgLong += "<b>" + _("is at") + "</b> <i>%.1f</i>%%\n" % listPrinters['done']
                            msgLong += "<b>" + _("Layer:") + "</b> <i>%s/%s</i> <b>" % (stateLists['layer'], listPrinters['ofLayer']) + _("at Z:") + "</b> <i>%.3fmm</i>\n" % stateLists['z']
                            msgLong += "<b>" + _("Print was started") + ":</b> <i>%s</i>\n" % arrow.get(int(listPrinters['start'])).format('DD.MM.YYYY - HH:mm')
                            msgLong += "<b>" + _("Expected end at") + ":</b> <i>%s</i>\n" % actTime.shift(seconds=restOfPrintTime).format('DD.MM.YYYY - HH:mm')
                            msgLong += "<b>" + _("Actual print time") + ":</b> <i>%s</i>\n" % getTimeDelta(int(listPrinters['printedTimeComp']))
                            msgLong += "<b>" + _("Time left to finish") + ":</b> <i>%s</i>\n" % getTimeDelta(int(listPrinters['printTime'])-int(listPrinters['printedTimeComp']))
                            msgLong += "\n<u><b>" + _("Printer state") + ":</b></u>\n"
                            msgLong += "<b>⚙️ " + _("Print speed") + ":</b> <i>%s%%</i> " % (stateLists['speedMultiply']) + "💧 <b>" + _("Flow") + ":</b> <i>%s%%</i>\n" % (stateLists['flowMultiply'])
                            msgLong += msgF
                            if len(stateLists['heatedChambers']) > 0:
                                msgLong += msgC
                            if len(stateLists['heatedBeds']) > 0:
                                msgLong += msgHB
                            if len(stateLists['extruder']) > 0:
                                msgLong += msgE
                        else:
                            msgLong += "<u><b>🔥 " + _("Heat up phase:") + ":</b></u>\n"
                            msgLong += msgF
                            if len(stateLists['heatedChambers']) > 0:
                                msgLong += msgC
                            if len(stateLists['heatedBeds']) > 0:
                                msgLong += msgHB
                            if len(stateLists['extruder']) > 0:
                                msgLong += msgE
                        if statusC and statusHB and statusE:
                            actTime = arrow.now()
                            restOfPrintTime = int(listPrinters['printTime'])-int(listPrinters['printedTimeComp'])
                            msgShort += "<b>🖨 " + _("Printing") + ": \"%s\"</b>\n<i>%.1f%%</i> ~ <i>%s</i>" % (listPrinters['job'], listPrinters['done'], actTime.shift(seconds=restOfPrintTime).format('DD.MM.YYYY - HH:mm')) + "\n"
                        else:
                            msgShort += "<u><b>🔥 " + _("Heat up phase:") + ":</b></u>\n" + msgC + msgHB + msgE
                        self.threadWishState("active",threadItem)
                else:
                    loggerWS.error("Could not run msgPrinter stateList. No datas available for %s" % threadItem.name)
            msg = {}
            msg['msgLong'] = msgLong
            msg['msgShort'] = msgShort
            loggerWS.debug("msgPrinter msg long and short only for debug purpose. have to remove...\n%s" % msg)
            self.addMsgToBot(slug=slug,
                             function=threadItem.function,
                             msg=msg,
                             reply_markup=None,
                             vidPic=None,
                             priority=False,
                             botMsg=False,
                             singleMsg=False, 
                             delTime=1)
        else:
            loggerWS.error("Could not run msgPrinter listPrinters. No datas available for %s" % threadItem.name)
        return True
        
    def checkFanssStatus(self, fans):
        feedbackMsg = ""
        if len(fans) > 0:
            for i in range(0, len(fans)):
                fan = fans[i]
                if fan['on']:
                    fanSpeed = 100 * fan['voltage'] / 255
                    feedbackMsg += "<b>🌬 " + _("Fan") + " %d:</b> <i>%.0f%%</i>\n" % (i+1, fanSpeed)
                else:
                    feedbackMsg += "<b>🌬 " + _("Fan") + " %d:</b> <i>" % (i+1) + _("Off")  + "</i>\n"
        return feedbackMsg

    def checkChambersStatus(self, chambers):
        feedbackMsg = ""
        feedback = True
        if len(chambers) > 0:
            for i in range(0, len(chambers)):
                chamber = chambers[i]
                if chamber['tempRead'] > (chamber['tempSet'] - 10) and chamber['tempRead'] < (chamber['tempSet'] + 10):
                    feedbackMsg += "<b>🔆 " + _("Chamber") + " %d:</b> <i>%.1f °C<b>/</b> %.1f °C</i>\n" % (i+1, chamber['tempRead'], chamber['tempSet'])
                else:
                    feedbackMsg += "<b>🔆 " + _("Chamber") + " %d:</b> <i>%.1f °C<b>/</b> %.1f °C</i>\n" % (i+1, chamber['tempRead'], chamber['tempSet'])
                    feedback = False
        return feedback, feedbackMsg

    def checkHeatedBedsStatus(self, heatBeds):
        feedbackMsg = ""
        feedback = True
        if len(heatBeds) > 0:
            for i in range(0, len(heatBeds)):
                heatBed = heatBeds[i]
                if heatBed['tempRead'] > (heatBed['tempSet'] - 10) and heatBed['tempRead'] < (heatBed['tempSet'] + 10):
                    feedbackMsg += "<b>♨️ " + _("Heatbed") + " %d:</b> <i>%.1f °C<b>/</b> %.1f °C</i>\n" % (i+1, heatBed['tempRead'], heatBed['tempSet'])
                else:
                    feedbackMsg += "<b>♨️ " + _("Heatbed") + " %d:</b> <i>%.1f °C<b>/</b> %.1f °C</i>\n" % (i+1, heatBed['tempRead'], heatBed['tempSet'])
                    feedback = False
        return feedback, feedbackMsg

    def checkExtrudersStatus(self, extruders):
        feedbackMsg = ""
        feedback = True
        if len(extruders) > 0:
            for i in range(0, len(extruders)):
                extruder = extruders[i]
                if extruder['tempRead'] > (extruder['tempSet'] - 10) and extruder['tempRead'] < (extruder['tempSet'] + 10):
                    feedbackMsg += "<b>🔥 " + _("Extruder") + " %d:</b> <i>%.1f °C<b>/</b> %.1f °C</i>\n" % (i+1, extruder['tempRead'], extruder['tempSet'])
                else:
                    feedbackMsg += "<b>🔥 " + _("Extruder") + " %d:</b> <i>%.1f °C<b>/</b> %.1f °C</i>\n" % (i+1, extruder['tempRead'], extruder['tempSet'])
                    feedback = False
        
        return feedback, feedbackMsg

    def getExtruderStatus(self, slug, stateList):
        messageBuffer = ""
        printerConfig = self.botData['printers'][slug]['config']
        extrTempLimit = printerConfig['extrCoolTemp']
        extrAboveTempLimit = False
        extrHeating = False
        for i in range(0, len(stateList['extruder'])):
            statHotCold = True
            extruder = stateList['extruder'][i]
            if extruder['tempRead'] >= extrTempLimit or extruder['tempSet'] != 0:
                if extruder['tempSet'] != 0:
                    messageBuffer += "<b>" + _("Extruder") + " %d:</b> <i>%.1f °C<b>/</b> %.1f °C</i>\n" % (i+1, extruder['tempRead'], extruder['tempSet'])
                    extrHeating = True
                else:
                    messageBuffer += "<b>" + _("Extruder") + " %d:</b> <i>%.1f °C</i>\n" % (i+1, extruder['tempRead'])
                extrAboveTempLimit = True
        if extrAboveTempLimit:
            if extrHeating:
                if len(stateList['extruder']) > 1:
                    messageBuffer += "<b>🔥 " + _("Extruders heating up") + "</b>\n"
                else:
                    messageBuffer += "<b>🔥 " + _("Extruder heating up") + "</b>\n"
            else:
                if len(stateList['extruder']) > 1:
                    messageBuffer += "<b>🆒 " + _("Extruders cooling down") + "</b>\n"
                else:
                    messageBuffer += "<b>🆒 " + _("Extruder cooling down") + "</b>\n"
        else:
            statHotCold = False
            messageBuffer += "<i>❄️ " + _("Extruder(s) cold") + "</i>\n"
        return statHotCold, messageBuffer

    def getHeatbedStatus(self, slug, stateList):
        messageBuffer = ""
        printerConfig = self.botData['printers'][slug]['config']
        heatbTempLimit = printerConfig['heatbCoolTemp']
        heatbAboveTempLimit = False
        heatbHeating = False
        for i in range(0, len(stateList['heatedBeds'])):
            statHotCold = True
            heatbed = stateList['heatedBeds'][i]
            if heatbed['tempRead'] >= heatbTempLimit or heatbed['tempSet'] != 0:
                if heatbed['tempSet'] != 0:
                    messageBuffer += "<b>" + _("Heatbed") + " %d:</b> <i>%.1f °C<b>/</b> %.1f °C</i>\n" % (i+1, heatbed['tempRead'], heatbed['tempSet'])
                    heatbHeating = True
                else:
                    messageBuffer += "<b>" + _("Heatbed") + " %d:</b> <i>%.1f °C</i>\n" % (i+1, heatbed['tempRead'])
                heatbAboveTempLimit = True
        if heatbAboveTempLimit or heatbHeating:
            if heatbHeating:
                if len(stateList['heatedBeds']) > 1:
                    messageBuffer += "<b>♨️ " + _("Heatbeds heating up") + "</b>"
                else:
                    messageBuffer += "<b>♨️ " + _("Heatbed heating up") + "</b>"
            else:
                if len(stateList['heatedBeds']) > 1:
                    messageBuffer += "<b>🆒 " + _("Heatbeds cooling down") + "</b>"
                else:
                    messageBuffer += "<b>🆒 " + _("Heatbed cooling down") + "</b>"
        else:
            statHotCold = False
            messageBuffer += "<i>❄️ " + _("Heatbed(s) cold") + "</i>\n"
        return statHotCold, messageBuffer

    def webcamHandler(self):
        threadItem = threading.current_thread()
        slug = threadItem.slug
        type = threadItem.type
        queryData = threadItem.queryData
        webcamSelect = threadItem.webcamSelect
        captionSelect = threadItem.captionSelect
        captionText = threadItem.captionText
        if queryData != None:
            cam = int(queryData.split()[2])
            cam = cam-1
        else:
            cam = webcamSelect-1
        listPrinters = self.getPrinterDataStorage(slug, "listPrinter")
        printerConfig = self.getPrinterDataStorage(slug=slug, action="getPrinterConfig")
        webcam = printerConfig['webcams'][cam]
        if type == "pic":
            pngDir = os.path.join(PNGFILEFOLDER, slug)
            filePathPng = pathlib.Path(pngDir)
            filePathPng.mkdir(parents=True, exist_ok=True)
            loggerWS.info("Starting getting picture for %s" % slug)
            for eachFileInPath in pathlib.Path(pngDir).glob('*.png'):
                loggerWS.debug("Delete %s" % eachFileInPath)
                eachFileInPath.unlink()
            telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
            pathToVidGif = self.get_img(webcam, slug, pngDir)
            if pathToVidGif == "Error":
                loggerWS.error("Could not retrieve picture filename for %s" % slug)
                self.abortVidGif(slug)
                return
            loggerWS.info("Png received for %s" % slug)        
        elif type == "gif":
            gifDir = os.path.join(GIFFILEFOLDER, slug)
            filePathGif = pathlib.Path(gifDir)
            filePathGif.mkdir(parents=True, exist_ok=True)
            for eachFileInPath in pathlib.Path(gifDir).glob('*.png'):
                loggerWS.debug("Delete %s" % eachFileInPath)
                eachFileInPath.unlink()
            for eachFileInPath in pathlib.Path(gifDir).glob('*.gif'):
                loggerWS.debug("Delete %s" % eachFileInPath)
                eachFileInPath.unlink()
            telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
            pathToVidGif = self.get_gif(webcam, slug, gifDir)
            if pathToVidGif == "Error":
                loggerWS.error("Could not retrieve gif filename for %s" % slug)
                self.abortVidGif(slug)
                return
            loggerWS.info("Gif received for %s" % slug)
            for eachFileInPath in pathlib.Path(gifDir).glob('*.png'):
                eachFileInPath.unlink()
        elif type == "vid":
            vidDir = os.path.join(VIDFILEFOLDER, slug)
            filePathVid = pathlib.Path(vidDir)
            filePathVid.mkdir(parents=True, exist_ok=True)
            for eachFileInPath in pathlib.Path(vidDir).glob('*.avi'):
                loggerWS.debug("Delete %s" % eachFileInPath)
                eachFileInPath.unlink()
            telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
            pathToVidGif = self.get_vid(webcam, slug, vidDir)
            if pathToVidGif == "Error":
                loggerWS.error("Could not retrieve video filename for %s" % slug)
                self.abortVidGif(slug)
                return
            loggerWS.info("Video received for %s" % slug)
        else:
            loggerWS.error("Requested webcam process unknown: %s" % type)
            return
        caption='<b>/%s</b>' % slug 
        if type == "pic":
            caption+= " 📸\n"
        elif type == "gif":
            caption+= " 📽\n"
        elif type == "vid":
            caption+= " 🎦\n"
        if queryData == None:
            if captionSelect == "zHeight":
                caption += "📣🎚 <i>" + _("Print") + " <b>\"%s\" </b>" % captionText['textField1'] + _("at Z:")+ " %smm - %s</i>" % (captionText['textField2'], arrow.now().format('DD.MM.YYYY - HH:mm'))
            if captionSelect == "timeBase":
                caption += "📣⏱ <i>" + _("Print") + " <b>\"%s\" </b>" % captionText['textField1']+ " - %s</i>" % arrow.now().format('DD.MM.YYYY - HH:mm')
            if captionSelect == "endOfPrint":
                caption += "📣🏁 <i>" + _("Finished print of") + " <b>\"%s\" </b>" % captionText['textField1']+ " - %s</i>" % arrow.now().format('DD.MM.YYYY - HH:mm')
            if captionSelect == "startOfPrint":
                caption += "📣🎬 <i>" + _("Starting print of") + " <b>\"%s\" </b>" % captionText['textField1']+ " - %s</i>" % arrow.now().format('DD.MM.YYYY - HH:mm')
        else:
            if listPrinters['job'] != "none":
                caption += "<i>🖨 " + _("Prints") + " <b>\"%s\"</b> " % listPrinters['job'] + _("at") + " %.1f%%" % listPrinters['done'] + "</i>" 
            else:
                if listPrinters['online'] == 1:
                    caption += "<i>🅿️ " + _("Standby") + "</i>" 
                else:
                    caption += "<i>😴 " + _("Switched off") + "</i>"
        loggerWS.info("Caption ready for %s in path: %s" % (slug, pathToVidGif))
        msg = {}
        msg['path'] = pathToVidGif
        msg['caption'] = caption
        self.addMsgToBot(slug=slug,
                            function=type+"Request",
                            msg=msg,
                            reply_markup=None,
                            vidPic=type,
                            priority=False,
                            botMsg=True,
                            singleMsg=False,
                            ) 
        loggerWS.info("%s send for %s with path: %s, caption: %s" % (type, slug, pathToVidGif, caption))
        self.pushAllMsgToFront()
  
    def get_img(self, webcam, slug, pngDir):
        try:
            realUrlServer = self.getWebcamUrl(webcam['staticUrl'])
        except:
            loggerWS.error("Request error in getWebcamUrl of get_image for printer: %s" % slug)
            self.abortVidGif(slug)
            return "Error"
        imageName = slug + ".png"
        try:
            image = requests.get(realUrlServer)
        except OSError:  
            loggerWS.error("Request error in requests of get_image for printer: %s / %s" % (slug, realUrlServer))
            return "Error"
        if image.status_code == 200:  # we could have retrieved error page
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
            loggerWS.error("Bad http request in get_image for printer: %s" % slug)
            self.abortVidGif(slug)
            return "Error"

    def get_gif(self, webcam, slug, gifDir):
        try:
            realUrlServer = self.getWebcamUrl(webcam['staticUrl'])
        except:
            loggerWS.error("Request error in getWebcamUrl of get_gif for printer: %s " % slug)
            self.abortVidGif(slug)
            return "Error"
        for i in range(0,20):
            imageName = slug + str(i)+".png" 
            try:
                image = requests.get(realUrlServer)
            except OSError:  
                loggerWS.error("Request error in requests of get_gif for printer: %s" % slug)
                return "Error"
            if image.status_code == 200:  # we could have retrieved error page
                with open(os.path.join(gifDir, imageName), "wb") as f:
                    f.write(image.content)
                if webcam['orientation'] != 0:
                    img = cv2.imread(os.path.join(gifDir, imageName))
                    if webcam['orientation'] == 90:
                        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                    elif webcam['orientation'] == 270:
                        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif webcam['orientation'] == 180:
                        img = cv2.rotate(img, cv2.ROTATE_180)
                    status = cv2.imwrite(os.path.join(gifDir, imageName),img)
                time.sleep(0.25)
        telegramChatAction(action=telegram.ChatAction.RECORD_VIDEO_NOTE, chat_id=CHATID, token=MY_TELEGRAM_TOKEN)
        gifName = slug + ".gif"
        try:
            with imageio.get_writer(os.path.join(gifDir, gifName), mode='I') as writer:
                for fileName in os.listdir(gifDir):
                    if fileName.endswith('.png'):
                        filePathPng = os.path.join(gifDir, fileName)
                        cv2.imwrite(filePathPng, cv2.resize(cv2.imread(filePathPng), (350, 290), interpolation = cv2.INTER_AREA))
                        writer.append_data(imageio.imread(filePathPng))
        except:
            loggerWS.error("Gif creation in imageio.mimsave in buildGif for printer: %s failed" % slug)
            self.abortVidGif(slug)
            return "Error"
        try:
            optimize(os.path.join(gifDir, gifName))
            return os.path.join(gifDir, gifName)
        except TypeError as err:
            loggerWS.error("TypeError at gifsicle in buildGif: %s" % err)
        except:
            loggerWS.error("Could not optimize in buildGif gifsicle for printer: %s" % slug)
        return os.path.join(gifDir, gifName)

    def get_vid(self, webcam, slug, vidDir):
        try:
            realUrlServer = self.getWebcamUrl(webcam['dynamicUrl'])
        except:
            loggerWS.error("Request error in getWebcamUrl of get_vid for printer: %s" % slug)
            return "Error"
        fps = 24
        width = 320
        height = 270
        videoCodec = cv2.VideoWriter_fourcc(*'XVID')
        videoName = slug + ".avi"
        cap = cv2.VideoCapture(realUrlServer)
        ret = cap.set(3, width)
        ret = cap.set(4, height)
        videoFile = os.path.join(vidDir, videoName)
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
                loggerWS.error("Stream could not be read in get_Vid for printer: %s" % slug)
                return "Error"
        cap.release()
        return videoFile
        
    def getWebcamUrl(self, url):
        loggerWS.info("getWebcamUrl - transfered URL request: %s" % url)
        try:
            repetierUrl = urlparse(url)
        except:
            loggerWS.error("getWebcamUrl - could not parse URL: %s" % url)
        try:
            realUrlServer = repetierUrl._replace(netloc=RepetierServerWebcamIP + ":" + str(repetierUrl.port))
        except:
            loggerWS.error("getWebcamUrl - could not replace URL: %s" % url)
        realUrlServer = realUrlServer.geturl()
        loggerWS.info("getWebcamUrl - return URL request: %s" % realUrlServer)
        return realUrlServer

    def abortVidGif(self, slug):
        self.addMsgToBot(slug=slug,
                            function="vidGifAbort",
                            msg="📵 <b>" + _("Error on the picture/video request for printer: %s") % slug + "</b>",
                            reply_markup=None,
                            vidPic=None,
                            priority=False,
                            botMsg=True,
                            singleMsg=True,
                            ) 

    def ModelManager(self): 
        # MODELFILEFOLDER = os.path.join(os.getcwd(), 'mod') 
        # # self.botData['printers'][slug]
        # # self.botData['bot']['messageID']....['vidPic'] 
        # # setNewPrintInfo(self, msg, id=None, actPrint=None) 
        # # resetPrintInfo(self, msg) -> msg['printInfo']['id'] -> msg['printInfo']['actPrint']
        # listModels
        threadItem = threading.current_thread()
        for slug in self.botData['printers']:
            filePathModel= pathlib.Path(os.path.join(MODELFILEFOLDER, slug))
            filePathModel.mkdir(parents=True, exist_ok=True)
            listModels = self.getPrinterDataStorage(slug, "listModels")
            listPrinters = self.getPrinterDataStorage(slug, "listPrinter")
            newRenderImage = self.getPrinterDataStorage(slug, "newRenderImage")
            if newRenderImage != "Error":
                newRenderImageID = newRenderImage['id']
                data = {}
                data['id'] = None
                self.setPrinterData(slug, "newRenderImage", data)
            else:
                newRenderImageID = None
                data = {}
                data['id'] = None
                self.setPrinterData(slug, "newRenderImage", data)
            for model in listModels['data']:
                if model['analysed'] == 1:
                    loggerWS.debug("modelManager - listModels - Printer: %s, model: %s analysed" % (slug,model['name']))
                    filename = str(model['id']) + '.png'
                    fileIDToCheck = os.path.join(filePathModel, filename)                    
                    if not os.path.exists(fileIDToCheck) or model['id'] == newRenderImageID:
                        if not self.getModelPic(slug, model['id'], fileIDToCheck, "models", "m"):
                            loggerWS.error("modelManager - listModels - Printer: %s, model: %s file not downloaded: %s" % (slug,model['name'], fileIDToCheck))
                            continue
                        if model['id'] == newRenderImageID:
                            msg = "<i>" + _("Model") + " \"%s\" " % (model['name'])  + _("finished rendering for printer %s.") %(listPrinters['name']) + "</i>"
                            self.addMsgToBot(slug="Bot",
                                             function="newModelRendered",
                                             msg=msg,
                                             reply_markup=None,
                                             vidPic=None,
                                             priority=False,
                                             botMsg=True,
                                             singleMsg=True, 
                                             delTime=5
                                             )
                        else:
                            msg = "<i>" + _("Model") + " \"%s\" " % (model['name'])  + _("uploaded to printer %s.") %(listPrinters['name']) + "</i>"
                            loggerWS.info("modelManager - listModels - Printer: %s, amount of models in print queue: %d" % (slug,len(listModels['data'])))
                            self.addMsgToBot(slug="Bot",
                                             function="newModelAdded",
                                             msg=msg,
                                             reply_markup=None,
                                             vidPic=None,
                                             priority=False,
                                             botMsg=True,
                                             singleMsg=True, 
                                             delTime=5
                                             )
                else:
                    loggerWS.info("modelManager - listModels - Printer: %s, model: %s not analysed till now" % (slug,model['name']))
            for eachFileInPath in pathlib.Path(filePathModel).glob('*.png'):
                fileToDelete = True
                for model in listModels['data']:
                    if model['id'] == int(os.path.splitext(os.path.basename(eachFileInPath))[0]): 
                        fileToDelete = False
                if fileToDelete:
                    eachFileInPath.unlink()
                    loggerWS.info("modelManager - listModels - Printer: %s, amount of models in print queue: %d" % (slug,len(listModels)))
                    msg = "<i>" + _("Model removed from printer %s.") %(listPrinters['name']) + "</i>"
                    self.addMsgToBot(slug="Bot",
                                    function="delModelAdded",
                                    msg=msg,
                                    reply_markup=None,
                                    vidPic=None,
                                    priority=False,
                                    botMsg=True,
                                    singleMsg=True, 
                                    delTime=5
                                    )
            if listPrinters['job'] != "none" and self.checkPrinterInMessageID(slug):
                filePathPrint= pathlib.Path(os.path.join(filePathModel, 'print'))
                filePathPrint.mkdir(parents=True, exist_ok=True)
                if listPrinters['analysed'] == 1:
                    loggerWS.debug("modelManager - listJobs - Printer: %s, model: %s analysed" % (slug, listPrinters['jobid']))
                    filename = str(listPrinters['job']) + '.png'
                    fileIDToCheck = os.path.join(filePathPrint, filename)
                    if not os.path.exists(fileIDToCheck) or listPrinters['jobid'] == newRenderImageID:
                        if not self.getModelPic(slug, listPrinters['jobid'], fileIDToCheck, "jobs", "m"):
                            loggerWS.error("modelManager - listJobs - Printer: %s, model: %s file not downloaded: %s" % (slug, listPrinters['jobid'], fileIDToCheck))
                            continue
                        msgSwitchOver = "<i>" + _("Load preview picture") + ".....</i>"
                        msg = {}
                        msg['msgLong'] = msgSwitchOver
                        msg['msgShort'] = msgSwitchOver
                        msg['id'] = listPrinters['jobid']
                        msg['actPrint'] = fileIDToCheck
                        self.addMsgToBot(slug=slug,
                                        function="printer",
                                        msg=msg,
                                        reply_markup=None,
                                        vidPic=None,
                                        priority=True,
                                        botMsg=False,
                                        singleMsg=False, 
                                        delTime=5,
                                        modMsg="print_pic")
                        loggerWS.info("modelManager - send new print preview picture - Printer: %s, model id: %s not analysed till now" % (slug, listPrinters['jobid']))
                else:
                    loggerWS.info("modelManager - listJobs - Printer: %s, model: %s not analysed till now" % (slug, listPrinters['jobid']))
            else:
                filePathPrint= pathlib.Path(os.path.join(filePathModel, 'print'))
                filePathPrint.mkdir(parents=True, exist_ok=True)
                for eachFileInPath in pathlib.Path(filePathPrint).glob('*.png'):
                    eachFileInPath.unlink()
                    msgSwitchOver = "<i>" + _("Delete preview picture") + ".....</i>"
                    msg = {}
                    msg['msgLong'] = msgSwitchOver
                    msg['msgShort'] = msgSwitchOver
                    msg['id'] = None
                    self.addMsgToBot(slug=slug,
                                    function="printer",
                                    msg=msg,
                                    reply_markup=None,
                                    vidPic=None,
                                    priority=True,
                                    botMsg=False,
                                    singleMsg=False, 
                                    delTime=1,
                                    modMsg="print_pic")
                    loggerWS.info("modelManager - listJobs - print pic file removed %s." % (eachFileInPath))
        self.threadWishState("idle",threadItem)

    def getModelPic(self, slug, id, file, type, size):
        try:
            realUrlServer = self.getModelUrl(slug, id, type, size) # http://192.168.100.44/dyn/render_image?q=models&id=72&slug=Anycubic_i3_Mega_S&t=s
        except:
            loggerWS.error("getModelPic - URL request error for printer: %s/id: %d" % (slug,id))
            return False
        try:
            image = requests.get(realUrlServer)
        except OSError:  
            loggerWS.error("getModelPic - Request requests error for printer: %s/id: %d" % (slug,id))
            return False
        if image.status_code == 200:  # we could have retrieved error page
            with open(file, "wb") as f:
                f.write(image.content)
        else:
            loggerWS.error("getModelPic - Writing file error for printer: %s/id: %d" % (slug,id))
            return False
        return True

    def getModelUrl(self, slug, id, type, size):
        # Model http://192.168.100.44/dyn/render_image?q=models&id=72&slug=Anycubic_i3_Mega_S&t=m -> small t=l / medium t=m / t=l -> large 
        # Print http://192.168.100.44/dyn/render_image?q=jobs&id=11&slug=Anycubic_i3_Mega_S&t=m
        realUrlServer = "http://" + RepetierServerIP + ":" + RepetierServerPort + "/dyn/render_image?q=" + type + "&id=" + str(id) + "&slug=" + slug + "&t=" + size
        return realUrlServer

    def getModelFileLocation(self, slug, id):
        filePathModel= pathlib.Path(os.path.join(MODELFILEFOLDER, slug))
        filename = str(id) + '.png'
        fileLocation = os.path.join(filePathModel, filename)
        return fileLocation

    def initModels(self):
        initStart = arrow.now()
        for slug in self.botData['printers']:
            filePathModel= pathlib.Path(os.path.join(MODELFILEFOLDER, slug))
            filePathModel.mkdir(parents=True, exist_ok=True)
            while True:
                listModels = self.getPrinterDataStorage(slug, "listModels")
                if listModels == "Error":
                    loggerWS.info("initModels - listModels - Printer: %s not available. Waiting for server response" % (slug))
                    time.sleep(1)
                else:
                    loggerWS.info("initModels - listModels - Printer: %s available" % (slug))
                    break
            listPrinters = self.getPrinterDataStorage(slug, "listPrinter")
            for model in listModels['data']:
                loggerWS.debug("initModels - listModels - Printer: %s, model: %s found" % (slug,model['name']))
                filename = str(model['id']) + '.png'
                fileIDToCheck = os.path.join(filePathModel, filename)                    
                if not os.path.exists(fileIDToCheck):
                    if not self.getModelPic(slug, model['id'], fileIDToCheck, "models", "m"):
                        loggerWS.error("initModels - listModels - Printer: %s, model: %s file not downloaded: %s" % (slug,model['name'], fileIDToCheck))
                        continue
            msg = "<i>" + _("Found") + " %s " % (len(listModels['data']))  + _("models in print queue for printer %s.") %(slug) + "</i>"
            self.addMsgToBot(slug="Bot",
                                function="initModels_" + slug,
                                msg=msg,
                                reply_markup=None,
                                vidPic=None,
                                priority=False,
                                botMsg=True,
                                singleMsg=True, 
                                delTime=10
                                )
            loggerWS.info("initModels - listModels - Printer: %s, models found: %s" % (slug,len(listModels['data'])))
        initRuntime = arrow.now() - initStart
        loggerWS.info("initModels Runtime: %ssek." % initRuntime)

    def ThreadSend(self):
        threadItem = threading.current_thread()
        webs = self.botData['server']['websocket']
        if not webs['actWS'].connected:
            loggerWS.info("ThreadSend: No websocket connection. Request new websocket")
            with self.threadLock:
                feedb = self.wsWebsocket() 
            if feedb == "Error":
                loggerWS.error("ThreadSend: Could not reestablish websocket")
                return
            else:
                loggerWS.info("ThreadSend: Reestablish websocket and request renew init actions")
                self.initServerActions()
                self.initPrinterConfigActions()
                loggerWS.debug("ThreadSend: Could reestablish websocket and set request renew init actions")
            loggerWS.info("ThreadSend: Request new websocket done!")
        if webs['actWS'].connected:
            try:
                result = webs['actWS'].send(self.sendCommand)
                result = webs['actWS'].send(self.encCommand(action = "listPrinter", callback_id = self.messageCntHndl(None, "listPrinter"), printer = "", data = {}))
                result = webs['actWS'].send(self.encCommand(action = "stateList", callback_id = self.messageCntHndl(None, "stateList"), printer = "", data = {}))
            except:
                loggerWS.error("ThreadSend: %s - unexpected error: %s" % (RepetierServerIP, sys.exc_info()[0]))
                return "Error"
            with self.threadLock:
                for sendCom in self.botData['server']['websocket']['dataSendBuffer']:
                    try:
                        result = webs['actWS'].send(sendCom)
                        self.botData['server']['websocket']['dataSendBuffer'].remove(sendCom)
                    except:
                        loggerWS.error("ThreadSend: %s/%s - unexpected error: %s" % (RepetierServerIP, sendCom, sys.exc_info()[0]))
            loggerWS.debug("Thread Send aktiv")
        self.threadWishState("active",threadItem)
        
    def ThreadRec(self):
        threadItem = threading.current_thread()
        webs = self.botData['server']['websocket']
        if webs['actWS'].connected:
            try:
                resServ = webs['actWS'].recv()  
            except:
                loggerWS.error("ThreadRec unexpected error: %s" % sys.exc_info()[0])
                webs['actWS'].close()
                self.botData['server']['websocket']['actSession'] = None
                return "Error"
            with self.threadLock:
                self.botData['server']['websocket']['dataReceiveBuffer'].append(resServ)
            loggerWS.debug("Thread Rec aktiv")
        self.threadWishState("active",threadItem)            
        
    def messageCntHndl(self, slug, action):
        webs = self.botData['server']['websocket']
        webs['msgCnt']
        webs['msgCnt'] += 1    
        if webs['msgCnt'] >= 20000:
            webs['msgCnt'] = 10000
        dataSet = {}
        dataSet['callback_id'] = webs['msgCnt']
        dataSet['slug'] = slug
        dataSet['action'] = action
        with self.threadLock:
            self.botData['server']['websocket']['msgCntHandler'].append(dataSet)
        loggerWS.debug("msgCntHndl - Request %s/%s with ID: %s" % (slug,action,webs['msgCnt']))
        return webs['msgCnt']

    def getMessageCntAction(self, callback_id):
        webs = self.botData['server']['websocket']
        slug = None
        action = None
        for cntAction in webs['msgCntHandler']:
            if callback_id == cntAction['callback_id']:
                slug = cntAction['slug']
                action = cntAction['action']
                with self.threadLock:
                    webs['msgCntHandler'].remove(cntAction)
        for cntCheck in webs['msgCntHandler']:
            if webs['msgCnt'] - cntCheck['callback_id'] == 100 or webs['msgCnt'] - cntCheck['callback_id'] == -9900 :
                loggerWS.debug("getMessageCntAction - CallbackID was deleted. Request was not answered by the server: %s" % cntCheck)
                with self.threadLock:
                    webs['msgCntHandler'].remove(cntCheck)
        if slug == None and action == None:
            loggerWS.debug("getMessageCntAction - CallbackID not found: %s" % callback_id)
        return slug, action

    def setPrinterDataStorage(self, dataset):
        slug, action = self.getMessageCntAction(dataset['callback_id'])
        try:
            self.botData['server']['websocket']['actSession'] = dataset['session']
        except:
            loggerWS.debug("setPrinterDataStorage - Session ID not found for: %s" % action)
        if slug == None:
            data = dataset['data']
            if action == "listPrinter":
                for printers in data:
                    self.checkForAddPrinter(printers)
                    loggerWS.debug("setPrinterDataStorage - New %s dataset for printer \"%s\"" % (action, printers['slug']))
                    self.setPrinterData(printers['slug'], action, printers)
                    loggerWS.debug("setPrinterDataStorage - New %s dataset for printer \"%s\" stored" % (action, printers['slug']))
            elif action == "stateList":
                for printers in data:
                    loggerWS.debug("setPrinterDataStorage - New %s dataset for printer \"%s\"" % (action, printers))
                    try:
                        self.setPrinterData(printers, action, data[printers])
                    except:
                        loggerWS.error("setPrinterDataStorage - Error in %s dataset for printer \"%s\" with data: %s" % (action, printers, dataset))
                    loggerWS.debug("setPrinterDataStorage - New %s dataset for printer \"%s\" stored" % (action, printers))
            else:
                loggerWS.error("setPrinterDataStorage - New %s dataset not recognized" % (action))
        else:
            loggerWS.debug("setPrinterDataStorage - New %s dataset for server/printer \"%s\"" % (action, slug))
            data = dataset['data']
            if action == "getPrinterConfig":
                self.setPrinterData(slug, action, data)
            elif action == "listExternalCommands":
                self.setServerData(data, action)
                sendMsgToBot(slug=slug, 
                                function="listExternalCommands", 
                                msg="<i>" + _("Checked for external Commands") + "</i>", 
                                reply_markup=None,
                                singleMsg=True,
                                delTime=5)
            elif action == "sendQuickCommand":
                if data == {}:
                    sendMsgToBot(slug=slug, 
                                    function="sendQuickCommand", 
                                    msg="<b>" + _("Quick command failed") + "</b>", 
                                    reply_markup=None,
                                    singleMsg=True,
                                    delTime=5)
                else:
                    sendMsgToBot(slug=slug, 
                                    function="sendQuickCommand", 
                                    msg="<i>" + _("Quick command successful") + "</i>", 
                                    reply_markup=None,
                                    singleMsg=True,
                                    delTime=5)
            elif action == "runExternalCommand":
                sendMsgToBot(slug=slug, 
                                function="runExternalCommand", 
                                msg="<i>" + _("External command successful") + "</i>", 
                                reply_markup=None,
                                singleMsg=True,
                                delTime=5)
            elif action == "messages":
                self.setServerData(data, action)
                if len(data) != 0:
                    if self.botData['bot']['actConv'] != None:
                        if self.botData['bot']['actConv']['slug'] == _("Messages") and self.botData['bot']['actConv']['function'] == "messages":
                            sendMsgToBot(slug=_("Messages"), 
                                            function="messages", 
                                            msg="<b>" + _("Update messages required") + "...</b>", 
                                            reply_markup=getMsgKeyboard())
                        else: 
                            sendMsgToBot(slug=_("Messages"), 
                                            function="messages", 
                                            msg="<b>" + _("Update messages required") + "...</b>", 
                                            reply_markup=None)
                    else: 
                        sendMsgToBot(slug=_("Messages"), 
                                        function="messages", 
                                        msg="<b>" + _("Update messages required") + "...</b>", 
                                        reply_markup=None)
                    self.checkAddThread(threadPlace="server", thread=_("Messages"), function="messages", hdlType="messages", execute=self.servMsgAction)
                else:
                    self.removeThread(threadPlace="server", thread=_("Messages"), function="messages", hdlType="messages", msgAvail=True)
                    sendMsgToBot(slug=_("Messages"), 
                                    function="messages", 
                                    msg="<i>" + _("Removing server info messages") + "</i>", 
                                    reply_markup=None,
                                    singleMsg=True,
                                    delTime=5)
            elif action == "removeMessage":
                self.sendRecExtendedData(action="messages", slug="server", messageCntItem="messages")
                sendMsgToBot(slug=slug, 
                                function="removeMessage", 
                                msg="<i>" + _("Message removed") + "</i>", 
                                reply_markup=None,
                                singleMsg=True,
                                delTime=5)
            elif action == "listModels":
                loggerWS.debug("setPrinterDataStorage - New %s dataset for printer \"%s\"" % (action, slug))
                buffer = {}
                try:
                    buffer['data'] = data['data']
                    self.setPrinterData(slug, action, buffer)
                    loggerWS.debug("setPrinterDataStorage - New %s dataset for printer \"%s\" stored. Data: %s" % (action, slug, data['data']))
                except:
                    loggerWS.error("setPrinterDataStorage - New %s dataset for printer \"%s\" made problems. Data: %s" % (action, slug, data))                
            elif action == "listJobs":
                buffer = {}
                try:
                    buffer['data'] = data['data']
                    self.setPrinterData(slug, action, buffer)  
                    loggerWS.info("setPrinterDataStorage - New %s dataset for printer \"%s\" stored. Data: %s" % (action, slug, data['data']))
                except:
                    loggerWS.error("setPrinterDataStorage - New %s dataset for printer \"%s\" made problems. Data: %s" % (action, slug, data))
            elif action == "historySummary":
                if slug == "server":
                    if len(data['list']) != 0:
                        buffer = {}
                        buffer[data['list'][0]['year']] = data['list']
                        self.setSpecialServerData(data['list'], action, data['list'][0]['year'])
                else:
                    if len(data['list']) != 0:
                        buffer = {}
                        buffer[data['list'][0]['year']] = data['list']
                        self.setPrinterData(slug, action, buffer) 
            else:
                loggerWS.info("setPrinterDataStorage - New unknown dataset \"%s\" for printer %s: %s" % (action, slug, dataset))
            loggerWS.debug("setPrinterDataStorage - New %s data set for printer \"%s\" stored" % (action, slug))
     
    def checkForAddPrinter(self, checkPrinter):
        addPrinter = True
        for printer in self.botData['printers']:
            if checkPrinter['slug'] == printer:
                self.checkAddThread(threadPlace='printers', 
                                    thread=checkPrinter['slug'], 
                                    function="printer", 
                                    hdlType="printer", 
                                    execute=self.msgPrinter)
                addPrinter = False
        if addPrinter:
            loggerWS.info("checkForAddPrinter - Printer %s was added to the data base" % (checkPrinter['slug']))
            newPrinterConfig = self.setPrinterRoot(checkPrinter['slug'], getNewPrinterConfig(slug = checkPrinter['slug'], name = checkPrinter['name']))
            with self.threadLock:
                self.botData['printers'].update(newPrinterConfig)
            self.savePrinterConfigFile()
            self.checkAddThread(threadPlace='printers', 
                                thread=checkPrinter['slug'], 
                                function="printer", 
                                hdlType="printer", 
                                execute=self.msgPrinter)
            self.initPrinterActions(checkPrinter['slug'])

    def setPrinterRoot(self, slug, config):
        initPrinters = {}
        initPrinters[slug] = {}
        initPrinters[slug]['config'] = config
        initPrinters[slug]['threads'] = {}
        initPrinters[slug]['dataRepetier'] = {}
        return initPrinters

    def checkForDelPrinters(self, data):
        for printer in self.botData['printers'].copy():
            delPrinter = True
            for avPrinters in data:
                if avPrinters['slug'] == printer:
                    delPrinter = False
            if delPrinter:
                with self.threadLock:
                    try:
                        element = self.botData['printers'].pop(printer)
                        loggerWS.info("checkForDelPrinters - Printer %s was deleted from data base" % (element['dataRepetier']['listPrinter']['slug']))
                        self.savePrinterConfigFile()
                        self.removeThread(threadPlace='printers', 
                                          thread=element['dataRepetier']['listPrinter']['slug'], 
                                          function="printer", 
                                          hdlType="printer")
                    except KeyError:
                        loggerWS.info("checkForDelPrinters - Could not delete printer %s from data base" % (printer))

    def getPrinterDataStorage(self, slug, action):
        try:
            datas = self.botData['printers'][slug]['dataRepetier'][action] 
            return datas
        except:
            loggerWS.error("getPrinterDataStorage - Dataset %s for printer \"%s\" not available" % (action, slug))
            return "Error"

    def getServerDataStorage(self, action):
        try:
            datas = self.botData['server']['dataRepetier'][action]
            return datas
        except:
            loggerWS.error("getServerDataStorage - Server dataset %s is not available" % (action))
            return "Error"

    def getPrinterDataConfig(self, slug):
        try:
            datas = self.botData['printers'][slug]['config']
            return datas
        except:
            loggerWS.error("getPrinterDataConfig - Config for printer \"%s\" not available" % (slug))
            return "Error"

    def setPrinterData(self, slug, action, data):
        with self.threadLock:
            try:
                self.botData['printers'][slug]['dataRepetier'][action] = data
                self.botData['printers'][slug]['dataRepetier'][action]['updTime'] = time.time()
            except:
                loggerWS.error("setPrinterData - Server dataset killed me: %s/%s - \ninside: %s" % (slug, action, data))
        return data

    def setSpecialPrinterData(self, slug, action, data, postfix):
        if not action in self.botData['printers'][slug]['dataRepetier']:
            with self.threadLock:
                try:
                    self.botData['printers'][slug]['dataRepetier'][action] = {}
                    self.botData['printers'][slug]['dataRepetier'][action][postfix] = data
                    self.botData['printers'][slug]['dataRepetier'][action][postfix]['updTime'] = time.time()
                except:
                    loggerWS.error("setPrinterData - Server dataset killed me: %s/%s - \ninside: %s" % (slug, action, data))
        else:
            with self.threadLock:
                try:
                    self.botData['printers'][slug]['dataRepetier'][action][postfix] = data
                    self.botData['printers'][slug]['dataRepetier'][action][postfix]['updTime'] = time.time()
                except:
                    loggerWS.error("setPrinterData - Server dataset killed me: %s/%s - \ninside: %s" % (slug, action, data))
        return data

    def setServerData(self, data, action):
        with self.threadLock:
            self.botData['server']['dataRepetier'][action] = data
        return data

    def setSpecialServerData(self, data, action, postfix):
        if not action in self.botData['server']['dataRepetier']:
            with self.threadLock:
                self.botData['server']['dataRepetier'][action] = {}
                self.botData['server']['dataRepetier'][action][postfix] = data
        else:
            with self.threadLock:
                self.botData['server']['dataRepetier'][action][postfix] = data
        return data

    def sendRecExtendedData(self, action="ping", slug="Plastich Bomber", data={}, messageCntItem=None):
        # messageCntHndl(self, slug, action)
        self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = action, 
                                                                                        callback_id = self.messageCntHndl(messageCntItem, action), 
                                                                                        printer = slug, 
                                                                                        data = data))
        loggerWS.info("sendRecExtendedData - Sending request to Repetier-Server: %s/%s/%s" % (action,slug,data))
        
    def initPrinterActions(self, slug):
        self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "getPrinterConfig", 
                                                                                        callback_id = self.messageCntHndl(slug, "getPrinterConfig"), 
                                                                                        printer = slug, 
                                                                                        data = {}))
        self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "listModels", 
                                                                                        callback_id = self.messageCntHndl(slug, "listModels"), 
                                                                                        printer = slug, 
                                                                                        data = {}))
        self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "listJobs", 
                                                                                        callback_id = self.messageCntHndl(slug, "listJobs"), 
                                                                                        printer = slug, 
                                                                                        data = {}))
        date = arrow.now()
        data = {}
        data['year'] = date.year
        data['slug'] = slug
        data['allPrinter'] = False
        self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "historySummary", 
                                                                                        callback_id = self.messageCntHndl(slug, "historySummary"), 
                                                                                        printer = slug, 
                                                                                        data = data))
        loggerWS.info("initPrinterActions - Sending request to Repetier-Server")

    def initServerActions(self):
        self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "listExternalCommands", 
                                                                                        callback_id = self.messageCntHndl("listExternalCommands", "listExternalCommands"), 
                                                                                        printer = "server", 
                                                                                        data = {}))
        self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "messages", 
                                                                                        callback_id = self.messageCntHndl("messages", "messages"), 
                                                                                        printer = "server", 
                                                                                        data = {}))
        date = arrow.now()
        data = {}
        data['year'] = date.year - 1
        data['slug'] = "server"
        data['allPrinter'] = True
        self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "historySummary", 
                                                                                        callback_id = self.messageCntHndl("server", "historySummary"), 
                                                                                        printer = "server", 
                                                                                        data = data))
        data['year'] = date.year
        self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "historySummary", 
                                                                                        callback_id = self.messageCntHndl("server", "historySummary"), 
                                                                                        printer = "server", 
                                                                                        data = data))
        loggerWS.info("initServerActions - Sending request to Repetier-Server")
    
    def initPrinterConfigActions(self):
        for slug in self.botData['printers']:
            self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "getPrinterConfig", 
                                                                                        callback_id = self.messageCntHndl(slug, "getPrinterConfig"), 
                                                                                        printer = slug, 
                                                                                        data = {}))
            self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "listModels", 
                                                                                        callback_id = self.messageCntHndl(slug, "listModels"), 
                                                                                        printer = slug, 
                                                                                        data = {}))
            self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "listJobs", 
                                                                                        callback_id = self.messageCntHndl(slug, "listJobs"), 
                                                                                        printer = slug, 
                                                                                        data = {}))
            date = arrow.now()
            data = {}
            data['year'] = date.year - 1
            data['slug'] = slug
            data['allPrinter'] = False
            self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "historySummary", 
                                                                                            callback_id = self.messageCntHndl(slug, "historySummary"), 
                                                                                            printer = slug, 
                                                                                            data = data))     
            data['year'] = date.year
            self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "historySummary", 
                                                                                            callback_id = self.messageCntHndl(slug, "historySummary"), 
                                                                                            printer = slug, 
                                                                                            data = data))
        loggerWS.info("initPrinterConfigActions - Sending request to Repetier-Server")

    def checkAddThread(self, threadPlace, thread, function, hdlType, execute):
        threadActive = False
        if threadPlace == "printers":
            threadList = self.botData['printers'][thread]['threads']            
        elif threadPlace == "server":
            threadList = self.botData['server']['threads']
        else:
            threadActive = True
            loggerWS.critical("checkAddThread - Thread request %s unknown for %s/%s" % (threadPlace, thread, function))
        with self.threadLock:
            try:
                for threadItem in threadList:
                    if threadItem == function:
                        if not threadList[threadItem].is_alive():
                            loggerWS.critical("checkAddThread - Restart dead thread %s/%s" % (thread, threadItem))
                            threadList.pop(threadItem)
                            newThread = {}
                            newThread[function] = self.startActionThread(name=thread, 
                                                                            slug=thread, 
                                                                            execute=execute, 
                                                                            function=function, 
                                                                            interval=THRDIDLE, 
                                                                            addData = None) 
                            threadList.update(newThread)
                        threadActive = True
            except:
                loggerWS.critical("checkAddThread - Something went wrong during the loop -> thread died, like message thread")
        if not threadActive:
            newThread = {}
            newThread[function] = self.startActionThread(name=thread, 
                                                            slug=thread, 
                                                            execute=execute, 
                                                            function=function, 
                                                            interval=THRDIDLE, 
                                                            addData = None)
            with self.threadLock:
                loggerWS.info("checkAddThread - Start thread %s/%s and add handler %s" % (thread, function, thread))
                threadList.update(newThread)
            self.addHandler(item=thread,hdlType=hdlType)
            
    def removeThread(self, threadPlace, thread, function, hdlType=None, msgAvail=True):
        threadActive = False
        if threadPlace == "printers":
            threadList = self.botData['printers'][thread]['threads']            
        elif threadPlace == "server":
            threadList = self.botData['server']['threads']
        with self.threadLock:
            for threadItem in threadList.copy():
                if threadItem == function:
                    loggerWS.info("removeThread - Remove thread %s/%s" % (thread, threadItem))
                    toRemove = threadList.pop(threadItem)
                    self.removeHandler(item=thread, hdlType=hdlType) # item, hdlType=None
                    if msgAvail:
                        self.remMsgFromBuffer(thread, function)
                        self.remMsgFromBot(thread, function)
                        loggerWS.info("removeThread - Removed message %s/%s" % (thread, function))
                    threadActive = True
                    loggerWS.info("removeThread - Removed %s/%s and handler %s" % (thread, function, thread))
        if not threadActive:
            loggerWS.info("removeThread - Could not find %s/%s and handler %s" % (thread, function, thread))
           
    def ThreadHdlOrderData(self):
        threadItem = threading.current_thread()
        startTime = arrow.now()
        #check for printer change in Repetier Server
        with self.threadLock:
            orderDataRaw = self.botData['server']['websocket']['dataReceiveBuffer']
            self.botData['server']['websocket']['dataReceiveBuffer'] = []
        for orderDataRawItem in orderDataRaw:
            try:
                dataSetItems = json.loads(orderDataRawItem)                
            except:
                loggerWS.error("ThreadHdlOrderData - JSON load failed")
                continue
            if dataSetItems['callback_id'] == -1:
                try:
                    dataSets = dataSetItems['data']
                except:
                    loggerWS.error("ThreadHdlOrderData - Data structure missing \"data\"-key")
                    continue
                for dataSet in dataSets:
                    try:
                        eventType = dataSet['event']                    
                    except:
                        loggerWS.error("ThreadHdlOrderData - Event key missing in: " % dataSet)
                        continue
                    loggerWS.debug("ThreadHdlOrderData looking up for event: " + str(eventType))
                    if eventType == "jobFinished":
                    # Payload: {start:unixTime,duration:seconds,end:unixTime,lines:linesOfJob} / Gets send after a normal job has finished. 
                    # # {'duration': 5507, 'end': 5507, 'lines': 117373, 'start': 1603207724}, 'event': 'jobFinished', 'printer': 'Anycubic_Mega_X1'}
                        printerConfig = self.getPrinterDataConfig(dataSet['printer'])
                        present = arrow.now()
                        future = present.shift(seconds=dataSet['data']['duration'])                                
                        messageBuffer = "%s" % (printerConfig['name']) + _(" has finished the print.") 
                        loggerWS.info("eventType: jobFinished: %s" % messageBuffer)
                        self.addMsgToBot(slug="Bot",
                                         function="jobFinished",
                                         msg="<b>%s</b>" % messageBuffer,
                                         reply_markup=None,
                                         vidPic=None,
                                         priority=False,
                                         botMsg=True,
                                         singleMsg=True, 
                                         delTime=20
                                         )
                        if printerConfig['extrCoolTempExtComm'] != None:
                            self.startActionThread(name=printerConfig['name'], 
                                                    slug=printerConfig['slug'], 
                                                    execute=self.coolDownAction, 
                                                    function="coolDownActionExtr", 
                                                    interval=THRDSLOW)
                        if printerConfig['heatbCoolTempExtComm'] != None:
                            self.startActionThread(name=printerConfig['name'], 
                                                    slug=printerConfig['slug'], 
                                                    execute=self.coolDownAction, 
                                                    function="coolDownActionHeatb", 
                                                    interval=THRDSLOW)
                        buffer = {}
                        buffer['printerConfig'] = printerConfig
                        buffer['listPrinters'] = self.getPrinterDataStorage(printerConfig['slug'], "listPrinter")
                        if printerConfig['AfterPrintPicCamSelect'] != None:
                            self.startActionThread(name=printerConfig['name'], 
                                                    slug=printerConfig['slug'], 
                                                    execute=self.sendPicAfterPrint, 
                                                    function="sendPicAfterPrint", 
                                                    interval=printerConfig['delayTimeAfterPrintPic'],
                                                    addData=buffer)
                        date = arrow.now()
                        data = {}
                        data['year'] = date.year
                        data['slug'] = "server"
                        data['allPrinter'] = True
                        self.sendRecExtendedData(action="historySummary", slug="server", data=data, messageCntItem="server")
                        data['slug'] = slug
                        data['allPrinter'] = False
                        self.sendRecExtendedData(action="historySummary", slug=slug, data=data, messageCntItem="slug")

                    elif eventType == "messagesChanged":
                        loggerWS.info("eventType: messagesChanged detected")
                        self.sendRecExtendedData(action="messages", slug="server", messageCntItem="messages")

                    elif eventType == "jobKilled":
                    # Payload: {start:unixTime,duration:seconds,end:unixTime,lines:linesOfJob} / Gets send after a normal job has been killed.
                        listPrinter = self.getPrinterDataStorage(dataSet['printer'],"listPrinter")
                        present = arrow.now()
                        past = present.shift(seconds=dataSet['data']['duration'])                                          
                        messageBuffer = _("Print from %s was aborted after %s") % (listPrinter['name'], past.humanize(present,locale='de', only_distance=True, granularity=["minute","second"])) 
                        loggerWS.info("eventTyp: jobKilled: %s" % messageBuffer)
                        self.addMsgToBot(slug="Bot",
                                         function="jobKilled",
                                         msg="<b>%s</b>" % messageBuffer,
                                         reply_markup=None,
                                         vidPic=None,
                                         priority=False,
                                         botMsg=True,
                                         singleMsg=True, 
                                         delTime=20
                                         )
                        date = arrow.now()
                        data = {}
                        data['year'] = date.year
                        data['slug'] = "server"
                        data['allPrinter'] = True
                        self.sendRecExtendedData(action="historySummary", slug="server", data=data, messageCntItem="server")
                        data['slug'] = slug
                        data['allPrinter'] = False
                        self.sendRecExtendedData(action="historySummary", slug=slug, data=data, messageCntItem="slug")
                        
                    elif eventType == "jobStarted":
                    # Payload: {start:unixTime} / Gets send after a normal job has been started. {'data': {'start': 1603036621}, 'event': 'jobStarted', 'printer': 'Anycubic_i3_Mega_S'}
                        loggerWS.info("eventTyp: jobStarted detected")
                        #test2 = {}
                        #test2['textField1'] = _("START GUT, ALLES GUT")
                        #botThreads.startWebcamThread(slug=botGetTracking(context),
                        #                            name="test_start", 
                        #                            type="pic", 
                        #                            webcamSelect=1,
                        #                            captionSelect="startOfPrint",
                        #                            captionText=test2)# <-- captionText['textField1']
                        printerConfig = self.getPrinterDataConfig(dataSet['printer'])
                        listPrinter = self.getPrinterDataStorage(dataSet['printer'],"listPrinter")
                        jobTitle = listPrinter['job']
                        messageBuffer = _("%s has started printing at %s.") % (listPrinter['name'], 
                                                                        arrow.get(dataSet['data']['start']).format('DD.MM.YYYY - HH:mm'))
                                                                         
                        loggerWS.info("eventTyp: jobStarted: %s" % messageBuffer)
                        if printerConfig['zHeightPrintPicCamSelect'] != None:
                            self.startActionThread(name=printerConfig['name'], 
                                                    slug=printerConfig['slug'], 
                                                    execute=self.sendPicAfterzHeight, 
                                                    function="sendPicAfterzHeight", 
                                                    interval=THRDSLOW,
                                                    addData=None)
                        if printerConfig['timeBasedPrintPicCamSelect'] != None:
                            self.startActionThread(name=printerConfig['name'], 
                                                    slug=printerConfig['slug'], 
                                                    execute=self.sendPicAfterTimeBase, 
                                                    function="sendPicAfterTimeBase", 
                                                    interval=THRDSLOW,
                                                    addData=None)
                        self.addMsgToBot(slug="Bot",
                                         function="jobStarted",
                                         msg="<b>%s</b>" % messageBuffer,
                                         reply_markup=None,
                                         vidPic=None,
                                         priority=False,
                                         botMsg=True,
                                         singleMsg=True, 
                                         delTime=20
                                         )
                        
                    elif eventType == "changeFilamentRequested":
                    # Payload: none / Firmware requested a filament change on server side.
                        loggerWS.info("eventTyp: changeFilamentRequested detected")
                        timeDelThread(feedbackMsg = telegramSendMsg("Drucker Filament Ende\n\n" + str(dataSet),reply_markup=None, chat_id=CHATID, token=MY_TELEGRAM_TOKEN))

                    elif eventType == "config": # general slug
                        self.sendRecExtendedData(action="getPrinterConfig", slug=dataSet['printer'], messageCntItem=dataSet['printer'])

                    elif eventType == "printqueueChanged": # {'slug': 'Anycubic_i3_Mega_S'}
                        slug = dataSet['data']['slug']
                        self.sendRecExtendedData(action="listJobs", slug=slug, data={}, messageCntItem=slug)

                    elif eventType == "jobsChanged": # {'slug': 'Anycubic_Mega_X1'}
                        slug = dataSet['data']['slug']
                        self.sendRecExtendedData(action="listModels", slug=slug, data={}, messageCntItem=slug)
                        self.sendRecExtendedData(action="listJobs", slug=slug, data={}, messageCntItem=slug)

                    elif eventType == "newRenderImage": # {'id': 94, 'list': 'models', 'slug': 'Anycubic_Mega_X1'}
                        slug = dataSet['data']['slug']
                        id = dataSet['data']['id']
                        with self.threadLock:
                            self.botData['printers'][slug]['dataRepetier']['newRenderImage']['id'] = id
                    else:
                        # ignored messages
                        if eventType == "userCredentials":
                            doNothing = True
                        elif eventType == "timer60": 
                            doNothing = True
                        elif eventType == "timer30": 
                            doNothing = True
                        elif eventType == "timer300": 
                            doNothing = True
                        elif eventType == "timer1800": 
                            doNothing = True
                        elif eventType == "timer3600": 
                            doNothing = True
                        elif eventType == "wifiChanged":
                            doNothing = True
                        elif eventType == "hardwareInfo":
                            doNothing = True
                        elif eventType == "modelGroupListChanged":
                            doNothing = True
                        elif eventType == "jobsChanged":
                            loggerWS.info("eventTyp: %s - %s" % (eventType, dataSet['data']))
                            doNothing = True
                        elif eventType == "temp":
                            doNothing = True
                        elif eventType == "printerListChanged": # [{'active': True, 'job': 'none', 'name': 'Anycubic Mega X', 'online': 2, 'pauseState': 0, 'paused': False, 'slug': 'Anycubic_Mega_X1'}, 
                                                                # {'active': True, 'job': 'none', 'name': 'Anycubic i3 Mega S', 'online': 0, 'pauseState': 0, 'paused': False, 'slug': 'Anycubic_i3_Mega_S'}]
                            doNothing = True
                        elif eventType == "timelapseChanged":
                            doNothing = True
                        elif eventType == "prepareJob": # {}
                            doNothing = True
                        elif eventType == "gcodeInfoUpdated": # {'modelId': 10, 'modelPath': '/var/lib/Repetier-Server/printer/Anycubic_i3_Mega_S/jobs/00000010_AI3M_201215_Ausstecher_Ana v1.u', 'slug': 'Anycubic_i3_Mega_S'}
                            doNothing = True
                        elif eventType == "prepareJobFinished": # {}
                            doNothing = True
                        elif eventType == "dispatcherCount": # {'count': 1}
                            doNothing = True
                        elif eventType == "workerFinished": # {'id': 1, 'message': '', 'type': 'lua'}
                            doNothing = True
                        #elif eventType == "prepareJob": #
                        #    doNothing = True
                        else:
                            try:
                                loggerWS.info("eventTyp: %s - %s" % (eventType, dataSet['data']))
                            except:
                                loggerWS.info("eventTyp (except): %s - %s" % (eventType, dataSet))
            else:
                self.setPrinterDataStorage(dataSetItems)                
        stopTime = arrow.now() 
        runTime = stopTime - startTime        
        loggerWS.debug("Order Storage Runtime: %ssek." % runTime)
        self.threadWishState("active",threadItem)

    def coolDownAction(self):
        threadItem = threading.current_thread()
        slug = threadItem.slug
        function = threadItem.function
        listPrinters = self.getPrinterDataStorage(slug, "listPrinter")
        if listPrinters['job'] != "none":
            messageBuffer = "🛑❄️<b>" + _("Execution of cool down action aborted for %s") % listPrinters['name'] + "</b>❄️"
            self.addMsgToBot(slug="Bot",
                            function="coolDownAction",
                            msg="<b>%s</b>" % messageBuffer,
                            reply_markup=None,
                            vidPic=None,
                            priority=False,
                            botMsg=True,
                            singleMsg=True, 
                            delTime=20
                            )
            loggerWS.info("coolDownAction: abort order to server for %s" % slug)
            return False
        state = self.getPrinterDataStorage(slug, "stateList")
        if state != "Error":
            printerConfig = self.botData['printers'][slug]['config']
            belowLimit = True
            if function == "coolDownActionExtr":
                tempLimit = printerConfig['extrCoolTemp']
                for extruder in state['extruder']:
                    if extruder['tempRead'] > float(tempLimit):
                        belowLimit = False
            elif function == "coolDownActionHeatb":
                tempLimit = printerConfig['heatbCoolTemp']
                for heatbed in state['heatedBeds']:
                    if heatbed['tempRead'] > float(tempLimit):
                        belowLimit = False
            if belowLimit == True:
                packOrder = {}
                if function == "coolDownActionExtr":
                    if printerConfig['extrCoolTempExtComm'] == None:
                        return False
                    packOrder['id'] = printerConfig['extrCoolTempExtComm']
                    messageBuffer = "❄️<b>" + _("Extruder cool down external command execute for printer %s") % printerConfig['name'] + "</b>❄️"
                elif function == "coolDownActionHeatb":
                    if printerConfig['heatbCoolTempExtComm'] == None:
                        return False
                    packOrder['id'] = printerConfig['heatbCoolTempExtComm']
                    messageBuffer = "❄️<b>" + _("Heatbed cool down external command execute for printer %s") % printerConfig['name'] + "</b>❄️"
                self.botData['server']['websocket']['dataSendBuffer'].append(self.encCommand(action = "runExternalCommand", 
                                                                            callback_id = self.messageCntHndl(slug, "runExternalCommand"), 
                                                                            printer = slug, 
                                                                            data = packOrder))
                self.addMsgToBot(slug="Bot",
                                         function="coolDownAction",
                                         msg="<b>%s</b>" % messageBuffer,
                                         reply_markup=None,
                                         vidPic=None,
                                         priority=False,
                                         botMsg=True,
                                         singleMsg=True, 
                                         delTime=20
                                         )
                loggerWS.info("coolDownAction: send order to server for %s" % slug)
                return False
        self.threadWishState("off",threadItem)
        return True
    
    def sendPicAfterPrint(self):
        threadItem = threading.current_thread()
        slug = threadItem.slug
        buffer = threadItem.addData
        printerConfig = buffer['printerConfig']
        listPrinter = buffer['listPrinters']
        picText = {}
        if listPrinter['job'] != "none":
            picText['textField1'] = listPrinter['job']
        else:
            picText['textField1'] = _("unknown print")
        botThreads.startWebcamThread(slug=printerConfig['slug'],
                                    name="endOfPrint", 
                                    type="pic", 
                                    webcamSelect=printerConfig['AfterPrintPicCamSelect']+1,
                                    captionSelect="endOfPrint",
                                    captionText=picText)# <-- captionText['textField1']
        return False
    
    def sendPicAfterzHeight(self):
        threadItem = threading.current_thread()
        slug = threadItem.slug
        listPrinter = self.getPrinterDataStorage(slug,"listPrinter")
        if listPrinter['job'] == "none":
            loggerWS.info("Exit pic after z height for %s" % slug)
            return False
        else:
            state = self.getPrinterDataStorage(slug, "stateList") # layer, z
            printerConfig = self.getPrinterDataConfig(slug)
            if threadItem.addData == None: 
                buffer = {}
                if printerConfig['zHeightPrintPic'] <= 0.0:
                    loggerWS.error("sendPicAfterzHeight - z height config for printer \"%s\" out of range: %.1fmm" % (slug, printerConfig['zHeightPrintPic']))
                    buffer['zConfig'] = 1.0
                else:
                    buffer['zConfig'] = printerConfig['zHeightPrintPic']
                buffer['nextZ'] = buffer['zConfig']
                threadItem.addData = buffer
                loggerWS.info("sendPicAfterzHeight - z height config for printer \"%s\" set to: %.1fmm" % (slug, buffer['zConfig']))
            else:
                buffer = threadItem.addData
                if state['z'] >= buffer['nextZ'] and state['layer'] > 0:
                    loggerWS.info("sendPicAfterzHeight - Actual layer for printer \"%s\" is: %s" % (slug, state['layer']))
                    if printerConfig['zHeightPrintPicCamSelect'] != None:
                        picText = {}
                        picText['textField1'] = listPrinter['job']
                        picText['textField2'] = "%.1f" % state['z'] # z height value
                        botThreads.startWebcamThread(slug=printerConfig['slug'],
                                                name="zHeight", 
                                                type="pic", 
                                                webcamSelect=printerConfig['zHeightPrintPicCamSelect']+1,
                                                captionSelect="zHeight",
                                                captionText=picText)# <-- captionText['textField1']
                    if printerConfig['zHeightPrintPic'] <= 0.0:
                        loggerWS.error("sendPicAfterzHeight - z height config for printer \"%s\" out of range: %.1fmm" % (slug, printerConfig['zHeightPrintPic']))
                        buffer['zConfig'] = 1.0
                    else:
                        buffer['zConfig'] = printerConfig['zHeightPrintPic']                    
                    buffer['nextZ'] = state['z'] + buffer['zConfig']
                    threadItem.addData = buffer
                    loggerWS.info("sendPicAfterzHeight - next z height for printer \"%s\" set to: %.1fmm" % (slug, buffer['nextZ']))
        return True
        
    def sendPicAfterTimeBase(self):
        threadItem = threading.current_thread()
        slug = threadItem.slug
        listPrinter = self.getPrinterDataStorage(slug,"listPrinter")
        if listPrinter['job'] == "none":
            loggerWS.info("Exit pic after time for %s" % slug)
            return False
        else:
            printerConfig = self.getPrinterDataConfig(slug)
            if threadItem.addData == None: 
                buffer = {}
                if printerConfig['timeBasedPrintPic'] <= 0 or printerConfig['timeBasedPrintPic'] > 60:
                    loggerWS.error("sendPicAfterTimeBase - time config for printer \"%s\" out of range: %s min" % (slug, printerConfig['timeBasedPrintPic']))
                    buffer['timeDiff'] = 10
                else:
                    buffer['timeDiff'] = printerConfig['timeBasedPrintPic']
                now = arrow.now()
                buffer['nextTime'] = now.shift(minutes=buffer['timeDiff'])
                threadItem.addData = buffer
                loggerWS.info("sendPicAfterTimeBase - time config for printer \"%s\" set to: %s min. Next pic at: %s" % (slug, 
                                                                                                                        buffer['timeDiff'], 
                                                                                                                        buffer['nextTime'].format('DD.MM.YYYY - HH:mm')))
            else:
                buffer = threadItem.addData
                if arrow.now() >= buffer['nextTime']:
                    if printerConfig['timeBasedPrintPicCamSelect'] != None:
                        picText = {}
                        picText['textField1'] = listPrinter['job']
                        botThreads.startWebcamThread(slug=printerConfig['slug'],
                                                    name="timeBase", 
                                                    type="pic", 
                                                    webcamSelect=printerConfig['timeBasedPrintPicCamSelect']+1,
                                                    captionSelect="timeBase",
                                                    captionText=picText)# <-- captionText['textField1']
                    buffer = {}
                    if printerConfig['timeBasedPrintPic'] <= 0 or printerConfig['timeBasedPrintPic'] > 60:
                        loggerWS.error("sendPicAfterTimeBase - time config for printer \"%s\" out of range: %s min" % (slug, printerConfig['timeBasedPrintPic']))
                        buffer['timeDiff'] = 10
                    else:
                        buffer['timeDiff'] = printerConfig['timeBasedPrintPic']
                    now = arrow.now()
                    buffer['nextTime'] = now.shift(minutes=buffer['timeDiff'])
                    threadItem.addData = buffer
                    loggerWS.info("sendPicAfterTimeBase - next time pic for printer \"%s\" at: %s" % (slug, buffer['nextTime'].format('DD.MM.YYYY - HH:mm')))
        return True
    
    def servMsgAction(self):
        threadItem = threading.current_thread()
        slug = threadItem.slug
        msg = botThreads.getServerDataStorage(action="messages")
        if len(msg) == 0:
            self.removeThread(threadPlace="server", 
                              thread=_("Messages"), 
                              function="messages", 
                              hdlType="messages", 
                              msgAvail=True)
            loggerWS.info("servMsgAction: terminating messages thread")
            return False
        msgBasis = "<b>/" + _("Messages") + "</b>\n"
        msgBasis += "<code>" + _("Update: %s at %s") % (arrow.now().format('DD.MM.YYYY'), arrow.now().format('HH:mm:ss')) + "</code>\n"
        msgLong = msgBasis
        msgShort = msgBasis
        for message in msg:
            name = "server"
            for item in self.botData['printers']:
                if message['slug'] == item:
                    name = self.botData['printers'][item]['config']['name']
            msgLong += "<b>[%s]: %s, %s</b>\n<code>%s</code>\n\n" % (message['id'],arrow.get(message['date']).format('DD.MM.YYYY - HH:mm'),
                                                                            name,
                                                                            message['msg'])
        lastMsg = len(msg)-1
        message = msg[lastMsg]
        name = "server"
        for item in self.botData['printers']:
            if message['slug'] == item:
                name = self.botData['printers'][item]['config']['name']
        msgShort += "<b><i>" + _("Last message") + "</i> [%s]: %s, %s</b>\n<code>%s</code>" % (message['id'],arrow.get(message['date']).format('DD.MM.YYYY - HH:mm'),
                                                                                                        name,
                                                                                                        message['msg'])
        msg = {}
        msg['msgLong'] = msgLong
        msg['msgShort'] = msgShort
        self.addMsgToBot(slug=slug,
                            function=threadItem.function,
                            msg=msg,
                            reply_markup=None,
                            vidPic=None,
                            priority=False,
                            botMsg=False,
                            singleMsg=False, 
                            delTime=1)
        self.threadWishState("standby",threadItem)
        return True
                
    def ThreadHdlRestart(self):
        hdlRestartThread = threading.current_thread()
        loggerWS.debug("Threads Alive:\nwsThreadSend: %s, wsThreadRec: %s, wswsThreadOrderData: %s, botCommunicator: %s, threadManager: %s, modelManager: %s,wsThreadRestart: %s" % (
                                                                                self.wsThreadSend.is_alive(), 
                                                                                self.wsThreadRec.is_alive(),
                                                                                self.wsThreadOrderData.is_alive(),
                                                                                self.botCommunicator.is_alive(),
                                                                                self.threadManager.is_alive(),
                                                                                self.modelManager.is_alive(),
                                                                                self.wsThreadRestart.is_alive()
                                                                                )
                       )
        loggerWS.debug("Threads Restarts:\nRestarts websocket send: %d, restarts websocket receive: %d, restarts order data: %d, restarts thread manager: %d, restarts model manager: %d,restarts bot communicator: %d" % (
                                                                                self.restartWsSend, 
                                                                                self.restartWsReceive,
                                                                                self.restartOrderData,
                                                                                self.restartThdMan,
                                                                                self.restartModelManager,
                                                                                self.restartbotCom
                                                                                )
                       )
        if not self.wsThreadSend.is_alive():
            if self.restartWsSend >= 100000:
                loggerWS.info("wsThreadSend reset restart counter")
                self.restartWsSend = 0
            self.restartWsSend += 1
            self.wsThreadSend = dataHdlThread(interval=THRDSEND, execute=self.ThreadSend, name="Repetier-Server-Send")
            self.wsThreadSend.start()
            loggerWS.info("wsThreadSend restartet. Counter: %d" % self.restartWsSend)
        if  not self.wsThreadRec.is_alive():
            if self.restartWsReceive >= 100000:
                loggerWS.info("wsThreadRec reset restart counter")
                self.restartWsReceive = 0
            self.restartWsReceive += 1
            self.wsThreadRec = dataHdlThread(interval=THRDRECEIVE, execute=self.ThreadRec, name="Repetier-Server-Receive")
            self.wsThreadRec.start()
            loggerWS.info("wsThreadRec restartet. Counter: %d" % self.restartWsReceive)
        if not self.wsThreadOrderData.is_alive():
            if self.restartOrderData >= 100000:
                loggerWS.info("wsThreadOrderData reset restart counter")
                self.restartOrderData = 0
            self.restartOrderData += 1
            self.wsThreadOrderData = dataHdlThread(interval=THRDORDERDATA, execute=self.ThreadHdlOrderData, name="Repetier-Server-Order-Data")
            self.wsThreadOrderData.start()
            loggerWS.info("wsThreadOrderData restartet. Counter: %s" % self.restartOrderData)
        if not self.threadManager.is_alive():
            if self.restartThdMan >= 100000:
                loggerWS.info("threadManager reset restart counter")
                self.restartThdMan = 0
            self.restartThdMan += 1
            self.threadManager = dataHdlThread(interval=THRDMANAGER, execute=self.ThreadManager, name="Repetier-Server-Thread-Manager")
            self.threadManager.start()
            loggerWS.info("threadManager restartet. Counter: %s" % self.restartThdMan)
        if not self.modelManager.is_alive():
            if self.restartModelManager >= 100000:
                loggerWS.info("modelManager reset restart counter")
                self.restartModelManager = 0
            self.restartModelManager += 1
            self.modelManager.join()
            self.modelManager = dataHdlThread(interval=THRDMODELMAN, execute=self.ModelManager, name="Repetier-Server-Model-Manager")
            self.modelManager.start()
            loggerWS.info("modelManager restartet. Counter: %s" % self.restartModelManager)
        if  not self.botCommunicator.is_alive():
            if self.restartbotCom >= 100000:
                loggerWS.info("botCommunicator reset restart counter")
                self.restartbotCom = 0
            self.restartbotCom += 1
            self.botCommunicator = dataHdlThread(interval=THRDBOTCOM, execute=self.ThreadHdlBot, name="Repetier-Server-Bot-Communication-Threads")
            self.botCommunicator.start()
            loggerWS.info("botCommunicator restartet. Counter: %d" % self.restartbotCom)
        loggerWS.debug("Amount of active threads. Value: %d" % threading.active_count())
        listThreads = threading.enumerate()
        for threads in listThreads:
            loggerWS.debug("Thread: %s" % threads)
        if self.botData['server']['websocket']['timeout'] != None:
            actTimeout = self.botData['server']['websocket']['timeout']
            if self.nextRSTimeoutMsg == None:
                self.nextRSTimeoutMsg = actTimeout.shift(minutes=15)
                loggerWS.error("Repetier Server webserver timeout. Started: %s" % self.botData['server']['websocket']['timeout'])
            elif self.nextRSTimeoutMsg < arrow.now():
                self.nextRSTimeoutMsg = arrow.now().shift(minutes=15)
                msg = "🛑<b>" + _("Repetier Server connection timeout. Started at: %s") % actTimeout.format('DD.MM.YYYY - HH:mm') + " ‼️</b>"
                self.addMsgToBot(slug="Bot",
                             function="timeoutRSWS",
                             msg=msg,
                             reply_markup=None,
                             vidPic=None,
                             priority=False,
                             botMsg=True,
                             singleMsg=True, 
                             delTime=30
                             )
        self.threadWishState("active",hdlRestartThread)
        
    def printThreadStatsInLogger(self):
        loggerWS.info("Bot thread counter statistic:\nSend: %d\nReceive: %d\nOrder-Data: %d\nBot Communication: %d\nThread Manager: %d\nModel Manager: %d" % (self.restartWsSend,
                                                            self.restartWsReceive,
                                                            self.restartOrderData,
                                                            self.restartbotCom,
                                                            self.restartThdMan,
                                                            self.restartModelManager))


# 🏁 Ziel / 💯 100% #   🇬🇧 🇺🇸 Fahnen  # 📣 Horn # 🔔 🔕 soung/no sound  # 🖕 Stinkefinger # 🔥 Flame  # ♨️ hot # 🔆 sun
# ❄️ cold 🆒 cool # 🌬 blow  🌪 Tornado # ⛔️ 💤 Stop # 🚽 💩 abort # 🚧 warning # 🅿️ park  # 💡 hint  # ⚙️ gear # 💧 multiplier
# 📵 no phone 🎦 📽 Movie # 📸 picture # 🤷‍♂️ what do you want? # 🖨 printing

### Main code
if __name__ == "__main__":
    threading.current_thread().name = FILENAME_NO_EXTENSION
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    logger = setup_logger("Main Thread",formatter,logging.INFO,LOGFILENAME)
    loggerWS = setup_logger("WS Thread",formatter,logging.INFO,LOGFILENAMEWS)
    
    changeLang(None)
    presLan.install()
    _ = presLan.gettext

    logger.info("########### Repetier-Server Bot ###########")
    logger.info("Software Version: %s" % SW_VERSION)
    logger.info("Thread Name: %s" % threading.current_thread().getName())
    logger.info("########### Geräte and Python Information ###########")
    logger.info("Python Version: %s" % platform.python_version())
    logger.info("OS: %s" % platform.system())
    logger.info("OS Version: %s" % platform.platform())
    username = getpass.getuser()
    logger.info("Active User: %s" % username)
    logger.info("####################################")

    # Import Konfigurationsdatei
    configFile = impConfig()
    presLan.install()
    _ = presLan.gettext

    # Bot
    updater = Updater(MY_TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Websocket - Repetier-Server Testumgebung
    botThreads = botThreadHdl(dp, configFile)
    botThreads.start()
    
    dp.add_handler(CommandHandler('reset', resetMsgs))
    addDebugHandler(dp)
    remPrinterFromBot(dp)
    repetierBotStats(dp)
    
    dp.add_error_handler(error_callback) 
    
    updater.start_polling()
    updater.idle()

    # Programm wird beendet
    botThreads.printThreadStatsInLogger()
    botThreads.stop()
    numActiveThread = threading.active_count()
    numActiveThreadbefore = numActiveThread - 1
    timeDelThread(feedbackMsg=telegramSendMsg(_("Bot is going offline"),
                                                reply_markup=None, 
                                                chat_id=CHATID, 
                                                token=MY_TELEGRAM_TOKEN
                                                ),
                    delayTimeSelect=10)
    botThreads.delPrinterMsg()
    time.sleep(5)
    while threading.active_count() != 1:
        time.sleep(1)
        numActiveThread = threading.active_count()
        if numActiveThread != numActiveThreadbefore:
            logger.info("Python programm was stopped. Active threads: %d / %s" % (threading.active_count(), threading.enumerate()))
            numActiveThreadbefore = numActiveThread
    sys.exit()



