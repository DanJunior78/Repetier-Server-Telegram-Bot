# Repetier-Server-Telegram-Bot (Beta) - Python
Telegram Bot connecting your Repetier Server and your Telegram bot account.

It updates every 2 seconds your bot and you´ll have latest information about your prints and printer status.

This is still a beta version and i am testing it with several friends having up to 2 printers connected to a raspberry.

Application is tested on Windows 10 and Linux Mint 20

Following requierements:

Python >= 3.8 

Get news and support at: https://t.me/Repetier_Server_Telegram

_If you want to support me with a fresh coffee and if you think it´s worthing what i'm doing, donate something, to get a fresh coffee_
[Push here :love_letter:](https://paypal.me/DanielGlock78)

# !For updating your existing installation, please refer Version History section below!
# Images/Pictures

![Main View](/00_Pictures/Main_View.JPG)
![Printer Detail](/00_Pictures/Printer_Detail_View.JPG)
![External Commands](/00_Pictures/ExtCommands.JPG)
![Webcam](/00_Pictures/Webcam_Items.JPG)

New in V04:

![Quick Command and Settings](/00_Pictures/QuickCommandsAndSettings_V04.JPG)
![Quick Command and Settings](/00_Pictures/QuickCommands_V04.JPG)
![Settings](/00_Pictures/Settings_V04.JPG)
![Settings_Temperature](/00_Pictures/Settings3_V04.JPG)
![Settings_ExtCommand](/00_Pictures/Settings2_V04.JPG)
![Notifications](/00_Pictures/Notifications_V04.JPG)

# Library dependencies (install via pip):

- pip install arrow
- pip install websocket_client
- pip install requests
- pip install imageio
- pip install pygifsicle
- pip install opencv-python
- pip install python-telegram-bot

# How to get started:

Configuration File (JSON): Repetier-Server_Telegram_Bot_Vx.json

Requiered data:| What to fill in:
---------------|-----------------
"CFG_VERSION": "V03"| --> **do not change!!!**
"LANGUAGE": "en"| --> Possible to change to your language, otherwise it will be used the system setting or if not availble, it will keep program in english.
"MY_REPETIER_SERVER_API_KEY": ""| --> Your Repetier-Server API Key
"RepetierServerIP": ""| --> Fill in your Repetier-Server IP adress, e.g. "192.168.100.44"
"RepetierServerIP2": ""| --> For future use, not required 
"RepetierServerPort": "3344"| --> usually Repetier-Server port is: 3344 
"MY_TELEGRAM_ID": | -->  Your telgram ID -> Is a integer number. You can check the number via the bot: Telegram Bot Raw - It feedbacks your details
"MY_TELEGRAM_TOKEN": ""| --> Your botfather token 
"LOGFILENAME": ""| --> usually all logs go to ./log folder
"LOGFILENAMEWS": ""| --> usually all logs go to ./log folder 
"PNGFILEFOLDER": ""| --> usually all pics/videos go to ./pic folder
"GIFFILEFOLDER": ""| --> usually all pics/videos go to ./pic folder 
"VIDFILEFOLDER": ""| --> usually all pics/videos go to ./pic folder 
"data": [] | --> **Do not change!!!**

# Available Languages:

German, English, Spanish
Please be aware of differences in the platform (Windows and Linux).

You can reduce the program size by deleting languages in the folder ./locale (But i would not recommend it, there are still only 3 languages inside...a few kB of your HD)

# Version History:
Use always the new Python file and the latest JSON configuration file. Please download always locale Folder (language files) too. 

V03: First Release

V04: Bugfixes, New functions for showing messages, quick commands, command to ExtCommand after printing and cooling down the extruder, reduced messages
  Please use new Configuration JSON or if you know how to modifiy your existing. Check for differences.
  
V05.000: Bugfixes, implemented FR001: Send picture after print finished, removed telegram message - repetier server message due to exceeding telegram bot limits, which will be fixed in V1.0.0, which will be the next version of my software.

# Additional information & support request

i would appreciate if someone would support me to add languages. I would be fully supportive with it, because i´ve a translation tool available. 
Please get in contact with me.

I am not a programming specialist, I know the code is looking maybe terrible for some persons which do program frequently.
The software itself is stable. I would be happy if someone with better programming skills would support me with dividing the main program to separated files (Bot, Connection to Server, etc.). I was not able to program it (Every program gets somehow better, but i am far away of declaring myself professional). 

I am also new to Github. It´s my first program which i made available. So please, i am open to learn. Let me know, if there is something to improve.

I have a job. I do this in my free time. So, please, i´ll answer usually <24h. I am located in europe, so don´t expect wonders, if i am sleeping, lol.

Disclaimer: It´s free, it´s in my eyes a missing feature for persons which used before Octoprint and miss the telegram bot option
