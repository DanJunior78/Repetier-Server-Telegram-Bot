# Repetier-Server-Telegram-Bot (Beta) - Python
Telegram Bot connecting your Repetier Server and your Telegram bot account.

It updates every 2 seconds your bot and you´ll have latest information about your prints and printer status.

This is still a beta version and i am testing it with several friends having up to 2 printers connected to a raspberry.

Application is tested on Windows 10 and Linux Mint 20

Following requierements:

Python >= 3.8 

# Library dependencies (installable via pip):

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
"MY_TELEGRAM_ID": | -->  Your telgram ID
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

# Additional information & support request

i would appreciate if someone would support me to add languages. I would be fully supportive with it, because i´ve a translation tool available. 
Please get in contact with me.

I am not a programming specialist, I know the code is looking maybe terrible for some persons which do program frequently.
The software itself is stable. I would be happy if someone with better programming skills would support me with dividing the main program to separated files (Bot, Connection to Server, etc.). I was not able to program it (Every program gets somehow better, but i am far away of declaring myself professional). 

I am also new to Github. It´s my first program which i made available. So please, i am open to learn. Let me know, if there is something to improve.

I have a job. I do this in my free time. So, please, i´ll answer usually <24h. I am located in europe, so don´t expect wonders, if i am sleeping, lol.

Disclaimer: It´s free, it´s in my eyes a missing feature for persons which used before Octoprint and miss the telegram bot option
