# Repetier-Server-Telegram-Bot - Python
## Version: 1.0.12 - 29.12.2020
Telegram Bot connecting your Repetier Server and your Telegram bot account.

It updates frequently your bot and you´ll have latest information about your prints and printer status.

Application is tested on Windows 10, Windows Server, Raspberry Pi, Proxmox VM and Linux Mint 20 (thanks to all supporting gents from the news group)

Following requierements:

Python >= 3.8 

Please visit the wiki for helpful information related to this program: [Main Wiki Page](https://github.com/DanJunior78/Repetier-Server-Telegram-Bot/wiki)

[Get support on Telegram :face_with_head_bandage:](https://t.me/Repetier_S_Telegram_Bot_Support)

[Get news on Telegram :newspaper:](https://t.me/Repetier_Server_Telegram)

_If you want to support me with a fresh coffee and if you think it´s worthing what i'm doing, donate something, to get a fresh coffee_
[Push here :love_letter:](https://paypal.me/DanielGlock78)

# Images/Pictures

### New in V1.0.2:

![Main View](/00_Pictures/main_view_v1_0.JPG)
![Printer Detail](/00_Pictures/main_detail_view_v1_0.JPG)
![Printing view collapsed](/00_Pictures/printing_v1_0.JPG)
![Heat up at print start](/00_Pictures/heat_up_v1_0.JPG)
![Heat up at print start 2](/00_Pictures/heat_up2_v1_0.JPG)
![Cool down at print finish and message](/00_Pictures/cool_down_messages_V1_0.JPG)
![New settings in V1.0.2](/00_Pictures/settings_v1_0.JPG)
![New debug support files in V1.0.2](/00_Pictures/Debug_Support.JPG)

impressions from Beta users (thanks again to Seb):

![User Impression V1.0.2](/00_Pictures/main_view_v1_0_by_Seb.JPG)
![User Impression 2 V1.0.2](/00_Pictures/main_view_v1_0_by_Seb2.JPG)


New in V05 (content still valid in V1.0.2):

![External Commands](/00_Pictures/ExtCommands.JPG)
![Webcam](/00_Pictures/Webcam_Items.JPG)

New in V04 (content still valid in V1.0.2):

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

please check correct installation depending on your Python installation with: python3 -m pip list / python3.9 -m pip list

and try if not properly installed via e.g. for Python 3.9: python3.9 -m pip install xxxxxxxxxx

UPDATE ALL PIP PACKAGES. CHECK WITH: python3.9 -m pip list --outdated -> Update all what is possible. Some are not possible, leaf them.

12/17/20: please don´t update single libraries via pip. known issues with: pip install numpy==1.19.4 -> program would not start as it is a problem on latest Windows 10 64bit installations.

# How to update from an old version:

Please only stop your actual running bot and exchange all files. From V1.0.2 and greater all updates will work without exchange of the .json file.
From > V1.0.2 please use in linux: 
### wget https://raw.githubusercontent.com/DanJunior78/Repetier-Server-Telegram-Bot/main/RepetierBot.py

# How to get started:

Configuration File (JSON): Repetier-Server_Telegram_Bot_Vx.json

Requiered data:| What to fill in:
---------------|-----------------
"CFG_VERSION": "Vxxx.xxx.xx"| --> **do not change!!!**
"LANGUAGE": "en"| --> Possible to change to your language, otherwise it will be used the system setting or if not availble, it will keep program in english.
"MY_REPETIER_SERVER_API_KEY": ""| --> Your Repetier-Server API Key
"RepetierServerIP": ""| --> Fill in your Repetier-Server IP adress, e.g. "192.168.100.44"
"RepetierServerPort": "3344"| --> usually Repetier-Server port is: 3344 
"MY_TELEGRAM_ID": | -->  Your telgram ID -> Is a integer number. You can check the number via the bot: Telegram Bot Raw - It feedbacks your details
"MY_TELEGRAM_TOKEN": ""| --> Your botfather token 
"printers": [] | --> **Do not change!!!**
"gui": [] | --> **Do not change!!!**

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
