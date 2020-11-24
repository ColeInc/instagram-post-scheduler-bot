import os
import re
import json
import emojis
import random
import datetime
import itertools
import mysql.connector
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class instagram_bot:

    # ---------------------------
    # Windows:
    # ---------------------------

    # def __init__(self):
    #     self.username = ''
    #     self.password = ''
    #     self.mysql = ''
    #     self.driver = ''
    #     self.resources = 'D:/Cole/Auckland University/Instagram Post Scheduler Bot/Instagram Bot/'
    #     print('-----------------------------------------------------------------------------')
    #     print("Starting instagram_bot in Windows via geckodriver!")
    #     print("Waiting for login from user...")
    #     print('-----------------------------------------------------------------------------')


    # ---------------------------
    # Amazon Linux 2:
    # ---------------------------
    
    def __init__(self):
        self.username = ''
        self.password = ''
        self.mysql = ''
        self.driver = ''
        self.resources = '/home/ec2-user/docker/app/flask/resources/'
        print('-----------------------------------------------------------------------------')
        print("Starting instagram_bot in Amazon Linux 2 via headless firefox!")
        print("Waiting for login from user...")
        print('-----------------------------------------------------------------------------')

    # ---------------------------


    def login(self):
        try:
            print("Logging in...")

            # CURRENT EC2 PUBLIC URL:
            # -------------------------- //
            ec2_url = 'ec2-13-211-201-181.ap-southeast-2.compute.amazonaws.com'
            # -------------------------- //

            self.driver = webdriver.Remote(
            command_executor=ec2_url + ':4444/wd/hub',
            desired_capabilities=DesiredCapabilities.FIREFOX)

            # for local testing:
            # self.driver = webdriver.Firefox()

            sleep(2.47)
            self.driver.get('https://www.instagram.com/accounts/login')
            sleep(self.rng()-1.5)
            self.driver.find_element_by_name('username').send_keys(self.username)
            self.driver.find_element_by_name('password').send_keys(self.password, Keys.RETURN)
            sleep(self.rng())
            
            return self.check_suspicious_login_attempt()   

        except Exception as e:
            print('Error logging in:\n', e, sep='')
            try:
                self.driver.quit()
            except:
                print('Could not close Selenium Webdriver...')
            finally:
                return 1, 'Error logging in:\n' + str(e)


    def connect_to_mysql(self):
        print("Connecting to MySQL Database...")

        with open(self.resources + 'mysql_credentials.json', 'r') as data:
            credentials = json.load(data)
        for i in credentials:
            host = i["host"]
            username = i["username"]
            password = i["password"]

        try:
            mydb = mysql.connector.connect(
                host=host,
                user=username,
                password=password,
                database='instagram_bot'
            )
            self.mysql = mydb
            self.cursor = mydb.cursor()

            print("Connected to database!")
            return True

        except Exception as e:
            print("Error while connecting to MySQL db:\n", e)


    def close_database_connection(self):
        self.cursor.close()
        self.mysql.close()
        print("Successfully closed MySQL Database connection.")


    def check_suspicious_login_attempt(self):
        if self.check_user_logged_in():
            print('Logged in to user @{}!'.format(self.username))
            return 0, 'Logged in to user @' + self.username + '!'
        else:
            try:
                self.driver.find_elements_by_xpath("//*[contains(text(), 'Suspicious Login Attempt')]")
                print("Suspicious Login Attempt identified!")
                user_email = self.driver.find_element_by_xpath("//label[@class='UuB0U Uwdwc']").text

                print("Failed to login, security code was sent to {}.".format(user_email))

                # from this point onwards, only way for this user to login is to continue in enter_security_code function via API call below.

                # This is where i'd create a separate function to login to gmail somehow and use gmail API to fetch security code from email.. but would only work for gmail users :/

                self.driver.find_element_by_xpath("//button[contains(text(), 'Send Security Code')]").click() # clicks on "Send Security Code" button
                print("Waiting on user to provide security code...")
                return 2, "Suspicious Login Attempt identified!\nFailed to login, security code was sent to " + user_email

            except Exception as e:
                print("An error occurred while logging in. Please revise login credentials.")
                return 3, "An error occurred while logging in. Please revise login credentials."

        
    def check_user_logged_in(self):
        try:
            self.driver.find_element_by_xpath("//img[@class='_6q-tv']").text
            return True
        except Exception as e:
            print("An error occurred while logging in.")
            return False


    def enter_security_code(self, security_code):
        print("Entering security code received from user...")
        self.driver.find_element_by_name('security_code').send_keys(security_code, Keys.RETURN)
        sleep(self.rng())
        if self.check_user_logged_in():
            print("Successfully logged in with security code!")
            return (0, "Successfully logged in with security code!")
        else:
            return(1, "An error occurred while trying to login with provided security code.")
        
        
    def rng(self):
        num = random.randint(3600,8200) / 1000
        # num = random.randint(6269,10213) / 1000
        return num


    def go_to_user(self, username):
        print("Going to user --> @{}".format(username))
        self.driver.get('https://www.instagram.com/{}'.format(username))
        sleep(self.rng())
        print("Loaded @{}'s Page.".format(username))


    def follow_user(self, username):
        self.go_to_user(username)
        sleep(self.rng())
        follow_button = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button')
        follow_button.click()
        sleep(self.rng())


    # def unfollow_user(self, username):
    #     self.go_to_user(username)
    #     try:
    #         print("Unfollowing {}...".format(username))
    #         # following_button = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/div[2]/div/span/span[1]/button').click()
    #         self.driver.find_element_by_xpath("//button[@class='_5f5mN    -fzfL     _6VtSN     yZn4P   ']").click()
    #         sleep(1)
    #         # self.driver.find_element_by_xpath("//button[contains(text(), 'Unfollow')]").click()
    #         self.driver.find_element_by_xpath("//button[@class='aOOlW -Cab_   ']").click()
    #         # sleep(self.rng())
    #         print("Unfollowed {}!".format(username))
    #         return 0, "Unfollowed successfully."
    #     except NoSuchElementException:
    #         print("You are not following that user!")
    #         return 0, "You are not following that user!"
    #     except:
    #         html = self.driver.page_source
    #         self.write_to_file(html, 'html')
    #         if self.check_for_try_again_later_notice():
    #             return 1, "Identified maximum like/follow actions restriction! Please wait a while before trying again."


    def unfollow_user_v2(self, username):
        self.go_to_user(username)
        print("Unfollowing {}...".format(username))

        try: # try unfollow them first, most efficient. if it fails, then we check if we're already following them, etc.
            follow_button = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//button[@class='_5f5mN    -fzfL     _6VtSN     yZn4P   ']"))) # UNFOLLOW CLASS
            follow_button.click()
            sleep(1.57)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[@class='aOOlW -Cab_   ']"))).click()
            print("Unfollowed {}!".format(username))
            return 0, "Unfollowed successfully."

        except Exception as e:
            try:
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//button[@class='sqdOP  L3NKy    _8A5w5    ']"))).click() # UNFOLLOW CLASS on some different users? maybe private acc?
                sleep(1.57)
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[@class='aOOlW -Cab_   ']"))).click()
                print("Unfollowed {}!".format(username))
                return 0, "Unfollowed successfully."

            except Exception as e:
                try:
                    follow_button = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//button[@class='_5f5mN       jIbKX  _6VtSN     yZn4P   ']"))) # FOLLOW CLASS 
                except:
                    try:
                        follow_button = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//button[@class='sqdOP  L3NKy   y3zKF     ']"))) # FOLLOW CLASS of private page.
                    except Exception as e:
                        print(e)
                        html = self.driver.page_source
                        self.write_to_file(html, 'html')
                        if self.check_for_try_again_later_notice():
                            return 1, "Identified maximum like/follow actions restriction! Please wait a while before trying again."

                if follow_button.text == "Follow":
                    print("You are not following that user!")
                    return 0, "You are not following that user!"
                else:
                    print(e)
                    html = self.driver.page_source
                    self.write_to_file(html, 'html')
                    if self.check_for_try_again_later_notice():
                        return 1, "Identified maximum like/follow actions restriction! Please wait a while before trying again."


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
                    follower = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, nth_child))).text # can alter this 3 seconds to be more/less if followers aren't loading fast enough, or waiting too long each time.
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
        legal bc we're using instagram's APIs without official permission so be careful where you use this lads.
        Only difference between followers and following v2 functions is the hash used inside the URL. Different hash for followers/following.
        """

        real_amount = self.get_num_followers(username)

        try:
            user_id = self.driver.execute_script("return window.__additionalData[Object.keys(window.__additionalData)[0]].data.graphql.user.id")
        except:
            user_id = self.driver.execute_script("return window._sharedData." "entry_data.ProfilePage[0]." "graphql.user.id")

        self.driver.get("https://www.instagram.com/static/bundles/es6/Consumer.js/1f67555edbd3.js")
        page_source = self.driver.page_source
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

        # pre = self.driver.find_element_by_xpath("//td[@class='line-content']") # looks like this only works when in chromedriver (definitely not working in firefox!)
        pre = self.driver.find_element_by_xpath("//body/pre") # works in firefox
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

            self.driver.get(url)
            sleep(self.rng())

            # pre = self.driver.find_element_by_xpath("//td[@class='line-content']") # looks like this only works when in chromedriver (definitely not working in firefox!)
            pre = self.driver.find_element_by_xpath("//body/pre") # works in firefox
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

        # pre = self.driver.find_element_by_xpath("//td[@class='line-content']") # looks like this only works when in chromedriver (definitely not working in firefox!)
        pre = self.driver.find_element_by_xpath("//body/pre") # works in firefox
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
            sleep(self.rng()-1.52) # maybe decrease or increase this...
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

            # pre = self.driver.find_element_by_xpath("//td[@class='line-content']") # looks like this only works when in chromedriver (definitely not working in firefox!)
            pre = self.driver.find_element_by_xpath("//body/pre") # works in firefox
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
        # Add a parameter that defines the maximum number of days old a value for the specified user is allowed to be, if found inside the corresponding .json file. E.g. nothing older than 3 days

        print("Getting latest followers list from followers.json...")
        dates_list = []
        if os.path.isfile(self.resources + 'followers.json'):
            with open(self.resources + 'followers.json') as file:
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
                    return None
        else:
            print("followers.json not found!")
            return None


    def get_latest_following_list_from_file(self, username):
        print("Getting latest following list from following.json...")
        dates_list = []
        if os.path.isfile(self.resources + 'following.json'):
            with open(self.resources + 'following.json') as file:
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
                    return None
        else:
            print("following.json not found!")
            return None

    
    def get_latest_unfollowers_list_from_file(self, username):
        print("Getting latest unfollowers list from unfollowers.json...")
        dates_list = []
        if os.path.isfile(self.resources + 'unfollowers.json'):
            with open(self.resources + 'unfollowers.json') as file:
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
                    return None
        else:
            print("unfollowers.json not found!")
            return None


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
        print("Unfollowing {} users from your unfollow list...".format(limit))
        try:
            i = 0
            for user in unfollowers_list:
                if i == limit:
                    break
                print("[", i+1, " of ", limit, "]: ", sep="")
                resp = self.unfollow_user_v2(user)
                if resp[0] > 0:
                    break
                sleep(self.rng())
                i += 1

            remaining_unfollowers = unfollowers_list[i:]
            print("\nNumber of remaining unfollowers: ", len(remaining_unfollowers))
            self.write_list_to_file(self.username, remaining_unfollowers, "unfollowers") # writing the updated unfollowers list back to unfollowers.json.

        except Exception as e:
            html = self.driver.page_source
            self.write_to_file(html, 'html')
            print('Error while unfollowing unfollowers:\n', e, sep='')


    def write_list_to_file(self, username, list_data, filename):
    
        now = datetime.datetime.now()

        if os.path.isfile(self.resources + filename + '.json'):    #if the file exists, append. Otherwise create new file
            append_dict = {
                "username": username,
                "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(list_data),
                filename: list_data
            }
            with open(self.resources + filename + '.json') as file:
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


    def write_list_to_file_v2(self, username, list_data, filename):
        
        now = datetime.datetime.now()

        if os.path.isfile(self.resources + filename + '.json'):    # check if file exists already, otherwise create new file
            append_dict = {
                "username": username,
                "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(list_data),
                filename: list_data
            }
            with open(self.resources + filename + '.json') as file:
                data = json.load(file)
                index = 0
                exists = False
                for i in data['followers']:
                    if i['username'] == username:
                        data['followers'][index] = append_dict
                        exists = True
                    index += 1
                
                if not exists:
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
        with open(self.resources + filename + '.json', 'w') as file:
            json.dump(data, file, indent=4)


    def read_json_followers(self):
        with open('followers.json', 'r') as data:
            users = json.load(data)
        print(users["followers"])


    def get_num_followers(self, username):
        self.go_to_user(username)
        # sleep(self.rng())
        followers = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span').text.replace(',', '')
        print(username, "'s Total Followers: ", followers, sep='')
        return int(followers)


    def get_num_following(self, username):
        self.go_to_user(username)
        # sleep(self.rng())
        following = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span').text.replace(',', '')
        print(username, "'s Total Following: ", following, sep='')
        return int(following)


    def like_and_comment_x_posts_of_hashtag(self, hashtag, number_of_likes=0, number_of_comments=0):
        print("Liking and commenting on {} recent posts under the #{} hashtag...".format(str(number_of_likes), hashtag))
        # Takes a hashtag and a number of posts to like, and likes a random x amount of posts from the "most recent" section of that certain hashtag.

        if number_of_comments == 0 and number_of_likes == 0:
            return 0, "User specified to like and comment on 0 posts. There you go pal, it's done."

        try:
            hashtag = hashtag.strip("#") # Removes any actual hashtags inputted
            self.driver.get('https://www.instagram.com/explore/tags/' + hashtag)
            sleep(self.rng())

            self.driver.find_elements_by_class_name("eLAPa")[9].click() # click on the first post in the Recent Posts section (10th box down, therefore index 9)
            sleep(2.81)
                
            for i in range(max(number_of_likes, number_of_comments)):
                print("[Post {} out of {}]".format(str(i+1), str(max(number_of_likes, number_of_comments))))

                if i+1 < number_of_likes: # while we haven't hit maximum specified likes, like the post.
                    self.driver.find_element_by_xpath("//span[@class='fr66n']/button").click() # click the like button on current post
                    print("Liked!")
                    sleep(self.rng()-2.51)

                if i+1 < number_of_comments: # while we haven't hit maximum specified comments, comment on the post.
                    comment = self.fetch_random_comment()
                    self.driver.find_element_by_class_name('Ypffh').click() # need to click into the comments textbox first
                    sleep(0.2) # stress test this to decrease as much as possible
                    self.driver.find_element_by_class_name('Ypffh').send_keys(emojis.encode(comment), Keys.RETURN) # changing any emoji text :heart_eyes: to an emoji here 
                    print("Commented: {}".format(comment))                                                                     
                    sleep(self.rng()-1.02)

                self.driver.find_element_by_class_name('coreSpriteRightPaginationArrow').click() # click on the next button to go to next post
                sleep(self.rng()-1.11)

                if i % 5 == 0: # for every 5 posts press Right Arrow twice to skip a post every once in a while to avoid looking sus when liking many posts.
                    self.driver.find_element_by_class_name('coreSpriteRightPaginationArrow').click() # click on the next button to go to next post
                    sleep(self.rng()-1.27)
            return 0, "Successfully liked " + str(number_of_likes) + " recent posts under the #" + hashtag + " hashtag!"

        except Exception as e:
            if self.check_for_try_again_later_notice():
                return 1, "Identified maximum like/follow actions restriction! Please wait a while before trying again."
            else:
                print("An error occurred while liking posts under this hashtag (It isn't a 'Try Again Later' error):\n", e)
                return 2, "An error occurred while liking posts under this hashtag (It isn't a 'Try Again Later' error):\n" + str(e)


    def like_and_comment_on_random_hashtag(self, number_of_likes=0, number_of_comments=0):
        hashtag = self.fetch_random_hashtag()
        return self.like_and_comment_x_posts_of_hashtag(hashtag, number_of_likes, number_of_comments)


    def check_for_try_again_later_notice(self):
        try:
            self.driver.find_elements_by_xpath("//*[contains(text(), 'We restrict certain activity to protect our community')]")
            print("Identified maximum like/follow actions restriction! Please wait a while before trying again.")
            return True
        except:
            print("No 'Try Again Later' notice detected. Looks like you're good kid.")
            return False


    def fetch_random_hashtag(self):
        print("Fetching list of hashtags from file...")
        with open(self.resources + 'hashtag_list.json', 'r') as data:
            hashtag_list = json.load(data)
        index = random.randint(0,len(hashtag_list['hashtags'])-1)
        hashtag = hashtag_list['hashtags'][index]
        print("Random Hashtag --> #", hashtag, sep="")
        return hashtag


    def fetch_random_comment(self):
        print("Fetching list of comments from file...")
        with open(self.resources + 'comment_list.json', 'r', encoding="utf8") as data:
            comment_data = json.load(data)
        index = random.randint(0,len(comment_data['comments'])-1)
        comment = comment_data['comments'][index]
        # current_index = comment_data['comments'][0]['current_index']
        # comment_list = comment_data['comments'][0]['comments']
        # print("Random Comment --> ", comment, sep="")
        return comment


    def fetch_id_from_username(self):
        """
        Takes the instagram user's username, goes to MySQL database, User table, checks if username already has record and returns UUID, 
        otherwise creates new table record with auto-generated UUID
        """

        try:
            print("Fetching UUID from User table...")
            # username = 'goose'

            sql = "SELECT * FROM user WHERE username=%s" # gotta use dat %s to prevent SQL injections. Means input has to be a string
            self.cursor.execute(sql, (self.username,))
            result = self.cursor.fetchall()

            if len(result) > 0:
                print("Successfully fetched UUID for {}.".format(self.username))
                return 0, str(result[0][0])
            else:
                print("User {} does not exist in table, creating new record...")

                sql = "INSERT INTO user (username) VALUES (%s)" # inserting new username into User table, which creates new uuid to match
                self.cursor.execute(sql, (self.username,))
                self.mysql.commit()
                print(self.cursor.rowcount, "record(s) inserted.")

                new_id = self.cursor.lastrowid
                return 0, str(new_id)

        except Exception as e:
            print('Error fetching UUID from User table:\n', e, sep='')
            return 1, 'Error fetching UUID from User table:\n' + str(e)


    def follow_users_under_hashtag(self, uuid, hashtag, number_of_users=0):
        print("Following {} users under the recent posts section of the #{} hashtag...".format(str(number_of_users), hashtag))

        if number_of_users == 0:
            return 0, "User specified to follow 0 people. There you go pal, consider it done."

        new_following_list = []

        try:
            hashtag = hashtag.strip("#") # Removing any actual hashtag characters inputted
            self.driver.get('https://www.instagram.com/explore/tags/' + hashtag)
            sleep(self.rng())

            self.driver.find_elements_by_class_name("eLAPa")[9].click() # click on the first post in the Recent Posts section (10th box down, therefore index 9)
            sleep(2.81)
                
            for i in range(number_of_users):
                print("[Post {} out of {}]".format(str(i+1), str(number_of_users)))

                follow_button = self.driver.find_element_by_xpath("//div[@class='bY2yH']/button")

                if follow_button.text == 'Follow':
                    follow_button.click()
                    current_post_username = self.driver.find_element_by_xpath("//a[@class='sqdOP yWX7d     _8A5w5   ZIAjV ']").text
                    insert_tuple = (int(uuid), current_post_username)
                    new_following_list.append(insert_tuple)
                    print("Followed {}!".format(current_post_username))
                    sleep(self.rng()-3.03)
                else:
                    print("Already following user.")

                self.driver.find_element_by_class_name('coreSpriteRightPaginationArrow').click() # click on the next button to go to next post
                sleep(self.rng()-1.51)

                if i % 5 == 0: # for every 5 posts press Right Arrow twice to skip a post every once in a while to avoid looking sus when liking many posts.
                    self.driver.find_element_by_class_name('coreSpriteRightPaginationArrow').click() # click on the next button to go to next post
                    sleep(self.rng()-1.51)

            print("Final new_following_list: ", new_following_list)
            return 0, "Successfully followed " + str(number_of_users) + " users under the #" + hashtag + " hashtag!", new_following_list

        except Exception as e:
            print("Error:\n", e, "\n--------------------------------------")
            if self.check_for_try_again_later_notice():
                return 1, "Identified maximum like/follow actions restriction! Please wait a while before trying again."
            else:
                print("An error occurred while following users under this hashtag (It isn't a 'Try Again Later' error):\n\n", e)
                return 2, "An error occurred while following users under this hashtag (It isn't a 'Try Again Later' error):\n" + str(e)


    def insert_into_following_table(self, following_list):
        try:
            print("Inserting list of users you followed into following table...")
            sql = """INSERT INTO following (user_id, username, date_followed) VALUES (%s, %s, NOW())"""
            self.cursor.executemany(sql, following_list)
            self.mysql.commit()
            print(self.cursor.rowcount, "record(s) inserted.")
            return 0, "Successfully inserted list of users you followed into Following Table."

        except Exception as e:
            print('Error inserting users into following table:\n', e, sep='')
            return 1, 'Error inserting users into following table:\n' + str(e)


    def get_users_older_than_x_days(self, uuid, number_of_days):
        print("Fetching users you follow that don't follow you back, that you've been following for {} day(s)..".format(number_of_days))

        try:
            sql = """SELECT username FROM following WHERE user_id = %s
            AND date_followed < NOW() - INTERVAL %s DAY"""

            self.cursor.execute(sql, (uuid, number_of_days))
            result = self.cursor.fetchall()

            following_list = list(map(lambda n: n[0], result))
            print("following_list: ", following_list) # delete

            print("Successfully fetched list from MySQL database.")
            return 0, following_list
        except Exception as e:
            print("Error at get_users_older_than_x_days:\n\n", e)
            return 1, "Error at get_users_older_than_x_days."


    def get_neverfollowers_list(self, followers_list, following_list):
        print("Calculating users you followed that haven't followed you back (next we're going to unfollow them)..")
        
        """ for user in following_list, if user NOT in followers_list, add to neverfollowers list """

        a = set(followers_list)
        b = set(following_list)
        neverfollowers = list(set(b).difference(a))
        print("neverfollowers list: ", neverfollowers) # delete this
        return neverfollowers
        

    def remove_unfollowed_neverfollowers_from_table(self, uuid, neverfollowers_list):
        print("Deleting users you've unfollowed from MySQL database...")
        
        try:
            format_strings = ','.join(["'%s'"] * len(neverfollowers_list))
            sql = "DELETE FROM following WHERE user_id = %s and username IN (%s)" % (uuid, format_strings) % tuple(neverfollowers_list)
            self.cursor.execute(sql)
            self.mysql.commit()
            print(self.cursor.rowcount, "record(s) deleted")
            return 0, str(self.cursor.rowcount) + "record(s) deleted"
        except Exception as e:
            print("Error while deleting neverFollowers from MySQL Following table.. (NOT GOOD).")
            return 1, "Error while deleting neverFollowers from MySQL Following table.. (NOT GOOD)."


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


    def follow_on_hashtag(self):
        pass
        #some random number of likes and random number of follows on a certain hashtag to gain growth/engagement (random so that no bot like actions identified)


    def check_user_follower_following_ratio(self):
        pass
        #checks if a user has more followers than following (don't follow them if they have larger following...)
        #this is a nice to have, pretty easy to implement with existing functions, for later development.


    def close_driver(self):
        print('Closed selenium webdriver!')
        self.driver.quit()
