import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from instagram_bot import instagram_bot

bot = instagram_bot()
app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()

parser.add_argument('username')
parser.add_argument('password')
# parser.add_argument('username', required=True)
# parser.add_argument('password', required=True)

class login(Resource):
    def get(self):
        print("1) ", request.authorization["username"]) 
        print("2) ", request.authorization["password"])

        args = parser.parse_args()
        bot.username = args['username']
        bot.password = args['password']
        resp = bot.login()
        if resp[0] == 0:
            return resp[1], 200
        elif resp[0] == 2: # Suspicious Login Attempt identified. User will need to use loginSecurityCode API call to continue login
            return resp[1], 403
        else:
            return resp[1], 401


class loginSecurityCode(Resource):
    def get(self, securitycode):
        resp = bot.enter_security_code(securitycode)
        if resp[0] == 0:
            return resp[1], 200
        else:
            return resp[1], 401


class getFollowers(Resource):
    def get(self, user):
        followers_list = bot.get_followers_list_v2(user)
        bot.write_list_to_file(user, followers_list, "followers")
        return followers_list, 200


class getFollowing(Resource):
    def get(self, user):
        following_list = bot.get_following_list_v2(user)
        bot.write_list_to_file(user, following_list, "following")
        return following_list, 200


class getUnfollowers(Resource): # Gets a fresh list of the unfollowers of the specified user.
    def get(self, user):

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

        return unfollowers, 200


parser.add_argument('numbertounfollow')

class unfollowUnfollowers(Resource): # Unfollows from the unfollowers list the amount of followers specified in the API query parameter for the current logged in user. 
    def get(self, user):
        args = parser.parse_args()
        try:
            number_to_unfollow = int(args['numbertounfollow'])
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


parser.add_argument('hashtag')
parser.add_argument('number_of_likes')
parser.add_argument('number_of_comments')

class likeAndCommentOnHashtag(Resource):
    def get(self):
        args = parser.parse_args()
        hashtag = args['hashtag']
        number_of_likes = int(args['number_of_likes'])
        number_of_comments = int(args['number_of_comments'])
        resp = bot.like_and_comment_x_posts_of_hashtag(hashtag, number_of_likes, number_of_comments)
        if resp[0] == 0:
            return resp[1], 200
        else:
            return resp[1], 401


class likeAndCommentRandomHashtag(Resource):
    def get(self):
        args = parser.parse_args()
        number_of_likes = int(args['number_of_likes'])
        number_of_comments = int(args['number_of_comments'])
        resp = bot.like_and_comment_on_random_hashtag(number_of_likes, number_of_comments)
        if resp[0] == 0:
            return resp[1], 200
        else:
            return resp[1], 401


parser.add_argument('number_of_users')

class followUsersUnderHashtag(Resource):
    def get(self):
        args = parser.parse_args()
        hashtag = args['hashtag']
        number_of_users = int(args['number_of_users'])

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


parser.add_argument('number_of_days')

class unfollowXUsersOlderThanXDays(Resource):
    def get(self):
        args = parser.parse_args()
        number_of_days = int(args['number_of_days'])
        number_of_users = int(args['number_of_users'])

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


class start(Resource):
    def get(self):
        # bot.quit()
        bot = instagram_bot()
        return "Successfully started instagram_bot."


class quit(Resource):
    def get(self):
        bot.quit()
        return "Successfully closed instagram_bot."


api.add_resource(login, '/login/')
api.add_resource(loginSecurityCode, '/loginsecuritycode/<securitycode>')
api.add_resource(getFollowers, '/getfollowers/<user>')
api.add_resource(getFollowing, '/getfollowing/<user>')
api.add_resource(getUnfollowers, '/getunfollowers/<user>')
api.add_resource(unfollowUnfollowers, '/unfollowunfollowers/<user>')
api.add_resource(likeAndCommentOnHashtag, '/likeandcommentonhashtag/')
api.add_resource(likeAndCommentRandomHashtag, '/likerandomhashtag/')
api.add_resource(followUsersUnderHashtag, '/followusersunderhashtag/')
api.add_resource(unfollowXUsersOlderThanXDays, '/unfollowxusersolderthanxdays/')
api.add_resource(start, '/start/')
api.add_resource(quit, '/quit/')

if __name__ == '__main__':
    app.run(debug=True)                     # For running on windows when testing
    # app.run()
    # app.run(host='0.0.0.0', port='80')    # When running on ubuntu server
    # app.run(host='0.0.0.0')
