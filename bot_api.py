import json
from flask.json import jsonify
from flask import Flask, request
from instagram_bot import instagram_bot


bot = instagram_bot()
app = Flask(__name__)

def login(auth):
    try:
        username = auth["username"]
        password = auth["password"]
        if len(username) > 0 and len(password) > 0:
            bot.username = username
            bot.password = password
            resp = bot.login()
            if resp[0] == 0:
                return True, resp[1], 200
            elif resp[0] == 2:    # Suspicious Login Attempt identified. User will need to use loginSecurityCode API call to continue login
                return False, resp[1], 403
            else:
                return False, resp[1], 401
        else:
            return False, "Invalid Basic Authentication Details, Try again.", 401
    except:
        return False, "Error with your authentication, Try again.", 401


@app.route('/loginsecuritycode/<securitycode>')
def loginsecuritycode(securitycode):
    login_status = login(request.authorization)
    if login_status[0] == False and login_status[2] != 403:    # if login failed AND login error code IS NOT suspicious login attempt, return normal
        return login_status[1], login_status[2]
    elif login_status[2] == 403:    #if login failed AND login error code == suspicious login attempt, send security code
        resp = bot.enter_security_code(securitycode)
        if resp[0] == 0:
            return resp[1], 200
        else:
            return resp[1], 401
    else:
        return "Failed to send Security Code to bypass Suspicious Login Attempt.", 404


@app.route('/getfollowers/<user>')
def getFollowers(user):

    login_status = login(request.authorization)
    if login_status[0] == False:
        return login_status[1], login_status[2]

    followers_list = bot.get_followers_list_v2(user)
    bot.write_list_to_file(user, followers_list, "followers")
    return jsonify(followers_list), 200


@app.route('/getfollowing/<user>')
def getFollowing(user):
    
    login_status = login(request.authorization)
    if login_status[0] == False:
        return login_status[1], login_status[2]
    
    following_list = bot.get_following_list_v2(user)
    bot.write_list_to_file(user, following_list, "following")
    return jsonify(following_list), 200


@app.route('/getunfollowers/<user>') # Gets a fresh list of the unfollowers of the specified user.
def getUnfollowers(user):
    
    login_status = login(request.authorization)
    if login_status[0] == False:
        return login_status[1], login_status[2]
    
    followers = bot.get_followers_list_v2(user)
    bot.write_list_to_file(user, followers, "followers")

    following = bot.get_following_list_v2(user)
    bot.write_list_to_file(user, following, "following")

    unfollowers = bot.get_unfollowers_list(followers, following)
    bot.write_list_to_file(user, unfollowers, "unfollowers")

    # think i'll need to create separate functions to check if user has done any of the above/below... already done in get_latest_followers_list_from_file, 
    # inefficient to create separate function that would loop the json twice

    # need to implement some kind of date range that previous lists fetched are. E.g. anything older than 3 days wouldn't be valid bc too old/out of date

    # if you haven't done a get_unfollowers_list(followers, following) request yet for that user, do one,
    # else bot.get_latest_unfollowers_list_from_file(username)

    return jsonify(unfollowers), 200


@app.route('/unfollowunfollowers/<user>') # Gets a fresh list of the unfollowers of the specified user.
def unfollowUnfollowers(user):
    
    login_status = login(request.authorization)
    if login_status[0] == False:
        return login_status[1], login_status[2]

    try:
        number_to_unfollow = int(request.args.get('numbertounfollow'))
    except:
        return "Invalid number to unfollow inputted. Check it's a valid number?", 401
    
    unfollowers = bot.get_latest_unfollowers_list_from_file(user)
    if unfollowers == None:
        followers = bot.get_latest_followers_list_from_file(user) # checks if there's a previous list of followers fetched for this user
        if followers == None:
            followers = bot.get_followers_list_v2(user) # if there isn't a previous list, goes off and fetches a new list, and updates followers.json accordingly
            bot.write_list_to_file(user, followers, "followers")

        following = bot.get_latest_following_list_from_file(user) 
        if following == None:
            following = bot.get_following_list_v2(user)
            bot.write_list_to_file(user, following, "following")

        unfollowers = bot.get_unfollowers_list(followers, following)
        bot.write_list_to_file(user, unfollowers, "unfollowers")
    
    print(unfollowers) # delete
    
    bot.unfollow_unfollowers(unfollowers, number_to_unfollow)
    return "Successfully unfollowed " + str(number_to_unfollow) + " users!", 200


@app.route('/likeandcommentonhashtag/')
def likeAndCommentOnHashtag():
    
    login_status = login(request.authorization)
    if login_status[0] == False:
        return login_status[1], login_status[2]
    
    hashtag = request.args.get('hashtag')
    number_of_likes = int(request.args.get('number_of_likes'))
    number_of_comments = int(request.args.get('number_of_comments'))
    resp = bot.like_and_comment_x_posts_of_hashtag(hashtag, number_of_likes, number_of_comments)
    if resp[0] == 0:
        return resp[1], 200
    else:
        return resp[1], 401


@app.route('/likerandomhashtag/')
def likeAndCommentRandomHashtag():
    
    login_status = login(request.authorization)
    if login_status[0] == False:
        return login_status[1], login_status[2]
    
    number_of_likes = int(request.args.get('number_of_likes'))
    number_of_comments = int(request.args.get('number_of_comments'))
    resp = bot.like_and_comment_on_random_hashtag(number_of_likes, number_of_comments)
    if resp[0] == 0:
        return resp[1], 200
    else:
        return resp[1], 401


@app.route('/followusersunderhashtag/')
def followUsersUnderHashtag():
    
    login_status = login(request.authorization)
    if login_status[0] == False:
        return login_status[1], login_status[2]
    
    hashtag = request.args.get('hashtag')
    number_of_users = int(request.args.get('number_of_users'))

    # perhaps offload all these calls to its own function because ideally bot_api should just be high level calling, no logic
    bot.connect_to_mysql()
    fetch_id_resp = bot.fetch_id_from_username()
    new_following_list_resp = bot.follow_users_under_hashtag(fetch_id_resp[1], hashtag, number_of_users)

    if new_following_list_resp[0] == 0:
        print(new_following_list_resp[1])
        print("new_following_list_resp[2] -->", new_following_list_resp[2]) # DELETE
        resp = bot.insert_into_following_table(new_following_list_resp[2])
        bot.close_database_connection()
        if resp[0] == 0:
            return resp[1], 200
        else:
            return resp[1], 401
    else:
        return new_following_list_resp[1], 401


@app.route('/unfollowxusersolderthanxdays/')
def unfollowXUsersOlderThanXDays():
    
    login_status = login(request.authorization)
    if login_status[0] == False:
        return login_status[1], login_status[2]
    
    number_of_days = int(request.args.get('number_of_days'))
    number_of_users = int(request.args.get('number_of_users'))

    followers_list = bot.get_followers_list_v2(bot.username) # mandatory get followers list before we begin (to see if users are following us yet)
    
    if bot.connect_to_mysql() != True:
        return "Failed to connect to MySQL Database", 401
    
    fetch_id_resp = bot.fetch_id_from_username()
    if fetch_id_resp[0] != 0:
        return fetch_id_resp[1], 401

    following_list_resp = bot.get_users_older_than_x_days(fetch_id_resp[1], number_of_days)
    if following_list_resp[0] != 0:
        return following_list_resp[1], 401
    
    neverfollowers_list = bot.get_neverfollowers_list(followers_list, following_list_resp[1])
    bot.unfollow_unfollowers(neverfollowers_list, number_of_users)

    final_resp = bot.remove_unfollowed_neverfollowers_from_table()
    if final_resp[0] != 0:
        return fetch_id_resp[1], 401

    return "Successfully unfollowed " + str(len(following_list_resp[1])) + " users that didn't follow you back in the last " + str(number_of_days) + " day(s).", 200


@app.route('/start/')
def start():
    # bot.quit()
    bot = instagram_bot()
    return "Successfully started instagram_bot."


@app.route('/quit/')
def quit():
    bot.quit()
    return "Successfully closed instagram_bot."

if __name__ == '__main__':
    app.run(debug=True)                     # For running on windows when testing
    # app.run()                             # When running on ubuntu server via gunicorn + nginx
    # app.run(host='0.0.0.0', port='80')    # When running on ubuntu server by 'python bot_api.py' only
    # app.run(host='0.0.0.0')
