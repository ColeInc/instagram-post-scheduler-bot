#delete:
from explicit import waiter, XPATH

import os
import re
import json
import random
import datetime
import itertools
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class instagram_bot:

    def __init__(self):
        self.username = ''
        self.password = ''
        self.driver = webdriver.Chrome('C:/Windows/chromedriver')
        self.fetch_credentials()
        self.login()


    def fetch_credentials(self):
        with open('../credentials.json', 'r') as data:
            credentials = json.load(data)
        for i in credentials:
            self.username = i["username"]
            self.password = i["password"]


    def login(self):
        self.driver.get('https://www.instagram.com/accounts/login')
        sleep(1)
        self.driver.find_element_by_name('username').send_keys(self.username)
        self.driver.find_element_by_name('password').send_keys(self.password, Keys.RETURN)
        sleep(self.rng())


    def rng(self):
        num = random.randint(3200,8200) / 1000
        return num


    def go_to_user(self, username):
        self.driver.get('https://www.instagram.com/{}'.format(username))


    def follow_user(self, username):
        self.go_to_user(username)
        sleep(self.rng())
        follow_button = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button')
        follow_button.click()
        sleep(self.rng())


    def unfollow_user(self, username):
        self.go_to_user(username)
        sleep(self.rng())
        try:
            print("Unfollowing {}...").format(username)
            following_button = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[2]/span/span[1]/button').click()
            sleep(2)
            following_button = self.driver.find_element_by_xpath("//button[contains(text(), 'Unfollow')]").click()
            # sleep(self.rng())
            print("Unfollowed {}.").format(username)
        except NoSuchElementException:
            print("You are not following that user!")


    def go_to_followers_list(self, username):
        self.go_to_user(username)
        sleep(self.rng())
        followers_list = self.driver.find_element_by_xpath("//a[contains(@href, '/" + username.lower() + "/followers/')]")
        followers_list.click()
        sleep(self.rng())


    def go_to_following_list(self, username):
        self.go_to_user(username)
        sleep(self.rng())
        following_list = self.driver.find_element_by_xpath("//a[contains(@href, '/" + username.lower() + "/following/')]")
        following_list.click()
        sleep(self.rng())


    def random_scroll_function(self, num_of_scrolls): #remove, too niche having first line like this (just for followers modal)
        followDivBox = self.driver.find_element_by_xpath("//div[@class='isgrP']")
        scroll = 0
        while scroll < num_of_scrolls:
            #executes javascript script to scroll page... bit choppy... might want to find better scrolling script
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', followDivBox)
            scroll += 1
            sleep(self.rng())


    def get_followers_list(self, username, following=False):
        
        """
        This original get_followers_list function is much less efficient than the v2 versions, essentially what this function does is goes to the
        modal showing the list of followers/following on a specified user's instagram page, then via selenium + executing javascript scripts I
        basically just keep loading down the list, fetching the 12 users that load, scroll to the end of the list, wait till next 12 load, collect
        them, and so on. Very inefficient, and have noticed it gets exponentially slower the larger amount of followers you iterate. 
        """

        if following:
            following_list = []
            num_following = self.get_num_following(username)
            self.driver.get("https://www.instagram.com/" + username.lower() + "/")
            self.driver.find_element_by_xpath("//a[contains(@href, '/" + username.lower() + "/following/')]").click()
        else:
            followers_list = []
            num_followers = self.get_num_followers(username)
            self.driver.get("https://www.instagram.com/" + username.lower() + "/")
            self.driver.find_element_by_xpath("//a[contains(@href, '/" + username.lower() + "/followers/')]").click()

        sleep(2)

        try:
            follower_css = "ul div li:nth-child({}) a.notranslate"
            for group in itertools.count(start=1, step=12):
                for follower_index in range(group, group + 12):
                    nth_child = "ul div li:nth-child(" + str(follower_index) + ") a.notranslate"
                    follower = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, nth_child))).text
                    print(follower_index, ") ", follower, sep='')
                    following_list.append(follower) if following else followers_list.append(follower)

                    # This section isn't needed for large following lists, but for small followings like 200 ish, found that sometimes it would
                    # only load 4 users in the next chunk instead of 12, breaking everything. This section just does an extra little scroll there
                    # to prevent this from happening. Could perhaps make a pre-check to see if total followers is less than a certain amount.
                    followDivBox = self.driver.find_element_by_xpath("//div[@class='isgrP']")
                    scroll = 0
                    while scroll < 2:
                        self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', followDivBox)
                        scroll += 1

                last_follower = self.driver.find_element_by_css_selector(nth_child)
                self.driver.execute_script("arguments[0].scrollIntoView();", last_follower)

            if following:
                print('Final following_list: ', following_list, "\nNum following counted: ", len(following_list), sep='')
                print("Successfully fetched following list!")
                return following_list
            else:
                print('Final followers_list: ', followers_list, "\nNum followers counted: ", len(followers_list), sep='')
                print("Successfully fetched list of followers!")
                return followers_list

        except NoSuchElementException:
            print('No Such Element Exception! - Cole')
        except TimeoutException:
            # print('TimeoutException!')
            if following:
                print("Num following counted: ", len(following_list), sep='')
                print("Successfully fetched following list!")
                return following_list
            else:
                print("Num followers counted: ", len(followers_list), sep='')
                print("Successfully fetched list of followers!")
                return followers_list
        except Exception as e:
            print('Error while iterating followers/following list:\n', e, sep='')


    def get_following_list(self, username):
        return self.get_followers_list(username, True)

    
    def get_followers_list_v2(self, username):
    
        """
        v2 of this function utlizes an unofficial instagram API call to fetch the list of followers/following. I've been told it theoretically isn't
        illegal so be careful where you use this lads.
        Only difference between followers and following v2 functions is the hash used inside the URL. Different hash for followers/following.
        """

        real_amount = self.get_num_followers(username)

        try:
            user_id = self.browser.execute_script("return window.__additionalData[Object.keys(window.__additionalData)[0]].data.graphql.user.id")
        except:
            user_id = self.browser.execute_script("return window._sharedData." "entry_data.ProfilePage[0]." "graphql.user.id")

        self.browser.get("https://www.instagram.com/static/bundles/es6/Consumer.js/1f67555edbd3.js")
        page_source = self.browser.page_source
        hash = re.findall('[a-z0-9]{32}(?=",n=")', page_source) # fetch 32 char followers hash
        
        if hash:
            query_hash = hash[0] # http://prntscr.com/trrreu            
        elif hash == False or hash[0] is None:
            print("Unable to calculate query hash for API call.")

        graphql_query_URL = "view-source:https://www.instagram.com/graphql/query/?query_hash={}".format(query_hash)

        variables = {
            "id": str(user_id),
            "include_reel": "true",
            "fetch_mutual": "true",
            "first": 50,
        }
        url = "{}&variables={}".format(graphql_query_URL, str(json.dumps(variables)))

        self.driver.get(url)
        sleep(self.rng())

        pre = self.browser.find_element_by_xpath("//td[@class='line-content']")
        data = json.loads(pre.text)
        followers_page = data["data"]["user"]["edge_followed_by"]["edges"]
        followers_list = []
        i = 1

        for follower in followers_page:
            print("{}) {}".format(i, follower["node"]["username"]))
            followers_list.append(follower["node"]["username"])
            i += 1

        has_next_page = data["data"]["user"]["edge_followed_by"]["page_info"]["has_next_page"]

        while has_next_page:
            sleep(self.rng())
            end_cursor = data["data"]["user"]["edge_followed_by"]["page_info"]["end_cursor"]

            variables = {
                "id": str(user_id),
                "include_reel": "true",
                "fetch_mutual": "true",
                "first": 50,
                "after": end_cursor,
            }
            url = "{}&variables={}".format(graphql_query_URL, str(json.dumps(variables)))

            self.browser.get(url)
            sleep(self.rng())

            pre = self.browser.find_element_by_xpath("//td[@class='line-content']")
            data = json.loads(pre.text)

            followers_page = data["data"]["user"]["edge_followed_by"]["edges"]
            for follower in followers_page:
                print("{}) {}".format(i, follower["node"]["username"]))
                followers_list.append(follower["node"]["username"])
                i += 1

            has_next_page = data["data"]["user"]["edge_followed_by"]["page_info"]["has_next_page"]

        print('Final followers_list: ', followers_list, "\nNum followers counted: ", len(followers_list), sep='')
        print("Successfully fetched list of followers!")
        return followers_list


    def get_following_list_v2(self, username):

        """
        v2 of this function utlizes an unofficial instagram API call to fetch the list of followers/following. I've been told it theoretically isn't
        illegal so be careful where you use this lads.
        Only difference between followers and following v2 functions is the hash used inside the URL. Different hash for followers/following.
        """

        real_amount = self.get_num_followers(username)

        try:
            user_id = self.driver.execute_script("return window.__additionalData[Object.keys(window.__additionalData)[0]].data.graphql.user.id")
        except:
            user_id = self.driver.execute_script("return window._sharedData." "entry_data.ProfilePage[0]." "graphql.user.id")

        self.driver.get("https://www.instagram.com/static/bundles/es6/Consumer.js/1f67555edbd3.js")
        page_source = self.driver.page_source
        hash = re.findall('[a-z0-9]{32}(?=",u=1)', page_source) # following hash regex
        
        if hash:
            query_hash = hash[0]
        elif hash == False or hash[0] is None:
            print("Unable to calculate query hash for API call.")

        graphql_query_URL = "view-source:https://www.instagram.com/graphql/query/?query_hash={}".format(query_hash)

        variables = {
            "id": str(user_id),
            "include_reel": "true",
            "fetch_mutual": "true",
            "first": 50,
        }
        url = "{}&variables={}".format(graphql_query_URL, str(json.dumps(variables)))

        self.driver.get(url)
        sleep(self.rng())

        pre = self.driver.find_element_by_xpath("//td[@class='line-content']")
        data = json.loads(pre.text)
        following_page = data["data"]["user"]["edge_follow"]["edges"]
        following_list = []
        i = 1

        for user in following_page:
            print("{}) {}".format(i, user["node"]["username"]))
            following_list.append(user["node"]["username"])
            i += 1

        has_next_page = data["data"]["user"]["edge_follow"]["page_info"]["has_next_page"]

        while has_next_page:
            sleep(self.rng())
            end_cursor = data["data"]["user"]["edge_follow"]["page_info"]["end_cursor"] # get next page reference

            variables = {
                "id": str(user_id),
                "include_reel": "true",
                "fetch_mutual": "true",
                "first": 50,
                "after": end_cursor,
            }
            url = "{}&variables={}".format(graphql_query_URL, str(json.dumps(variables)))

            self.driver.get(url)
            sleep(self.rng())

            pre = self.driver.find_element_by_xpath("//td[@class='line-content']")
            data = json.loads(pre.text)

            followers_page = data["data"]["user"]["edge_follow"]["edges"]
            for user in followers_page:
                print("{}) {}".format(i, user["node"]["username"]))
                following_list.append(user["node"]["username"])
                i += 1

            has_next_page = data["data"]["user"]["edge_follow"]["page_info"]["has_next_page"]

        print('Final following_list: ', following_list, "\nNum following counted: ", len(following_list), sep='')
        print("Successfully fetched following list!")
        return following_list


    def get_latest_followers_list_from_file(self, username):
        dates_list = []
        if os.path.isfile('../followers.json'):    #if the file exists, append. Otherwise create new file
            with open('../followers.json') as file:
                data = json.load(file)
                index = 0
                exists = False
                for i in data['followers']:
                    if i['username'] == username:
                        date_time = datetime.datetime.strptime(i['date'], '%Y-%m-%d %H:%M:%S')
                        date_dict = (index, date_time)
                        dates_list.append(date_dict)
                        exists = True
                    index += 1
                if exists:
                    sorted_list = sorted(dates_list, key=lambda x: x[1], reverse=True)
                    print("Successfully fetched latest followers from followers.json!")
                    # print(data['followers'][sorted_list[0][0]]['followers'])
                    return data['followers'][sorted_list[0][0]]['followers']
                else:
                    # this is where you'd call get_followers_list but i won't do that for now.
                    print("No existing followers list was found for user @", username, sep='')
        else:
            print("followers.json not found!")


    def get_latest_following_list_from_file(self, username):
        dates_list = []
        if os.path.isfile('../following.json'):    #if the file exists, append. Otherwise create new file
            with open('../following.json') as file:
                data = json.load(file)
                index = 0
                exists = False
                for i in data['following']:
                    if i['username'] == username:
                        date_time = datetime.datetime.strptime(i['date'], '%Y-%m-%d %H:%M:%S')
                        date_dict = (index, date_time)
                        dates_list.append(date_dict)
                        exists = True
                    index += 1
                if exists:
                    sorted_list = sorted(dates_list, key=lambda x: x[1], reverse=True)
                    print("Successfully fetched latest following from following.json!")
                    # print(data['following'][sorted_list[0][0]]['following'])
                    return data['following'][sorted_list[0][0]]['following']
                else:
                    # this is where you'd call get_following_list but i won't do that for now.
                    print("No existing following list was found for user @", username, sep='')
        else:
            print("following.json not found!")

    
    def get_latest_unfollowers_list_from_file(self, username):
        dates_list = []
        if os.path.isfile('../unfollowers.json'):    # If the file exists, append. Otherwise create new file
            with open('../unfollowers.json') as file:
                data = json.load(file)
                index = 0
                exists = False
                for i in data['unfollowers']:
                    if i['username'] == username:
                        date_time = datetime.datetime.strptime(i['date'], '%Y-%m-%d %H:%M:%S')
                        date_dict = (index, date_time)
                        dates_list.append(date_dict)
                        index += 1
                        exists = True
                if exists:
                    sorted_list = sorted(dates_list, key=lambda x: x[1], reverse=True)
                    print("Successfully fetched latest unfollowers from unfollowers.json!")
                    # print(data['unfollowers'][sorted_list[0][0]]['unfollowers'])
                    return data['unfollowers'][sorted_list[0][0]]['unfollowers']
                else:
                    print("No existing following list was found for user @", username, sep='')
        else:
            print("unfollowers.json not found!")


    def get_unfollowers_list(self, followers_list, following_list):
        # Finding the people I'm following that aren't following me back. E.g. the people in following that aren't in followers.
        a = set(followers_list)
        b = set(following_list)
        unfollowers = list(set(b).difference(a))
        print(unfollowers)
        print("Number of people I'm following that aren't in followers ---> ", len(unfollowers))
        print("Successfully calculated list of people you follow who don't follow you back.")
        return unfollowers


    def unfollow_unfollowers(self, unfollowers_list, limit=10):
        test = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
        remaining_unfollowers = test[limit:] # should be 11-16
        print("\nremaining_followers: \n", remaining_unfollowers)

        for user in unfollowers_list:
            self.unfollow_user(user)
            sleep(self.rng())


    def write_list_to_file(self, username, list_data, filename):

        now = datetime.datetime.now()

        if os.path.isfile('../' + filename + '.json'):    #if the file exists, append. Otherwise create new file
            append_dict = {
                "username": username,
                "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(list_data),
                filename: list_data
            }
            with open('../' + filename + '.json') as file:

                data = json.load(file)
                data[filename].append(append_dict)
            self.write_to_file(data, filename)

        else:
            new_dict = {
                filename: [
                    {
                        "username": username,
                        "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "total": len(list_data),
                        filename: list_data
                    }
                ]
            }
            self.write_to_file(new_dict, filename)

        print("Successfully wrote list to file: {0}.json".format(filename))


    def write_to_file(self, data, filename):
        with open('../' + filename + '.json', 'w') as file:
            json.dump(data, file, indent=4)


    def read_json_followers(self):
        with open('followers.json', 'r') as data:
            users = json.load(data)
        print(users["followers"])


    def get_num_followers(self, username):
        self.go_to_user(username)
        # sleep(self.rng())
        sleep(2.1)
        followers = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span').text.replace(',', '')
        print(username, "'s Total Followers: ", followers, sep='')
        return int(followers)


    def get_num_following(self, username):
        self.go_to_user(username)
        # sleep(self.rng())
        sleep(2.1)
        following = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span').text.replace(',', '')
        print(username, "'s Total Following: ", following, sep='')
        return int(following)


    def get_user_followers_count(self):
        pass
        #will be useful inside the get_followers_list/get_following_list function


    def get_user_following_count(self):
        pass
        #will be useful inside the get_followers_list/get_following_list function


    def like_post(self):
        pass


    def follow_similar_users(self):
        pass
        # E.g. follow people that appear when clicking that triangle that shows recommended users similar to that account.


    def like_and_follow_on_hashtag(self):
        pass
        #some random number of likes and random number of follows on a certain hashtag to gain growth/engagement (random so that no bot like actions identified)


    def check_user_follower_following_ratio(self):
        pass
        #checks if a user has more followers than following (don't follow them if they have larger following...)
        #this is a nice to have, pretty easy to implement with existing functions, for later development.


    def close_driver(self):
        self.driver.quit()


# username = 'cole_mcconnell'
# username = 'BillionaireCole'
username = 'xylotheous'

bot = instagram_bot()
# bot.write_list_to_file(username, bot.get_following_list_v2(username), "following")
# bot.write_list_to_file(username, bot.get_followers_list_v2(username), "followers")
# bot.get_followers_list(username)
# bot.get_following_list(username)

followers = bot.get_latest_followers_list_from_file(username)
following = bot.get_latest_following_list_from_file(username)
unfollowers = bot.get_unfollowers_list(followers, following)
bot.write_list_to_file(username, unfollowers, "unfollowers")
# bot.unfollow_unfollowers(unfollowers, 10)

# unfollowers = bot.get_latest_unfollowers_list_from_file(username)
# unfollowers = [1,2,3,4,5,6,7,8,9,10,11,12]
# bot.unfollow_unfollowers(unfollowers, 10)

# bot.get_followers_list_v2(username)
# bot.get_following_list_v2(username)

bot.close_driver()

#------------------
# DO DO LIST:
#------------------

"""
Then need to make some kind of list updater somehow? E.g. if we have a list of 100 ppl to unfollow and set it to iterate 20 of them and unfollow them, then pass back to the write unfollowers.json file the remaining 80 ppl in that list we didn't iterate, so it knows which ones we haven't unfollowed yet + more efficient than going back and fetching all unfollowers each time.

merge all get_latest_followers/following/unfollowers_list_from_file functions into single function with new parameter to distinguish which to run

Implement a "Starting so and so function" statement in each major function

Make a UI that enables us to 1 click choose which of these particular commands we want to execute. Flutter or Angular... react?
"""