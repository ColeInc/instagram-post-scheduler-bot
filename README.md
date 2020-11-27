# Cole's Instagram Bot
An instagram bot created to complete numerous tasks automatically for me on Instagram. Namely, automatically running processes to encourage page growth, and unfollow followers who don’t follow me back. Written in Python, utilizing the Selenium library.


## Specifications
* instagram_bot.py - main python class with all underlying functionality of this bot.
* bot_api.py - utilises the instagram_bot class from instagram_bot.py to create a public REST API using flask.
* In order to get the full capabilities out of this instagram bot, a form of persistant storage is necessary. The way I've configured it on my machine is to have a MySQL database running side by side with this API to store long term data which some of the functions below depend on.
* In terms of hosting the actual API, I've created a separate repository which stores a full docker container setup that can host and provide all functionalities needed for it. The docker container consists of an Nginx server, which works to serve the Flask application. Then a Selenium grid with a single Firefox node to perform all webscraping of the underlying instagram_bot.py.
* Docker container repo here - [docker_instagram_bot](https://github.com/ColeInc/docker_instagram_bot)
* Eventually want to link up this bot to a frontend UI written in Angular.


### External python libraries necessary before running:
* pip install selenium
* pip install flask
* pip install uwsgi
* pip install emojis
* pip install mysql-connector


## Authentication:
With every API call you pass, you'll need to send the corresponding instagram account credentials as basic authentication parameters.


## API Calls and Parameters:

### loginSecurityCode:
##### Description:
Given the user's account identifies a 'Suspicious Login Attempt', the user may provide the security code as a parameter here that has been sent to their personal email/phone, and the instagram bot can now use this to continue through this warning screen.
##### URL:
- loginSecurityCode - 'http://127.0.0.1:5000/loginsecuritycode/**securitycode**'
##### Parameters:
- securitycode: 871293

### getFollowers:
##### Description:
Gets the specified user's list of followers.
##### URL:
- getFollowers - 'http://127.0.0.1:5000/getfollowers/**user**'
##### Parameters:
- user: cole

### getFollowing:
##### Description:
Gets the list of specified user's current following.
##### URL:
- getFollowing - 'http://127.0.0.1:5000/getfollowing/**user**'
##### Parameters:
- user: cole

### getUnfollowers
##### Description:
Fetches provided user's followers list, following list, then calculates all users this user is currently following that is not following them back.
##### URL:
- getUnfollowers - 'http://127.0.0.1:5000/getunfollowers/**user**'
##### Parameters:
- user: cole

### unfollowUnfollowers:
##### Description:
1) Calculates unfollowers list
2) Unfollows specified number of users to unfollow from this list, for the user provided
##### URL:
- unfollowUnfollowers - 'http://127.0.0.1:5000/unfollowunfollowers/**user**?numbertounfollow=10'
##### Parameters:
- user: cole_mcconnell
- number_to_unfollow: 10


### likeAndCommentOnHashtag:
##### Description:
You specify the hashtag you want to like and comment on, the number of likes, and number of comments you'd like to make, and the bot will go to the corresponding page for this hashtag, jump to the recent section, and semi-randomly select the corresponding number of posts to like/comment.
##### URL:
- likeAndCommentOnHashtag - 'http://127.0.0.1:5000/likeandcommentonhashtag?hashtag=bakedbeans&number_of_likes=30&number_of_comments=25'
##### Parameters:
- hashtag: bakedbeans
- number_of_likes: 30
- number_of_comments: 40


### likeRandomHashtag:
##### Description:
I guess this should actually be called likeAndCommentOnRandomHashtag, but that doesn't roll of the tongue quite as nicely. With this API call it will randomly fetch a hashtag from a pre-defined list of hashtags you can define inside the resources/hashtags.json file. You simply specify the number of likes, and number of comments you'd like to make, and the bot will go to the corresponding page for this hashtag, jump to the recent section, and semi-randomly select the corresponding number of posts to like/comment.
##### URL:
- likerandomhashtag - 'http://127.0.0.1:5000//likerandomhashtag?number_of_likes=30&number_of_comments=20'
##### Parameters:
- number_of_likes: 30
- number_of_comments: 30


### followUsersUnderHashtag:
##### Description:
The idea of this function is to find like-minded or similar style pages to yours, in the hopes they follow you back.

You specify the hashtag you'd like to follow people under, and the number of people you'd like to follow, and the bot will go to the corresponding page for this hashtag, jump to the recent section, iterate through these posts, and semi-randomly follow the users who've posted under this hashtag. This function also has the added capability (if configured) to store the corresponding users you've followed into a MySQL database table, along with the date you followed them.

You'll find this function goes hand in hand quite nicely with unfollowXUsersOlderThanXDays.
##### URL:
- followusersunderhashtag - 'http://127.0.0.1:5000/followusersunderhashtag?hashtag=cats&number_of_users=30'
##### Parameters:
- hashtag: cats
- number_of_users: 30


### unfollowXUsersOlderThanXDays:
##### Description:
Unfortunately this function only works if you've configured a MySQL database to store persistant data collected by the followUsersUnderHashtag function above. The idea is that you collect all data of users you've previously followed with the followUsersUnderHashtag function, and then using this function, you define the number of days ago to check, and it will go away and check of all users you've followed previously, which ones have not followed you back in that corresponding time period. It will then continue on and graciously unfollow the corresponding number of users from this list you specify in the number_of_users parameter. 
##### URL:
- unfollowxusersolderthanxdays - 'http://127.0.0.1:5000/unfollowxusersolderthanxdays?number_of_days=1&number_of_users=100'
##### Parameters:
- number_of_days: 7
- number_of_users: 100


### Start:
##### Description:
Starts a fresh webdriver instance.
##### Parameters:
- start - 'http://127.0.0.1:5000/start/'

### Quit:
##### Description:
Closes current webdriver instance.
##### Parameters:
- quit - 'http://127.0.0.1:5000/quit/'