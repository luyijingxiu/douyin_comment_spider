#!/usr/bin/env/ python
# -*- coding:utf-8 -*-

import os
import re
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import dy_search
import spider_util

file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, 'config.json'), encoding='UTF-8') as fp:
    CONFIG = json.load(fp)

tik_tok_prefix_url = 'https://www.douyin.com'

video_regex = r"^https://www.douyin.com/video/(.*)\?.*$"

file_save_path = file_path + r'/spider/'

# http://chromedriver.storage.googleapis.com/index.html
chrome_driver_path = file_path + '/chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
browser = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
browser.maximize_window()



if __name__ == '__main__':
    # dy_search.begin_search(browser, "屋顶光伏", 300, 182, 0)
    dy_search.save_searched_video_list_data(browser,"屋顶光伏")
