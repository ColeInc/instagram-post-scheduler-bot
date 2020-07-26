#delete:
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


    def random_scroll_function(self, num_of_scrolls): #remove, too niche having first line like this (just for followers modal)
        followDivBox = self.driver.find_element_by_xpath("//div[@class='isgrP']")
        scroll = 0
        while scroll < num_of_scrolls:
            #executes javascript script to scroll page... bit choppy... might want to find better scrolling script
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', followDivBox)
            scroll += 1
            sleep(self.rng())


    def get_followers_list(self, username, following=False):
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
                    print(follower_index, ") ", follower, sep="")
                    following_list.append(follower) if following else followers_list.append(follower)

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
                print('Final following_list: ', following_list, "\nNum following counted: ", len(following_list), sep='')
                print("Successfully fetched following list!")
                return following_list
            else:
                print('Final followers_list: ', followers_list, "\nNum followers counted: ", len(followers_list), sep='')
                print("Successfully fetched list of following!")
                return followers_list
        except Exception as e:
            print('Error while iterating followers/following list:\n', e, sep="")


    def get_following_list(self, username):
        self.get_followers_list(username, True)


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


    def write_list_to_file(self, username, list_data, filename):
        
        now = datetime.datetime.now()

        if os.path.isfile('./' + filename + '.json'):    #if the file exists, append. Otherwise create new file
            append_dict = {
                "username": username,
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
                        "username": username,
                        "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "total": len(list_data),
                        filename: list_data
                    }
                ]
            }
            self.write_to_file(new_dict, filename)
        
        print("Successfully wrote list to file: {0}".format(filename))


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


    def get_num_following(self, username):
        self.go_to_user(username)
        sleep(self.rng())
        following = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span').text.replace(',', '')
        print(username, "'s Total Dollowing: ", following, sep='')
        return int(following)


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


    def close_driver(self):
        self.driver.quit()


username = 'cole_mcconnell'
# username = 'BillionaireCole'
# username = 'xylotheous'
bot = instagram_bot()
# account = 'BillionaireCole'
# bot.write_list_to_file(username, bot.get_followers_list_v2(username), "followers")
# bot.write_list_to_file(bot.get_followers_list_v2('xylotheous'), "followers")
bot.get_following_list('cole_mcconnell')
# bot.get_following_list('BillionaireCole')
# followers_list = self.driver.find_element_by_class_name('-nal3 ')
# self.driver.find_element_by_xpath("//a[contains(@href, '/billionairecole/followers/)]")
bot.close_driver()

# Make a UI in flutter that enables us to 1 click choose which of these particular commands we want to execute.