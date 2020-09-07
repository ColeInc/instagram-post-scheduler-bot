# instagram-post-scheduler-bot
An instagram bot created to complete numerous tasks automatically for me on Instagram. Namely, automatically post scheduled media to Instagram at a specified time, and unfollow followers who don’t follow me back. Written in Python, utilizing the Selenium library.


## Specifications
* instagram_bot.py - main python class with all underlying functionality of this bot.
* bot_api.py - utilises the instagram_bot class from instagram_bot.py to create a public REST API using flask.
* Currently hosting this API on Amazon EC2 via an ubuntu 20.04 server.
* Eventually want to link up this backend to a frontend UI written in Angular or Flutter.



## Prerequisites if using python scripts:
- Need to download the corresponding version of chromedriver from [here].
  - instagram_bot.py currently looks for chromedriver.exe inside the location "C:/Windows/chromedriver.exe" so change to the corresponding location with where you install it (located in \_\_init\_\_).

- s

### External python libraries necessary before running:
* Selenium
* Flask
* Flask_restful
* 

## API Calls and Parameters:

### Login:
##### Description:
Enables the instagram bot to login to your instagram account to perform automated actions. Provide username and password as parameters.
##### URL:
* login - 'http://127.0.0.1:5000/login/'
##### Parameters:
- username: cole_mcconnell
- password: **********


### loginSecurityCode:
##### Description:
Given the user's account identifies a 'Suspicious Login Attempt', the user may provide the security code as a parameter here that has been sent to their personal email/phone, and the instagram bot can now use this to continue through this warning screen.
##### URL:
- loginSecurityCode - 'http://127.0.0.1:5000/loginsecuritycode/<securitycode>'


### getFollowers:
##### Description:
Gets the specified user's list of followers.
##### URL:
- getFollowers - 'http://127.0.0.1:5000/getfollowers/<user>'


### getFollowing:
##### Description:
Gets the list of specified user's current following.
##### URL:
- getFollowing - 'http://127.0.0.1:5000/getfollowing/<user>'


### getUnfollowers
##### Description:
Fetches provided user's followers list, following list, then calculates all users this user is currently following that is not following them back.
##### URL:
- getUnfollowers - 'http://127.0.0.1:5000/getunfollowers/<user>'


### unfollowUnfollowers:
##### Description:
1) Calculates unfollowers list
2) Unfollows specified number of users to unfollow from this list, for the user provided
##### URL:
- unfollowUnfollowers - 'http://127.0.0.1:5000/unfollowunfollowers/'
##### Parameters:
- username: cole_mcconnell
- number_to_unfollow: 10


### Quit:
##### Description:
Closes current instance of chromedriver.
##### Parameters:
- quit - 'http://127.0.0.1:5000/quit/'


[here]: <https://chromedriver.chromium.org/>