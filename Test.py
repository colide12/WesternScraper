import random
import re
import requests
import urllib.request, urllib.parse, urllib.error
from urllib.parse import urlparse

import selenium.common.exceptions
import selenium.webdriver.common.action_chains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import selenium.webdriver.common.desired_capabilities
import selenium.webdriver.support.ui
from selenium.webdriver.support import expected_conditions
import time


driver = selenium.webdriver.Firefox(executable_path = 'C:\Python\Mymodules\PythonCrawler\geckodriver')
driver.get('http://lib.snu.ac.kr')
startLogin = driver.find_element_by_css_selector("#top-user-menu-additional > div:nth-child(2) > a:nth-child(1)")
startLogin.click()
time.sleep(3)
ID = driver.find_element_by_css_selector("#edit-si-id")
# ID.send_keys(input("Your ID: "))
ID.send_keys('jjy911018')
PW = driver.find_element_by_css_selector("#edit-si-pwd")
# PW.send_keys(input("Your PW: "))
PW.send_keys('%3gkrsus3qksM')
login = driver.find_element_by_css_selector("#edit-actions--2 > input:nth-child(1)")
login.click()
driver.get('http://libproxy.snu.ac.kr/_Lib_Proxy_Url/www.lexisnexis.com/hottopics/lnacademic/?')
