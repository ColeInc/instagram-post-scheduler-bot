import os
import json
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

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
        num = random.randint(220,620) / 100
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

    def like_post(self):
        pass

    def follow_similar_users(self):
        pass
        # E.g. follow people that appear when clicking that triangle that shows recommended users similar to that account.

bot = instagram_bot()
bot.unfollow_user('iiv.3z')

# Make a UI in flutter that enables us to 1 click choose which of these particular commands we want to execute.