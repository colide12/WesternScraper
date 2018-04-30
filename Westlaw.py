import random
import re
import requests
import time
import os

import urllib.request, urllib.parse, urllib.error
from urllib.parse import urlparse

import selenium.common.exceptions
import selenium.webdriver.common.action_chains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import selenium.webdriver.common.desired_capabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

class WestlawScraper:
  """
	Class for downloading documents w.r.t. patent invalidity in Westlaw database using the Keynumber search.

  Example(Should be changed)::

      downloader = WestlawScraper(mass_download_mode=True)
      for (content, (doc_index, doc_count)) in downloader.iter_search_results(6318, 'DATE(=1987)'):
        print doc_id

  This code uses `Geckodriver`__ and `Selenium Webdriver <http://www.seleniumhq.org/>`__ to scrape Westlaw pages.
  """

  if os.name == 'nt':
      DOWNLOAD_DIR = "C:"+os.environ['HOMEPATH']+"\\Downloads"
      HISTORY_DIR = "\\Shepards"
      SOURCE_DIR = "\\Sources"
  else:
      DOWNLOAD_DIR = os.environ['HOME']+"/Downloads"
      HISTORY_DIR = "/Shepards/"
      SOURCE_DIR = "/Sources/"
  VERSION_NUM = "1.3.20"
  editor_abbreviation = None
  author_abbreviation = None

  def __init__(self, wait_timeouts=(15, 1800)):
    """
    Constructs a downloader object.

    :param  str  url for Westlaw keynumber search. 2 urls stated above.
    :param float,float wait_timeouts: tuple of `(short, long)` where `short` and `long` are the no. of seconds to wait while page elements are loaded (for Webdriver). `long` timeout is used when waiting for LexisNexis to format documents for mass downloads.

    """

    self.profile = self.create_browser_profile()
    self._driver = self.get_driver(self.profile)
    # self._driver = selenium.webdriver.Firefox(executable_path = 'C:\Python\Mymodules\PythonCrawler\geckodriver')
    # self._driver.set_window_size(800, 600)
    self._short_wait = WebDriverWait(self._driver, wait_timeouts[0], poll_frequency=0.05)
    self._long_wait = WebDriverWait(self._driver, wait_timeouts[1], poll_frequency=1)
    self.ResultsSet = set()
  # end def

  def logInToSNU(self):
    # self._driver = selenium.webdriver.Firefox(executable_path = 'C:\Python\Mymodules\PythonCrawler\geckodriver')
    self._driver.get('https://lib.snu.ac.kr')
    startLogin = self._driver.find_element_by_css_selector("#top-user-menu-additional > div:nth-child(2) > a:nth-child(1)")
    startLogin.click()
    time.sleep(1) # expected_conditions 코드를 사용하면 좀 더 최적화 가능, 그런데 왜인지 모르겠지만 is not reachable by keyboard
    ID = self._driver.find_element_by_css_selector("#edit-si-id")
    # ID.send_keys(input("Your ID: "))
    ID.send_keys('jjy911018')
    PW = self._driver.find_element_by_css_selector("#edit-si-pwd")
    # PW.send_keys(input("Your PW: "))
    PW.send_keys('%3gkrsus3qksM')
    loginButton = self._driver.find_element_by_css_selector("#edit-actions--2 > input:nth-child(1)")
    loginButton.submit()
    return self._driver
  # end of def

  def Westlaw_appears(self, current_handle_or_xpath, isWindow):
        # isWindow = 1: detect whether Wes tlaw homepage loaded
        #          = 0: detect whether keynumber link loaded
    def f(driver): # self._driver(blur~)라서 앞의 _driver에서 가져 오는 듯
      for handle in driver.window_handles:
        if current_handle_or_xpath != handle:
          driver.switch_to.window(handle)  # switch first to check window title
          if driver.title.endswith('Westlaw'): return True  # this is our new window!/JY:check if the title ends with 'Download Documents'
        #end if
      #end for
      return False # JY: as Westlaw_appears is an input for wait_for, False will make python wait.
    #end def

    def g(driver): # 사실 이게 wait_for나 page_loaded랑 같은 건데
      if expected_conditions.visibility_of_any_elements_located((selenium.webdriver.common.by.By.XPATH, current_handle_or_xpath)):
        keyNumber = driver.find_element_by_xpath(current_handle_or_xpath).get_attribute('href')
        return True
      return False
    # end of def

    if isWindow == 1: return f
    else: return g
  # end of def

  def MoveToWestLawKeyNumber(self): # 이거 둘로 쪼개야겠다. lib2westlaw + westlaw2westlaw

    # move to academic DB in SNU library
    self._driver.get('http://library.snu.ac.kr/find/databases')

    # move to Westlaw main page
    self._wait_for_element('/html/body/div[2]/div/div/main/div/div[2]/div/div/div/div/div/div/div[4]/div/div[2]/ul/li[23]')
    wButton = self._driver.find_element_by_xpath('/html/body/div[2]/div/div/main/div/div[2]/div/div/div/div/div/div/div[4]/div/div[2]/ul/li[23]')
    wButton.click()
    self._wait_for_element('/html/body/div[2]/div/div/main/div/div[2]/div/div/div/div/div/div/div[5]/div/div/div/div/div[2]/table/tbody/tr[2]/td[1]/div')
    goToWestlaw = self._driver.find_element_by_xpath('/html/body/div[2]/div/div/main/div/div[2]/div/div/div/div/div/div/div[5]/div/div/div/div/div[2]/table/tbody/tr[2]/td[1]/div')
    goToWestlaw.click()
    parent_window_handle = self._driver.current_window_handle
    self._wait_for_element('/html/body/div[5]/div/form/input[4]')
    confirmWestlaw = self._driver.find_element_by_xpath('/html/body/div[5]/div/form/input[4]')
    confirmWestlaw.click()
    self._long_wait.until(self.Westlaw_appears(parent_window_handle, 1))

    # move to keynumber
    self._long_wait.until(self.Westlaw_appears('/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div[1]/ul/li[2]/a', 0))
    keyNumber = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div[1]/ul/li[2]/a').get_attribute('href')
    self._driver.get(keyNumber)

    # move to keynumber-patent
    self._long_wait.until(self.Westlaw_appears('/html/body/div[1]/div/div[2]/div[3]/div/div/div[2]/div/div/div[3]/ul[3]/li[4]/div/a[1]', 0))
    keyNumber_patent = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[3]/div/div/div[2]/div/div/div[3]/ul[3]/li[4]/div/a[1]').get_attribute('href')
    # self._driver.get(keyNumber_patent)
    return keyNumber_patent
    # # move to invalidation cases
    # self._long_wait.until(Westlaw_appears('/html/body/div[1]/div/div[2]/div[3]/div/div/div[2]/div/div/div[2]/div[2]/div/a', 0))
    # keyNumber_patent_invalidation = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[3]/div/div/div[2]/div/div/div[2]/div[2]/div/a').get_attribute('href')
    # self._driver.get(keyNumber_patent_invalidation)

   # end of def

  def __del__(self):
    try: self._driver.quit()
    except: pass

  def iter_search_results(self, start_from=1):
    """
    A generator function that executes LexisNexis search query on source data CSI (:attr:`csi`), with query :attr:`search_query` and downloads all documents returned by search.
    :param str url:
    :param int start_from: document index to start downloading from.
    :returns: a tuple `(doc_content, (index, results_count))`, where `doc_content` is the HTML content of the `index`th document, and `results_count` is the number of documents returned by specified search query.
    """
    self.logInToSNU()
    time.sleep(0.5)
    with wait_for_page_load(self._driver) as pl:
      KeyNumberURL = self.MoveToWestLawKeyNumber()
    selectSet = ('//*[@id="coid_browseShowCheckboxes"]',           # 0 Specify Content to Search selection box
                 '//*[@id="I57197764642a01705dd361fff15ee4f9"]',   # 1 Selection box A
                 '//*[@id="Idb2f23ddf74a790d1b0699b1c12b6422"]',   # 2 Selection box B
                 '//*[@id="I146adefaf1f3cb67acd36a561222fec5"]',   # 3 Selection box C
                 '//*[@id="Id841cb612743d076ea11140558a11feb"]',   # 4 Selection box D
                 '//*[@id="I7ea157dafea7a8113db636840c9fb6f6"]',   # 5 Selection box E
                 '//*[@id="I049b6daeada85ffe53b43521991c5817"]',   # 6 Selection box F
                 'jurisdictionIdInner',                            # 7 Select Option  //*[@id="jurisdictionIdInner"]
                 '//*[@id="co_fed_CTA"]',                          # 8 Selection box Court of Appeals 이거는 빼야겠다. 날짜도 그냥 포함해서 하고, 나중에 걸러 내는 식으로
                 '//*[@id="co_fed_CTAF"]',                         # 9 Selection box Federal Court
                 '//*[@id="co_jurisdictionSave"]',                 # 10 save
                 '//*[@id="searchButton"]',                        # 11 search botton
                 '//*[@id="co_dateWidget_date_dropdown_span"]',     # 12 date
                 '/html/body/div[1]/div/div[2]/div[3]/div[3]/div/div/div[1]/div[1]/div[2]/div[5]/div/div[3]/div/div/ul[2]/li[2]/a',   # 13 all dates after
                 '//*[@id="co_dateWidgetCustomRangeText_date_after"]' ,       # 14 date input
                 '//*[@id="co_dateWidgetCustomRangeDoneButton_date_before"]' , # 15 go button
                 '//*[@id="cobalt_result_headnote_title1"]'        # 16 first document
                 )
    for i in range(3):
      print('i is '+str(i))
      self._driver.get(KeyNumberURL)
      self._wait_for_element(selectSet[0])
      specifyContentTOSearch = self._driver.find_element_by_xpath(selectSet[0])
      if not specifyContentTOSearch.is_selected():
        self._driver.find_element_by_xpath(selectSet[0]).click() # Click Specify Content To Search

      time.sleep(0.5)
      self._driver.execute_script('window.scrollBy(0,250)', '')
      for j in range(1+(2*i),3+(2*i)):
        self._driver.find_element_by_xpath(selectSet[j]).click() # Select Search boxes from A to B
      # end for
      if not i: # for CDEF, skip setting jurisdiction
        self._driver.find_element_by_id(selectSet[7]).click() # click option
        self._wait_for_element(selectSet[9])
        for k in range(9,11):
          self._driver.find_element_by_xpath(selectSet[k]).click() # Select CoA and FC and save
      time.sleep(0.5)
      self._short_wait.until_not(
        expected_conditions.element_to_be_clickable((selenium.webdriver.common.by.By.XPATH, selectSet[10]))
        )

      with wait_for_page_load(self._driver) as pl:
        self._driver.find_element_by_xpath(selectSet[11]).click() #click search button and wait for the results to appear

      with wait_for_page_load(self._driver) as pl:
        self._long_wait.until(self.Westlaw_appears(selectSet[12], 0)) # wait for date to appear
        self._driver.execute_script('window.scrollBy(0,250)', '')
        self._driver.find_element_by_id("co_dateWidget_date_dropdown_span").click()
        self._driver.find_element_by_link_text("All Dates After").click()
        self._driver.find_element_by_id("co_dateWidgetCustomRangeText_date_after").clear()
        self._driver.find_element_by_id("co_dateWidgetCustomRangeText_date_after").send_keys("1982.10.01")
        self._driver.find_element_by_id("co_dateWidgetCustomRangeDoneButton_date_after").click()

      self._long_wait.until(self.Westlaw_appears(selectSet[16], 0)) # wait until the first search result appears
      p = re.compile('\(|\)|\,')
      totalDocNumber = int(p.sub('', self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[5]/div[1]/h1/span').text)) # total document number
      firstDocURL = self._driver.find_element_by_xpath(selectSet[16]).get_attribute('href')
      self._driver.get(firstDocURL) # open the first result

      for k in range(totalDocNumber):
        print('k is '+str(k))
        self._driver.execute_script('window.scrollTo(0,0);') # scroll to top left corner
        nextDocButtonXpath = '//*[@id="co_documentFooterResultsNavigationNext"]'
        self._wait_for_element(nextDocButtonXpath)
        if self._driver.find_element_by_xpath('//*[@id="courtline"]').text == 'United States Court of Appeals, Federal Circuit.':
          q1 = re.compile("[0-9]{4}") # get **** (**** can be any number)
          q2 = re.compile("[a-zA-Z]*")      # get month name
          m1 = q1.search(self._driver.find_element_by_xpath('//*[@id="filedate"]').text)
          m2 = q2.search(self._driver.find_element_by_xpath('//*[@id="filedate"]').text)

          if (int(m1.group()) > 1982)|((m1.group() == 1982) & (m2.group() in ('October', 'November', 'December'))):
            docTitle = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/h2/span/a').text # current document name
            citationCode = self._driver.find_element_by_xpath('//*[@id="cite0"]').text # current citation code
            print(docTitle)
            self._driver.execute_script('window.scrollTo(0,0);')
            # self._wait_for_element('/html/body/div[1]/div/div[2]/div[2]/div/div/div[5]/div/div[2]/div/div[5]/div[1]/span')
            docketNumber = self._driver.find_element_by_xpath('//div[@class="co_contentBlock co_briefItState co_docketBlock"]/span').text
            plaintiffDefendant = self._driver.find_element_by_xpath('//div[@class="co_suit"]').text
            print(plaintiffDefendant)
            plaintiffNameOR = plaintiffDefendant[0]
            plaintiffName = plaintiffNameOR[:len(plaintiffNameOR)-len(', Plaintiff–Appellee,')]
            print(plaintiffName)
            defendantNameOR = plaintiffDefendant[1]
            defendantName = defendantNameOR[:len(defendantNameOR) - len(', Defendant–Appellant.')]
            print(defendantName)
            self.tmp = ((i, k), docTitle, citationCode, docketNumber, plaintiffName, defendantName)
            self.ResultsSet.add(self.tmp)
            if i == 0:
              with open("./WestlawHTMLAB/"+citationCode+".html", "wb") as f:
                f.write(self._driver.page_source.encode('utf-8')) # download it in html format
            elif i == 1:
              with open("./WestlawHTMLCD/"+citationCode+".html", "wb") as f:
                f.write(self._driver.page_source.encode('utf-8')) # download it in html format
            else:
              with open("./WestlawHTMLEF/"+citationCode+".html", "wb") as f:
                f.write(self._driver.page_source.encode('utf-8')) # download it in html format
            # end if
          # end if
        # end if
      # end for
        with wait_for_page_load(self._driver) as pl:
          self._driver.find_element_by_xpath(nextDocButtonXpath).click()
          pl
    # end for
  # end def

  def _safe_wait(self, poll_func):
    try: return self._long_wait.until(poll_func)
    except selenium.common.exceptions.TimeoutException: return None
  # end def

  def _wait_for_element(self, xpath, raise_error=True):
    elem = self._safe_wait(expected_conditions.visibility_of_any_elements_located((selenium.webdriver.common.by.By.XPATH, xpath)))
    if raise_error and elem is None: raise selenium.common.exceptions.TimeoutException(msg='XPath \'{}\' presence wait timeout.'.format(xpath))
    return elem

  def get_driver(self, profile):
    # get firefox driver (start firefox)
    # using profile created in create_browser_profile()

    self._driver = webdriver.Firefox(firefox_profile=profile)
    return self._driver

  def create_browser_profile(self):
    # change profile to remove download dialog box
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 0) # custom location
    profile.set_preference('browser.download.manager.useWindow', False)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', self.DOWNLOAD_DIR)
    profile.set_preference('browser.download.manager.focusWhenStarting', False)
    profile.set_preference('browser.helperApps.alwaysAsk.force', False)
    profile.set_preference('services.sync.prefs.sync.browser.download.manager.showWhenStarting', False)
    profile.set_preference('pdfjs.disabled', True)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')

    return profile


class wait_for_page_load(object):

    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
      self.old_page = self.browser.find_element_by_tag_name('html')

    def __exit__(self, *_):
        self.wait_for(self.page_has_loaded)

    def wait_for(self, condition_function):
        import time

        start_time = time.time()
        while time.time() < start_time + 100:
            if condition_function():
                return True
            else:
                time.sleep(0.1)
        raise Exception(
            'Timeout waiting for {}'.format(condition_function.__name__)
        )

    def page_has_loaded(self):
      try:
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id
      except:
        print('No html dected yet')
        return False