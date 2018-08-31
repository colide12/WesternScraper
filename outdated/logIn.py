# logIn.py: Before running the crawler, this file let you log in to your SNU library.

# 아이디/비밀번호를 입력해준다.
import selenium.common.exceptions
import selenium.webdriver.common.action_chains
import selenium.webdriver.common.desired_capabilities
import selenium.webdriver.support.ui
import time

def logInToSNU():
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
	loginButton = driver.find_element_by_css_selector("#edit-actions--2 > input:nth-child(1)")
	loginButton.click()

