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
import selenium.webdriver.support.ui
from selenium.webdriver.support import expected_conditions

from logIn import logInToSNU

class WestlawScraper:
  """
	Class for downloading documents w.r.t. patent invalidity in Westlaw database using the Keynumber search.

  URLs below searched Westlaw database using the Keynumbers w.r.t. II. PATENTABILITY AND VALIDITY, k421-k850.
  Jurisdiction is set to be CAFC, and the date is from Oct. 01. 1982 to Feb. 28. 2018.

  The first URL searched subsection A~D(k421~k670), and the second one searched E~F(k671~k850).

  URL:
  1) http://lps3.1.next.westlaw.com.libproxy.snu.ac.kr/Search/Results.html?jurisdiction=CTAF&contentType=CUSTOMDIGEST&querySubmissionGuid=i0ad6ad3a000001625941c6eb3d80e251&tocGuid=I2501c862419b7f95f8720560c638baee&categoryPageUrl=Home%2FWestKeyNumberSystem&searchId=i0ad6ad3a000001625941006af9d8901f&collectionSet=w_cs_cd_toc&transitionType=ListViewType&contextData=(sc.CustomDigest)
  2) http://lps3.1.next.westlaw.com.libproxy.snu.ac.kr/Search/Results.html?jurisdiction=CTAF&contentType=CUSTOMDIGEST&querySubmissionGuid=i0ad6ad3a0000016259442d083d8102b9&tocGuid=I2501c862419b7f95f8720560c638baee&categoryPageUrl=Home%2FWestKeyNumberSystem&searchId=i0ad6ad3a0000016259434b96f9d8910d&collectionSet=w_cs_cd_toc&transitionType=ListViewType&contextData=(sc.CustomDigest)

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

  _RE_STYLESHEET = re.compile(r'\<STYLE TYPE\=\"text\/css\"\>(\<\!\-\-)?(?P<css_string>.+?)(\-\-\>)?\<\/STYLE\>', flags=re.S | re.U | re.I)
  _RE_LEXIS_DOC = re.compile(r'\<DOC NUMBER\=(?P<docid>\d+)\>\s+\<DOCFULL\>(?P<doc>.+?)\<\/DOCFULL\>', flags=re.S | re.U | re.I)

# re.compile(ur ~~~) is the original form. Jay Jung changed it to re.compile(r ~~~)
# _RE_STYLESHEET = re.compile(ur'\<STYLE TYPE\=\"text\/css\"\>(\<\!\-\-)?(?P<css_string>.+?)(\-\-\>)?\<\/STYLE\>', flags=re.S | re.U | re.I)
#  _RE_LEXIS_DOC = re.compile(ur'\<DOC NUMBER\=(?P<docid>\d+)\>\s+\<DOCFULL\>(?P<doc>.+?)\<\/DOCFULL\>', flags=re.S | re.U | re.I)

  def __init__(self, urlWestlaw, wait_timeouts=(15, 1800)):
    """
    Constructs a downloader object.

    :param float,float wait_timeouts: tuple of `(short, long)` where `short` and `long` are the no. of seconds to wait while page elements are loaded (for Webdriver). `long` timeout is used when waiting for LexisNexis to format documents for mass downloads.
    :param  str  url for Westlaw keynumber search. 2 urls stated above.
    """

    self.profile = self.create_browser_profile()
    self._driver = self.get_driver(self.profile)
    # self._driver = selenium.webdriver.Firefox(executable_path = 'C:\Python\Mymodules\PythonCrawler\geckodriver')
    # self._driver.set_window_size(800, 600)
    self._short_wait = selenium.webdriver.support.ui.WebDriverWait(self._driver, wait_timeouts[0], poll_frequency=0.05)
    self._long_wait = selenium.webdriver.support.ui.WebDriverWait(self._driver, wait_timeouts[1], poll_frequency=1)

    self.urlWestlaw = urlWestlaw
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
    loginButton.click()
    return self._driver
  # end of def

  def Westlaw_appears(self, current_handle_or_xpath, isWindow):
        # isWindow = 1: detect whether Westlaw homepage loaded
        #          = 0: detect whether keynumber link loaded, detect whether patent link loaded, detect whether patent-sub link loaded

        def f(driver):
          for handle in driver.window_handles:
            if current_handle_or_xpath != handle:
              driver.switch_to.window(handle)  # switch first to check window title
              if driver.title.endswith('Westlaw'): return True  # this is our new window!/JY:check if the title ends with 'Download Documents'
            #end if
          #end for

          return False # JY: this probably means an error
        #end def

        def g(driver):
          if expected_conditions.visibility_of_any_elements_located((selenium.webdriver.common.by.By.XPATH, current_handle_or_xpath)):
            # keyNumber = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div[1]/ul/li[2]/a').get_attribute('href')
            keyNumber = self._driver.find_element_by_xpath(current_handle_or_xpath).get_attribute('href')
            print(keyNumber)
            return True

          return False
        # end of def

        if isWindow == 1: return f
        else: return g
  # end of def

  def MoveToWestLaw(self):

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
    self._driver.get(keyNumber_patent)

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
    time.sleep(2)
    self.MoveToWestLaw()
    selectSet = ('//*[@id="coid_browseShowCheckboxes"]',           # 0 Specify Content to Search selection box
                 '//*[@id="I57197764642a01705dd361fff15ee4f9"]',   # 1 Selection box A
                 '//*[@id="Idb2f23ddf74a790d1b0699b1c12b6422"]',   # 2 Selection box B
                 '//*[@id="I146adefaf1f3cb67acd36a561222fec5"]',   # 3 Selection box C
                 '//*[@id="Id841cb612743d076ea11140558a11feb"]',   # 4 Selection box D
                 '//*[@id="I7ea157dafea7a8113db636840c9fb6f6"]',   # 5 Selection box E
                 '//*[@id="I049b6daeada85ffe53b43521991c5817"]',   # 6 Selection box F
                 'jurisdictionIdInner',                  # 7 Select Option  //*[@id="jurisdictionIdInner"]
                 '//*[@id="co_fed_CTA"]',                          # 8 Selection box Court of Appeals 이거는 빼야겠다. 날짜도 그냥 포함해서 하고, 나중에 걸러 내는 식으로
                 '//*[@id="co_fed_CTAF"]',                         # 9 Selection box Federal Court
                 '//*[@id="co_jurisdictionSave"]',                 # 10 save
                 '//*[@id="searchButton"]',                        # 11 search botton
                 #'//*[@id="jurisdictionTDBabFpHVnlZV3dfRVF8Um1Wa1pYSmhiQV9FUV9FUQ_EQ_EQLink"]' # 12 expand Federal
                 'jurisdictionTDBabFpHVnlZV3dfRVF8Um1Wa1pYSmhiQV9FUV9FUQ_EQ_EQLink',
                 # '//*[@id="jurisdictionTDBabFpHVnlZV3d2UTNSekxpQnZaaUJCY0hCbFlXeHp8UTNSekxpQnZaaUJCY0hCbFlXeHo_EQLink"]', # 13 expand Ct. of Appeals
                 'jurisdictionTDBabFpHVnlZV3d2UTNSekxpQnZaaUJCY0hCbFlXeHp8UTNSekxpQnZaaUJCY0hCbFlXeHo_EQLink',
                 # '//*[@id="facet_hierarchy_jurisdictionTDBabFpHVnlZV3d2UTNSekxpQnZaaUJCY0hCbFlXeHp8UTNSekxpQnZaaUJCY0hCbFlXeHo_EQ"]', # 14 select FC
                 'facet_hierarchy_jurisdictionTDBabFpHVnlZV3d2UTNSekxpQnZaaUJCY0hCbFlXeHpMMFpsWkdWeVlXd2dRMmx5TGdfRVFfRVF8Um1Wa1pYSmhiQ0JEYVhJdQ_EQ_EQ',
                 'co_dateWidget_date_dropdown_span',    # 15 date setting
                 'All Dates After', # 16 click to set date after a certain day
                 '//*[@id="co_dateWidgetCustomRangeText_date_after"]', # 17 put in the 'certain' day
                 '//*[@id="co_dateWidgetCustomRangeDoneButton_date_after"]', # 18 confirm the date
                 '//*[@id="co_multifacet_selector_2_applyFacetFilter"]', # 19 apply the filter
                 '//*[@id="cobalt_result_headnote_title1"]'             # 20 first document
                 )
    for i in range(2):
      self._wait_for_element(selectSet[0])
      self._driver.find_element_by_xpath(selectSet[0]).click() # Click Specify Content To Search

      # self._wait_for_element(selectSet[1])
      time.sleep(0.5)
      for j in range(1+(2*i),3+(2*i)):
        self._driver.find_element_by_xpath(selectSet[j]).click() # Select Search boxes from A to B
      # end for

      self._driver.find_element_by_id(selectSet[7]).click() # click option
      self._wait_for_element(selectSet[9])
      for k in range(9,11):
        self._driver.find_element_by_xpath(selectSet[k]).click() # Select CoA and FC and save

      # self._wait_for_element(selectSet[11])
      time.sleep(0.5)
      self._driver.find_element_by_xpath(selectSet[11]).click()

      # put in several search options
      # self._long_wait.until(self.Westlaw_appears(selectSet[16], 0))
      time.sleep(20)
      # self._driver.find_element_by_xpath(selectSet[12]).click()
      # self._driver.find_element_by_xpath(selectSet[13]).click()
      # self._driver.find_element_by_id(selectSet[12]).click()
      # print('12')
      # wait_for_page_load(self._driver)
      # self._driver.find_element_by_id(selectSet[13]).click()
      # print('13')
      # wait_for_page_load(self._driver)
      # time.sleep(5)
      # self._driver.find_element_by_id(selectSet[14]).click()
      # # self._long_wait.until(self.Westlaw_appears(selectSet[15], 0))
      # time.sleep(10)
      # self._driver.find_element_by_id(selectSet[15]).click()
      # wait_for_page_load(self._driver)
      # time.sleep(10)
      # self._driver.find_element_by_link_text(selectSet[16]).click()
      # self._driver.find_element_by_xpath(selectSet[17]).click()
      # self._driver.find_element_by_xpath(selectSet[17]).send_keys('1982.10.01')
      # self._driver.find_element_by_xpath(selectSet[18]).click()
      # self._driver.find_element_by_xpath(selectSet[19]).click()
      self._long_wait.until(self.Westlaw_appears(selectSet[20], 0)) # wait until the first search result appears
      firstDocURL = self._driver.find_element_by_xpath(selectSet[20]).get_attribute('href')
      self._driver.get(firstDocURL) # open the first result
      docNumber = 0
      self._driver.send_keys(u'\ue011')
      print(self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[5]/div[1]/div/ul[1]/li[2]/div/span/strong[1]'))
      while docNumber != self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[5]/div[1]/div/ul[1]/li[2]/div/span/strong[1]'):
        docNumber = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[5]/div[1]/div/ul[1]/li[2]/div/span/strong[1]') # current document number
        docTitle = self._driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/h2/span/a').text # current document name
        with open("./"+docTitle+".html", "wb") as f:
          f.write(self._driver.page_source.encode('utf-8')) # download it in html format
        self.driver.find_element_by_xpath('//*[@id="co_documentFooterResultsNavigationNext"]').click # to the next document
      # self._driver.get(firstDocURL)
      # self._sequential_download()
    # end for

    # self._driver.get(self.urlWestlaw)
    time.sleep(100)
    # selenium.webdriver.common.action_chains.ActionChains(self._driver).send_keys('jjy911018').send_keys(u'\ue004').send_keys('?').send_keys(u'\ue006') # 로그인을 위한 코드인데 수정이 필요할 듯. 따로 pyㅠ파일을 만들 생각

    # if not self._have_results(): return []

    # self._sequential_download(start_from)
  # end def

  def _sequential_download(self):

    pass
  # end of def

  def _safe_wait(self, poll_func):
    try: return self._long_wait.until(poll_func)
    except selenium.common.exceptions.TimeoutException: return None
  # end def

  def _wait_for_element(self, xpath, raise_error=True):
    elem = self._safe_wait(expected_conditions.presence_of_element_located((selenium.webdriver.common.by.By.XPATH, xpath)))
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

# log in to the library

# go to Westlaw website

# move to the keynumber search results

# do sequential download(click the first doc, and download html, and then click next doc.)




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
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id