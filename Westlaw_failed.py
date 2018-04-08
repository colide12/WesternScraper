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

from logIn import logInToSNU
import time

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

  _RE_STYLESHEET = re.compile(r'\<STYLE TYPE\=\"text\/css\"\>(\<\!\-\-)?(?P<css_string>.+?)(\-\-\>)?\<\/STYLE\>', flags=re.S | re.U | re.I)
  _RE_LEXIS_DOC = re.compile(r'\<DOC NUMBER\=(?P<docid>\d+)\>\s+\<DOCFULL\>(?P<doc>.+?)\<\/DOCFULL\>', flags=re.S | re.U | re.I)

# re.compile(ur ~~~) is the original form. Jay Jung changed it to re.compile(r ~~~)
# _RE_STYLESHEET = re.compile(ur'\<STYLE TYPE\=\"text\/css\"\>(\<\!\-\-)?(?P<css_string>.+?)(\-\-\>)?\<\/STYLE\>', flags=re.S | re.U | re.I)
#  _RE_LEXIS_DOC = re.compile(ur'\<DOC NUMBER\=(?P<docid>\d+)\>\s+\<DOCFULL\>(?P<doc>.+?)\<\/DOCFULL\>', flags=re.S | re.U | re.I)

  def __init__(self, wait_timeouts=(15, 1800), documents_per_download=(250, 500), user_agent_string='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0', mass_download_mode=False):
    """
    Constructs a downloader object.

    :param float,float wait_timeouts: tuple of `(short, long)` where `short` and `long` are the no. of seconds to wait while page elements are loaded (for Webdriver). `long` timeout is used when waiting for LexisNexis to format documents for mass downloads.
    :param int,int documents_per_download: a range specifying the number of documents to download each time when using :attr:`mass_download_mode`.
    :param str user_agent_string: the user agent string that PhantomJS should declare itself to be.
    :param bool mass_download_mode: whether to mass download articles using the download link or page through each document one by one and download.
    """

    self._USER_AGENT_STRING = user_agent_string
    self._DOCUMENTS_PER_DOWNLOAD = documents_per_download

    # desired_capabilities = dict(selenium.webdriver.common.desired_capabilities.DesiredCapabilities.PHANTOMJS)
    # desired_capabilities['phantomjs.page.settings.userAgent'] = self._USER_AGENT_STRING

    self._driver = selenium.webdriver.Firefox(executable_path = 'C:\Python\Mymodules\PythonCrawler\geckodriver')
    # self._driver.set_window_size(800, 600)

    self._short_wait = selenium.webdriver.support.ui.WebDriverWait(self._driver, wait_timeouts[0], poll_frequency=0.05)
    self._long_wait = selenium.webdriver.support.ui.WebDriverWait(self._driver, wait_timeouts[1], poll_frequency=1)

    self.mass_download_mode_ = mass_download_mode

  #end def

  def logInToSNU(self):
    # self._driver = selenium.webdriver.Firefox(executable_path = 'C:\Python\Mymodules\PythonCrawler\geckodriver')
    self._driver.get('http://lib.snu.ac.kr')
    startLogin = self._driver.find_element_by_css_selector("#top-user-menu-additional > div:nth-child(2) > a:nth-child(1)")
    startLogin.click()
    time.sleep(2) # expected_conditions 코드를 사용하면 좀 더 최적화 가능
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

  def __del__(self):
    try: self._driver.quit()
    except: pass

  def iter_search_results(self, csi, search_query, start_from=1):
    """
    A generator function that executes LexisNexis search query on source data CSI (:attr:`csi`), with query :attr:`search_query` and downloads all documents returned by search.

    :param str csi: LexisNexis CSI (see `<http://amdev.net/rpt_download.php>`_ for full list). e.g. Federal Circuit - US Court of Appeals Cases(csi = 6396)
    :param str search_query: execute search query string.
    :param int start_from: document index to start downloading from.
    :returns: a tuple `(doc_content, (index, results_count))`, where `doc_content` is the HTML content of the `index`th document, and `results_count` is the number of documents returned by specified search query.
    """
    self.logInToSNU()
    time.sleep(2)
    self._driver.get('http://libproxy.snu.ac.kr/_Lib_Proxy_Url/www.lexisnexis.com/hottopics/lnacademic/?' + urllib.parse.urlencode({'verb': 'sr', 'csi': csi, 'sr': search_query}))
    # selenium.webdriver.common.action_chains.ActionChains(self._driver).send_keys('jjy911018').send_keys(u'\ue004').send_keys('?').send_keys(u'\ue006') # 로그인을 위한 코드인데 수정이 필요할 듯. 따로 pyㅠ파일을 만들 생각

    if not self._have_results(): return []

    if self.mass_download_mode_: return self._mass_download(start_from)
    return self._sequential_download(start_from)
  #end def

  def _have_results(self):  # todo: kinda slow, due to having wait for multiple timeouts
    self._switch_to_frame('main')
    if self._wait_for_element('//td[text()[contains(., \'No Documents Found\')]]', raise_error=False) is not None: return False
    if self._wait_for_element('//frame[@title=\'Results Content Frame\']', raise_error=False) is not None: return True
    if self._wait_for_element('//frame[@title=\'Results Document Content Frame\']', raise_error=False) is not None: return True

    raise Exception('Page loaded improperly while checking for results frame.')
  #end def

  def _mass_download(self, start_from=1):  # Returns documents as a list of strings containing HTML
    self._switch_to_frame('navigation')

    try:
        documents_count = int(self._driver.find_element_by_xpath('//form[@name=\'results_docview_DocumentForm\']/input[@name=\'totalDocsInResult\']').get_attribute('value'))
        # print(documents_count)
    except: documents_count = -1

    def download_sequence(start, end):
      docs_left = end - start + 1
      cur = start
      while docs_left > self._DOCUMENTS_PER_DOWNLOAD[1]:
        download_count = random.randint(*self._DOCUMENTS_PER_DOWNLOAD)
        yield (cur, cur + download_count - 1)
        docs_left -= download_count
        cur += download_count
      #end while

      yield (cur, cur + docs_left - 1)
    #end def

    def lexis_nexis_download_window_appears(current_handle):
      def f(driver):
        for handle in driver.window_handles:
          if current_handle != handle:
            driver.switch_to.window(handle)  # switch first to check window title
            if driver.title.endswith('Download Documents'): return True  # this is our new window!/JY:check if the title ends with 'Download Documents'
          #end if
        #end for

        return False # JY: this probably means an error
      #end def

      return f
    #end class

    for download_start, download_end in download_sequence(start_from, documents_count):
      self._switch_to_frame('navigation')

      parent_window_handle = self._driver.current_window_handle

      # check for download icon and click it
      self._wait_for_element('//img[@title=\'Download Documents\']').click()

      # wait for download window to appear
      self._short_wait.until(lexis_nexis_download_window_appears(parent_window_handle))
      self._wait_for_element('//img[@title=\'Download\']')

      # get all the form items
      selenium.webdriver.support.ui.Select(self._driver.find_element_by_xpath('//select[@name=\'delFmt\']')).select_by_value('QDS_EF_HTML')
      selenium.webdriver.support.ui.Select(self._driver.find_element_by_xpath('//select[@name=\'delView\']')).select_by_value('GNBFI')
      selenium.webdriver.support.ui.Select(self._driver.find_element_by_xpath('//select[@name=\'delFontType\']')).select_by_value('COURIER')  # i like courier

      search_term_bold = self._driver.find_element_by_xpath('//input[@type=\'checkbox\'][@id=\'termBold\']')
      if not search_term_bold.is_selected(): search_term_bold.click()
      doc_new_page = self._driver.find_element_by_xpath('//input[@type=\'checkbox\'][@id=\'docnewpg\']')
      if not doc_new_page.is_selected(): doc_new_page.click()

      self._driver.find_element_by_xpath('//input[@type=\'radio\'][@id=\'sel\']').click()
      self._driver.find_element_by_xpath('//input[@type=\'text\'][@id=\'rangetextbox\']').send_keys('{}-{}'.format(download_start, download_end))

      self._driver.find_element_by_xpath('//img[@title=\'Download\']').click()

      download_url = self._long_wait.until(expected_conditions.presence_of_element_located((selenium.webdriver.common.by.By.XPATH, '//center[@class=\'suspendbox\']/p/a'))).get_attribute('href')

      # set up cookies and use requests library to do download
      cookies = dict([(cookie['name'], cookie['value']) for cookie in self._driver.get_cookies()])
      response = requests.get(download_url, cookies=cookies, headers={'User-Agent': self._USER_AGENT_STRING})
      html_content = response.text

      m = self._RE_STYLESHEET.search(html_content)  # JY: If we find any string matches _RE_STYLESHEET from html_content return match object.
      css_string = m.group('css_string').strip()  # JY: .strip erases white spaces before, and after the grouped string.
      # _RE_STYLESHEET = re.compile(r'\<STYLE TYPE\=\"text\/css\"\>(\<\!\-\-)?(?P<css_string>.+?)(\-\-\>)?\<\/STYLE\>', flags=re.S | re.U | re.I)
      # _RE_LEXIS_DOC = re.compile(r'\<DOC NUMBER\=(?P<docid>\d+)\>\s+\<DOCFULL\>(?P<doc>.+?)\<\/DOCFULL\>', flags=re.S | re.U | re.I)


      for i, m in enumerate(self._RE_LEXIS_DOC.finditer(html_content)):
        page_content = m.group('doc').replace('<!-- Hide XML section from browser', '').replace('-->', '').strip()
        page_content = '\n'.join(['<HTML>', '<HEAD>', '<STYLE TYPE=\"text/css\">', css_string, '</STYLE>', '</HEAD>', '<BODY>', page_content, '</BODY>', '</HTML>'])

        yield (page_content, (download_start + i, documents_count))
      #end for

      self._driver.close()
      self._driver.switch_to.window(parent_window_handle)
    #end for
  #end def

  def _sequential_download(self, start_from=1):
    self._switch_to_frame('navigation')
    try: documents_count = int(self._driver.find_element_by_xpath('//form[@name=\'results_docview_DocumentForm\']/input[@name=\'totalDocsInResult\']').get_attribute('value'))
    except: documents_count = -1
    if documents_count <= 0: return

    if start_from > documents_count: return

    if documents_count == 1:
      self._switch_to_frame('content')
      page_content = self._driver.page_source # this line of code gets all the html content of the page
      yield (page_content, (1, 1))
      return
    #end if

    self._switch_to_frame('results')  # go to results list and grab the first link
    first_document_url = self._wait_for_element('//td/a[contains(@href, \'/lnacui2api/results/docview/docview.do\')]').get_attribute('href')

    url_obj = urlparse.urlparse(first_document_url)
    qs_dict = dict(urlparse.parse_qsl(url_obj.query))
    qs_dict['docNo'] = start_from # url에 docNo라는 항목이 있어서  search result에서 몇 번째인지 나옴
    doc_url = urlparse.urlunparse((url_obj.scheme, url_obj.netloc, url_obj.path, url_obj.params, urllib.parse.urlencode(qs_dict), url_obj.fragment))
    self._driver.get(doc_url)  # jump to the page we want

    # qs_dict['RELEVANCE'] = 'BOOLEAN'  # doesnt seem to work
    # http://www.lexisnexis.com/lnacui2api/results/docview/docview.do?docLinkInd=true&risb=21_T21153102977&format=GNBFI&sort=RELEVANCE&startDocNo=1&resultsUrlKey=29_T21153102981&cisb=22_T21153102980&treeMax=true&treeWidth=0&csi=6318&docNo=1

    for doc_index in range(start_from, documents_count + 1):
      self._switch_to_frame('content', in_iframe=False)
      page_content = self._driver.page_source
      yield (page_content, (doc_index, documents_count))

      self._switch_to_frame('navigation', in_iframe=False)
      next_page_elem = self._wait_for_element('//img[@title=\'View next document\']', raise_error=False)
      if next_page_elem is None:
        if doc_index != documents_count:
          raise Exception('Next page icon could not be found: doc_index={}, documents_count={}'.format(doc_index, documents_count))
      else: next_page_elem.click()
    #end while
  #end def

  def _switch_to_frame(self, frame_name, in_iframe=True):
    self._driver.switch_to.default_content() # this command initializes the frame you are in.

    if in_iframe:
      frame = self._safe_wait(expected_conditions.frame_to_be_available_and_switch_to_it('mainFrame'))
      if not frame: raise SwitchFrameException(frame_name)
    #end if

    try:
      if frame_name == 'main': return frame
      elif frame_name == 'results': frame = self._wait_for_element('//frame[@title=\'Results Content Frame\']')
      elif frame_name == 'navigation': frame = self._wait_for_element('//frame[@title=\'Results Navigation Frame\']')
      elif frame_name == 'content': frame = self._wait_for_element('//frame[@title=\'Results Document Content Frame\']')
    except selenium.common.exceptions.TimeoutException:
      raise SwitchFrameException(frame_name)

    self._safe_wait(expected_conditions.frame_to_be_available_and_switch_to_it(frame))

    return frame
  #end def

  def _safe_wait(self, poll_func):
    try: return self._short_wait.until(poll_func)
    except selenium.common.exceptions.TimeoutException: return None
  #end def

  def _wait_for_element(self, xpath, raise_error=True):
    elem = self._safe_wait(expected_conditions.presence_of_element_located((selenium.webdriver.common.by.By.XPATH, xpath)))
    if raise_error and elem is None: raise selenium.common.exceptions.TimeoutException(msg='XPath \'{}\' presence wait timeout.'.format(xpath))
    return elem
  #end def
#end class


class SwitchFrameException(Exception):
  """
  Exception class when we are unable to load the require page properly.
  This is usually due to
  #. Page taking too long to load. This happens sometimes when loading LexisNexis for the first time.
  #. Improper page loading.
  """

  def __init__(self, frame_name): self.frame_name = frame_name

  def __str__(self): return 'Exception while switching to frame \'{}\'.'.format(self.frame_name)
#end class
