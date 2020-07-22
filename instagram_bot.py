#delete unused:
import itertools
from explicit import waiter, XPATH
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import json
import random
import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
        num = random.randint(3200,9200) / 1000
        return num

    def go_to_user(self, username):
        self.driver.get('https://www.instagram.com/' + username)

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
            following_button = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[2]/span/span[1]/button')
            following_button.click()
            sleep(3)
            following_button = self.driver.find_element_by_xpath("//button[contains(text(), 'Unfollow')]")
            following_button.click()
            sleep(self.rng())
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

    def random_scroll_function(self, num_of_scrolls):
        followDivBox = self.driver.find_element_by_xpath("//div[@class='isgrP']")
        scroll = 0
        while scroll < num_of_scrolls:
            #executes javascript script to scroll page... bit choppy... might want to find better scrolling script
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', followDivBox)
            scroll += 1
            sleep(self.rng())

    def get_followers_list(self, username, limit=1000000):
        # this ideally needs to be stored inside a db... can't call this every time
        self.go_to_followers_list(username)
        sleep(self.rng())
        followers_list = []
        try:
            for i in range(limit): # could make it that the limit here is a scraped number of followers/following in user's main page, before calling this function.
                if i % 7 == 0:
                    self.random_scroll_function(2)
                follower = self.driver.find_elements_by_class_name('FPmhX')[i]
                followers_list.append(follower.text)
                print(i+1, ') ', follower.text, sep='')
            print("Current number of followers: ", len(followers_list), sep="")
            return followers_list
        except Exception as e:
            print(e)
            print('Found all followers!')
            return followers_list
        
    def get_followers_list_v2(self, username):
        num_followers = self.get_num_followers(username)
        # sleep(self.rng())

        self.driver.get("https://www.instagram.com/{0}/".format(username))
        waiter.find_element(self.driver, "//a[contains(@href, '/" + username.lower() + "/followers/')]", by=XPATH).click()
        waiter.find_element(self.driver, "//div[@role='dialog']", by=XPATH)
        followers_list = []

        try:
            followDivBox = self.driver.find_element_by_xpath("//div[@class='isgrP']")

            follower_css = "ul div li:nth-child({}) a.notranslate"
            for group in itertools.count(start=1, step=12):
                for follower_index in range(group, group + 12):                    
                    nth_child = "ul div li:nth-child(" + str(follower_index) + ") a.notranslate"
                    follower = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, nth_child))).text
                    print(follower_index, ") ", follower, sep="")
                    followers_list.append(follower)
                    # print("inner: ", x)
                    self.driver.execute_script("arguments[0].scrollBy(0,250)", followDivBox)

                last_follower = waiter.find_element(self.driver, follower_css.format(follower_index))
                self.driver.execute_script("arguments[0].scrollIntoView();", last_follower)

                
                # self.driver.find_elements_by_class_name('FPmhX')[x-1]

            print('Final followers_list: ', followers_list)

        # except breakLoopError:
        #     print('Final followers_list: ', followers_list)
        except NoSuchElementException:
            print('No Such Element Exception! - Cole')
        except TimeoutException:
            print('TimeoutException!')
            print('Final followers_list: ', followers_list, "\nNum followers counted: ", len(followers_list), sep='')
            return followers_list
        except Exception as e:
            print('Error while iterating followers/following list. \nError: ', e, sep="")

    def get_following_list(self, username, limit=1000000):
        # this ideally needs to be stored inside a db... can't call this every time tbh
        self.go_to_following_list(username)
        sleep(self.rng())
        following_list = []
        try:
            self.random_scroll_function(5)
            for i in range(limit):
                if i % 7 == 0:
                    self.random_scroll_function(2)
                user = self.driver.find_elements_by_class_name('FPmhX')[i]
                following_list.append(user.text)
                print(i+1, ') ', user.text, sep='')
            print("Current number of people you're following: ", len(following_list), sep="")
            return following_list
        except Exception as e: 
            print(e) 
            print("Found all people you're following!")
            return following_list

    def unfollow_unfollowers(self):
        #get list of my followers, get list of people i'm following, do a match on them and create a list of anyone else who isn't in that match then iterate through them and unfollow.
        
        # what about, for i in FOLLOWERS, if next to username says FOLLOWING, then add to list, then only have to iterate one list to get ppl that follow me.
        
        a = [1, 2, 3, 4, 5]
        b = [9, 8, 7, 6, 5]
        set(a).intersection(b) # finds the matches of 2 lists
        
        # followDivBox = self.driver.find_element_by_xpath("//div[@class='isgrP']")
        # scroll = 0
        # while scroll < 5:       #change this 5 to however many times i want to scroll
        #     self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', followDivBox)   #executes javascript script to scroll page... bit choppy... might want to find better scrolling script
        #     scroll += 1
        #     sleep(self.rng())

    def write_list_to_file(self, list_data, filename):
        
        now = datetime.datetime.now()

        if os.path.isfile('./' + filename + '.json'):    #if the file exists, append. Otherwise create new file
            append_dict = {
                "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(list_data),
                filename: list_data
            }
            with open(filename + '.json') as file:
                data = json.load(file)
                data["followers"].append(append_dict)
            self.write_to_file(data, filename)

        else:
            new_dict = {
                filename: [
                    {
                        "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "total": len(list_data),
                        filename: list_data
                    }
                ]
            }
            self.write_to_file(new_dict, filename)
        
    def write_to_file(self, data, filename):
        with open(filename + '.json', 'w') as file:
            json.dump(data, file, indent=4)
        
    def read_json_followers(self):
        with open('followers.json', 'r') as data:
            users = json.load(data)
        print(users["followers"])

    def get_num_followers(self, username):
        self.go_to_user(username)
        sleep(self.rng())
        followers = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span').text.replace(',', '')
        print(username, "'s Total Followers: ", followers, sep='')
        return int(followers)
        
    def get_user_followers_count(self):
        #will be useful inside the get_followers_list/get_following_list function
        pass

    def get_user_following_count(self):
        #will be useful inside the get_followers_list/get_following_list function
        pass
    
    def like_post(self):
        pass

    def follow_similar_users(self):
        pass
        # E.g. follow people that appear when clicking that triangle that shows recommended users similar to that account.

    def like_and_follow_on_hashtag(self):
        #some random number of likes and random number of follows on a certain hashtag to gain growth/engagement (random so that no bot like actions identified)
        pass

    def check_user_follower_following_ratio(self):
        #checks if a user has more followers than following (don't follow them if they have larger following...)
        #this is a nice to have, pretty easy to implement with existing functions, for later development.
        pass

bot = instagram_bot()
bot.get_followers_list_v2('cole_mcconnell')