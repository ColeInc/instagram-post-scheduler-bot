# instagram-post-scheduler-bot
This bot is created to complete numerous tasks automatically for me on Instagram. Namely, automatically post scheduled media to Instagram at a specified time, and unfollow followers who don’t follow me back. Written in Python, utilizing the Selenium library.

## Specifications
instagram_bot.py - main python class with all underlying functionality of this bot.
bot_api.py - utilises the instagram_bot class from instagram_bot.py to create a public REST API using flask. 
Currently hosting this API on Amazon EC2 via an ubuntu 20.04 server.
Eventually want to link up this backend to a frontend UI written in Angular or Flutter.
