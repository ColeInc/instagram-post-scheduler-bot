from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import os

class InstagramBot:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome('C:/Windows/chromedriver')

bot = InstagramBot('billy', 'password1')