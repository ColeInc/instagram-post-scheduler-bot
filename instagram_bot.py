import os
import json
import random
import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class instagram_bot:

    def __init__(self):
        self.username = ''
        self.password = ''
        # self.driver = webdriver.Chrome('C:/Windows/chromedriver')
        # self.fetch_credentials()
        # self.login()

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
        num = random.randint(320,920) / 100
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
        followers_list = self.driver.find_element_by_xpath("//a[contains(@href, '/" + username.lower() + "/following/')]")
        followers_list.click()
        sleep(self.rng())

    def random_scroll_function(self, num_of_scrolls):
        followDivBox = self.driver.find_element_by_xpath("//div[@class='isgrP']")
        scroll = 0
        while scroll < num_of_scrolls:
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', followDivBox)   #executes javascript script to scroll page... bit choppy... might want to find better scrolling script
            scroll += 1
            sleep(self.rng())

    def get_followers_list(self, username, limit=50):
        # this ideally needs to be stored inside a db... can't call this every time
        self.go_to_followers_list(username)
        sleep(self.rng())
        followers_list = []
        for i in range(limit):
            if i % 7 == 0:
                self.random_scroll_function(1)
            follower = self.driver.find_elements_by_class_name('FPmhX')[i]
            followers_list.append(follower.text)
            print(i, ') ', follower.text, sep='')
        print("Current number of followers: ", len(followers_list), sep="")
        return followers_list

    def get_following_list(self, username, limit=50):
        # this ideally needs to be stored inside a db... can't call this every time tbh
        self.go_to_following_list(username)
        sleep(self.rng())
        following_list = []
        for i in range(limit):
            if i % 7 == 0:
                self.random_scroll_function(1)
            user = self.driver.find_elements_by_class_name('FPmhX')[i]
            following_list.append(user.text)
            # print(i, ') ', user.text, sep='')
        print("Current number of people you're following: ", len(following_list), sep="")
        return following_list

    def unfollow_unfollowers(self):
        #get list of my followers, get list of people i'm following, do a match on them and create a list of anyone else who isn't in that match then iterate through them and unfollow.
        
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
        
    def like_post(self):
        pass

    def follow_similar_users(self):
        pass
        # E.g. follow people that appear when clicking that triangle that shows recommended users similar to that account.

    def like_and_follow_on_hashtag(self):
        #some random number of likes and random number of follows on a certain hashtag to gain growth/engagement (random so that no bot like actions identified)
        pass

    def check_user_follower_following_ratio(self):
        #this is a nice to have, pretty easy to implement with existing functions, for later development.
        pass

bot = instagram_bot()
# bot.get_followers_list('BillionaireCole')
bot.write_list_to_file(["cat", "dog", "mouse"], "following")
# bot.go_to_following_list('BillionaireCole')
# followers_list = self.driver.find_element_by_class_name('-nal3 ')
# self.driver.find_element_by_xpath("//a[contains(@href, '/billionairecole/followers/)]")

# Make a UI in flutter that enables us to 1 click choose which of these particular commands we want to execute.