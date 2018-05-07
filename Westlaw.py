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

import csv

class WestlawURLScraper:
  """
  Class for downloading URLs of documents w.r.t. patent invalidity in Westlaw database using the Keynumber search.

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
    self._driver.get('https://lib.snu.ac.kr')
    startLogin = self._driver.find_element_by_css_selector("#top-user-menu-additional > div:nth-child(2) > a:nth-child(1)")
    startLogin.click()
    time.sleep(1)
    ID = self._driver.find_element_by_css_selector("#edit-si-id")
    # ID.send_keys(input("Your ID: "))
    ID.send_keys('jjy911018')
    PW = self._driver.find_element_by_css_selector("#edit-si-pwd")
    # PW.send_keys(input("Your PW: "))
    PW.send_keys('%3gkrsus3qksM')
    loginButton = self._driver.find_element_by_css_selector("#edit-actions--2 > input:nth-child(1)")
    loginButton.click()
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

    SNUXPaths = (
        '/html/body/div[2]/div/div/main/div/div[2]/div/div/div/div/div/div/div[4]/div/div[2]/ul/li[23]',  # W Button
        '/html/body/div[2]/div/div/main/div/div[2]/div/div/div/div/div/div/div[5]/div/div/div/div/div[2]/table/tbody/tr[2]/td[1]/div',  # Westlaw link
        '/html/body/div[5]/div/form/input[4]'  # Confirm direct to Westlaw
        )

    self._wait_for_element(SNUXPaths[0])
    wButton = self._driver.find_element_by_xpath(SNUXPaths[0])
    wButton.click()
    self._wait_for_element(SNUXPaths[1])
    WestlawLink = self._driver.find_element_by_xpath(SNUXPaths[1])
    WestlawLink.click()
    parent_window_handle = self._driver.current_window_handle
    self._wait_for_element(SNUXPaths[2])
    confirmWestlaw = self._driver.find_element_by_xpath(SNUXPaths[2])
    confirmWestlaw.click()
    self._long_wait.until(self.Westlaw_appears(parent_window_handle, 1))

    WestlawXPath = (
        '/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div[1]/ul/li[2]/a',  # keynumber link
        '/html/body/div[1]/div/div[2]/div[3]/div/div/div[2]/div/div/div[3]/ul[3]/li[4]/div/a[1]'  # keynumber-patent link
      )
    # move to keynumber
    self._long_wait.until(self.Westlaw_appears(WestlawXPath[0], 0))
    keyNumber = self._driver.find_element_by_xpath(WestlawXPath[0]).get_attribute('href')
    self._driver.get(keyNumber)

    # move to keynumber-patent
    self._long_wait.until(self.Westlaw_appears(WestlawXPath[1], 0))
    keyNumber_patent = self._driver.find_element_by_xpath(WestlawXPath[1]).get_attribute('href')
    # self._driver.get(keyNumber_patent)
    return keyNumber_patent
   # end of def

  def __del__(self):
    try: self._driver.quit()
    except: pass

  def iter_search_results(self, isABCDEF, , KeyNumberURL, start_from=1):
    """
    A generator function that executes LexisNexis search query on source data CSI (:attr:`csi`), with query :attr:`search_query` and downloads all documents returned by search.
    :param int isABCDEF: 1 to 6(A to F), indicating which subdirectory of Keynumbers to search for. 
    :param str 
    :param int start_from: document index to start downloading from.
    :returns: a tuple `(doc_content, (index, results_count))`, where `doc_content` is the HTML content of the `index`th document, and `results_count` is the number of documents returned by specified search query.
    """
    
    time.sleep(0.5)
    with wait_for_page_load(self._driver) as pl:
      KeyNumberURL = self.MoveToWestLawKeyNumber()

    selectSet = (
        '//*[@id="coid_browseShowCheckboxes"]',           # 0 Specify Content to Search selection box
        '//*[@id="I57197764642a01705dd361fff15ee4f9"]',   # 1 Selection box A
        '//*[@id="Idb2f23ddf74a790d1b0699b1c12b6422"]',   # 2 Selection box B
        '//*[@id="I146adefaf1f3cb67acd36a561222fec5"]',   # 3 Selection box C
        '//*[@id="Id841cb612743d076ea11140558a11feb"]',   # 4 Selection box D
        '//*[@id="I7ea157dafea7a8113db636840c9fb6f6"]',   # 5 Selection box E
        '//*[@id="I049b6daeada85ffe53b43521991c5817"]',   # 6 Selection box F
        'jurisdictionIdInner',                            # 7 Select Option  //*[@id="jurisdictionIdInner"]
        '//*[@id="co_fed_CTAF"]',                         # 8 Selection box Federal Court
        '//*[@id="co_jurisdictionSave"]',                 # 9 save
        '//*[@id="searchButton"]',                        # 10 search botton
        "co_dateWidget_date_dropdown_span",               # 11 date
        "All Dates After",                                # 12 all dates after
        "co_dateWidgetCustomRangeText_date_after",        # 13 date input
        "co_dateWidgetCustomRangeDoneButton_date_after",  # 14 go button
        '//*[@id="cobalt_result_headnote_title1"]',       # 15 first document
        "coid_search_pagination_size_footer",             # 16 document number drop down
        "//option[@value='100']"                          # 17 100 documents
        )
    ABCDEF = ('A', 'B', 'C', 'D', 'E', 'F')
    
    i = isABCDEF
    print('Start downloading URL from the subdirectory ' + ABCDEF[i-1])
    self._driver.get(KeyNumberURL)
    self._wait_for_element(selectSet[0])
    specifyContentTOSearch = self._driver.find_element_by_xpath(selectSet[0])
    if not specifyContentTOSearch.is_selected():
      self._driver.find_element_by_xpath(selectSet[0]).click()  # Click Specify Content To Search

    time.sleep(0.5)
    self._driver.execute_script('window.scrollBy(0,250)', '')
    self._driver.find_element_by_xpath(selectSet[i]).click()  # Select Search boxes from A to F according to i
    FCOption = self._driver.find_element_by_xpath('//*[@id="jurisdictionIdInner"]')
    if not FCOption.text == 'Federal Circuit':
      self._driver.find_element_by_id(selectSet[7]).click()  # click option
      self._wait_for_element(selectSet[8])
      for k in range(8,10):
        self._driver.find_element_by_xpath(selectSet[k]).click()  # Select FC and save
      time.sleep(1)
    # print('waiting to click the search button')
    # self._short_wait.until(
    #   expected_conditions.invisibility_of_element_located((By.XPATH, selectSet[8]))  # wait until the save button to disappear
    #   )

    with wait_for_page_load(self._driver) as pl:
      self._driver.find_element_by_xpath(selectSet[10]).click()  # click search button and wait for the results to appear
      print('waiting for search results to appear')

    with wait_for_page_load(self._driver) as pl:
      print('waiting for data to appear')
      self._long_wait.until(self.Westlaw_appears(selectSet[15], 0))  # wait for date to appear
      self._driver.execute_script('window.scrollBy(0,250)', '')
      self._driver.find_element_by_id(selectSet[11]).click()
      self._driver.find_element_by_link_text(selectSet[12]).click()
      self._driver.find_element_by_id(selectSet[13]).clear()
      self._driver.find_element_by_id(selectSet[13]).send_keys("1982.10.01")
      self._driver.find_element_by_id(selectSet[14]).click()

    self._long_wait.until(self.Westlaw_appears(selectSet[15], 0)) # wait until the first search result appears
    
    p = re.compile('\(|\)|\,')
    totalDocNumber = int(p.sub('', self._driver.find_element_by_xpath('//span[@class="co_search_titleCount"]').text))  # total document number
    print(totalDocNumber)

    with wait_for_page_load(self._driver) as pl:
      self._driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')  # scroll down to the bottom to change the number of documents in one page
      self._driver.find_element_by_id(selectSet[16]).click()
      self._driver.find_element_by_xpath(selectSet[17]).click()

    docURLsTMP = []
    docRanksTMP = []
    docDateTMP = []
    docCiteTMP = []
    for j in range(int(totalDocNumber)//100 + 1):
      if j:
        self._driver.find_element_by_xpath('//a[@id = "co_search_header_pagination_next"]').click()
      self._long_wait.until(self.Westlaw_appears('//span[@class="co_search_titleCount"]', 0))  
      print(j)
      for k in self._driver.find_elements_by_xpath('//div[@class="co_searchContent"]/h3/a'):
        docURLsTMP.append(k.get_attribute('href'))
        docRanksTMP.append(int(k.get_attribute('rank')))
      for k in self._driver.find_elements_by_xpath('//div[@class="co_searchContent"]/div[@class = "co_searchResults_citation"]/span[1]'):
        docDateTMP.append(k.text)
      for k in self._driver.find_elements_by_xpath('//div[@class="co_searchContent"]/div[@class = "co_searchResults_citation"]/span[2]'):  
        docCiteTMP.append(k.text)
      zipped = zip(docRanksTMP, docDateTMP, docCiteTMP, docURLsTMP)
      print(zipped)
      with open('docURL_Ver'+str(isABCDEF)+'.csv', 'a', encoding='utf-8', newline='') as f:
        wr = csv.writer(f)
        for l in zipped:
          wr.writerow(l)
      del docURLsTMP[:]  # clear docURLsTMP
      del docRanksTMP[:]  # clear docRanksTMP
      
  #   for k in range(totalDocNumber):
  #     print('k is '+str(k))
  #     self._driver.execute_script('window.scrollTo(0,0);') # scroll to top left corner
  #     nextDocButtonXpath = '//*[@id="co_documentFooterResultsNavigationNext"]'
  #     self._wait_for_element(nextDocButtonXpath)
  #     if self._driver.find_element_by_xpath('//*[@id="courtline"]').text == 'United States Court of Appeals, Federal Circuit.':
  #       q1 = re.compile("[0-9]{4}") # get **** (**** can be any number)
  #       q2 = re.compile("[a-zA-Z]*")      # get month name
  #       m1 = q1.search(self._driver.find_element_by_xpath('//*[@id="filedate"]').text)
  #       m2 = q2.search(self._driver.find_element_by_xpath('//*[@id="filedate"]').text)

  #       if (int(m1.group()) > 1982)|((m1.group() == 1982) & (m2.group() in ('October', 'November', 'December'))):
  #         docTitle = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/h2/span/a').text # current document name
  #         citationCode = self._driver.find_element_by_xpath('//*[@id="cite0"]').text # current citation code
  #         print(docTitle)
  #         self._driver.execute_script('window.scrollTo(0,0);')
  #         # self._long_wait.until(self.Westlaw_appears('/html/body/div[1]/div/div[2]/div[2]/div/div/div[5]/div/div[2]/div/div[5]/div[1]/span',0))
  #         # docketNumber = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[5]/div/div[2]/div/div[5]/div[1]/span').text
  #         # plaintiffNameOR = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[5]/div/div[2]/div/div[5]/div/div[1]').text
  #         # plaintiffName = plaintiffNameOR[:len(plaintiffNameOR)-len(', Plaintiff–Appellee,')]
  #         # defendantNameOR = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[5]/div/div[2]/div/div[5]/div/div[3]').text
  #         # defendantName = defendantNameOR[:len(defendantNameOR) - len(', Defendant–Appellant.')]
  #         # self.tmp = ((i, k), docTitle, citationCode, docketNumber, plaintiffName, defendantName)
  #         # self.ResultsSet.add(self.tmp)
  #         if i == 0:
  #           with open("./WestlawHTMLAB/"+citationCode+".html", "wb") as f:
  #             f.write(self._driver.page_source.encode('utf-8')) # download it in html format
  #         elif i == 1:
  #           with open("./WestlawHTMLCD/"+citationCode+".html", "wb") as f:
  #             f.write(self._driver.page_source.encode('utf-8')) # download it in html format
  #         else:
  #           with open("./WestlawHTMLEF/"+citationCode+".html", "wb") as f:
  #             f.write(self._driver.page_source.encode('utf-8')) # download it in html format
  #         # end if
  #       # end if
  #     # end if
  #   # end for
  #     with wait_for_page_load(self._driver) as pl:
  #       self._driver.find_element_by_xpath(nextDocButtonXpath).click()
  #       pl
  # # end def

  def _get_additional_info(self, ):
    pass
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