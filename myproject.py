from flask import Flask
from flask_restful import Resource, Api
from instagram_bot import instagram_bot

app = Flask(__name__)
api = Api(app)
bot = instagram_bot()
    
# class login(Resource, username, password)
#     pass

class firstTest(Resource):
    def get(self, user):
        return 'Congrats kid, it works !', 200
        
class getFollowers(Resource):
    def get(self, user):
        follower_list = bot.get_followers_list_v2(user)
        bot.write_list_to_file(user, follower_list, "followers")
        return '', 200


class getFollowing(Resource):
    def get(self, user):
        following_list = bot.get_following_list_v2(user)
        bot.write_list_to_file(user, following_list, "following")
        return '', 200

class getUnfollowers(Resource):
    def get(self, user):

        # if you haven't done a getfollowing + getfollowers request for user, then do them first.

        # think i'll need to create separate functions to check if user has done any of the above/below

        # if you haven't done a get_unfollowers_list(followers, following) request yet for that user, do one,
        # else bot.get_latest_unfollowers_list_from_file(username)

        return '', 200


class unfollowUnfollowers(Resource):
    def get(self, user):
        pass
        # think i'll need to create separate functions to check if user has done any of the above/below

        # if you haven't done a get_unfollowers_list(followers, following) request yet for that user, do one,
        # else bot.get_latest_unfollowers_list_from_file(username)



# abort(404, message="Todo {} doesn't exist".format(todo_id))

# api.add_resource(login, '/login/')
api.add_resource(firstTest, '/firsttest')
api.add_resource(getFollowers, '/getfollowers/<user>')
api.add_resource(getFollowing, '/getfollowing/<user>')
api.add_resource(getUnfollowers, '/getunfollowers/<user>')
api.add_resource(unfollowUnfollowers, '/unfollowunfollowers/<user>')

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0')
    
    # bot.close_driver()

#-----------------------------
# DO DO LIST:
#-----------------------------

"""
- Remember to remove debug mode from main function when deploying to prod

- Look into auth0 to see how I can securely let people login to their IG without my dodgey eyes seeing 
  their password
  Actually just look into normal ways of authenticating in APIs in general.

- Maybe look at separating out the login function in my main function, then make the separate login api 
  call here, so that it doesn't initiate with logging in every time I run this by default.

- Stress test invalid entries + invalid request types (using post to a get, etc.)

"""