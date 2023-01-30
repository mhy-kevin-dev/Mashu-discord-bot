# Discord bot prototype

This bot can do: 
- NLP tasks
    - Tanslate
    - Detect languages
    - Summarization
    - Talk to AI
- Other tasks
    - Search image sources
    - Get youtube thumbnails


Requirements 
============================
- Python 3.8 or higher is required
- check requirements.txt
    - discord.py (pip install discord.py)
    - websockets
    - requests
    - googletrans==3.1.0a0
    - saucenao-api 
    - openai

It is recommended to use Conda to install the above packages.

Installation
============================
```sh
pip install -r requirements.txt
```

Quick Start
============================
Make sure you have these accounts, and get their api keys:
- openai api (https://openai.com/api/)
- saucenao api (https://saucenao.com/user.php?page=search-api)
- discord bot (https://discord.com/developers/applications)

Then, start the bot:
```sh
python discordbot.py
```


Funcions
============================
- bot prefix: !
- need to reply the source message:
    - !trans 
    - !detect 
    - !tldr
- !talk  SOME_SENTENCES
- !yt  URL
- !search  IMAGE_URL
- !dice


TODO
============================
- clean code
- documentations
