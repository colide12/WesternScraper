import csv
import re
import selenium.common.exceptions
import selenium.webdriver.common.action_chains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import selenium.webdriver.common.desired_capabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from Westlaw import WestlawURLScraper

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

import pickle
import time
from multiprocessing import Pool
"""
Collecting US patent, judge identities
"""

class USPTOScraper(WestlawURLScraper):
    def nameCleaner(self, searchIndex, fileName= 'AddedData.csv'):
        resultArray = []
        if searchIndex == 4:
            isPatent = 1
        elif searchIndex == 5:
            isPatent = 1
        else:
            print('---Put in integers 4, or 5 for clearing patent numbers---')
            raise ValueError

        with open(fileName, 'r', encoding='utf-8', newline='') as f:
            for i in list(csv.reader(f, delimiter=',')):
                if isPatent:
                    q1 = re.compile("US Patent.+[,][0-9]{3}(([,]\s)|[.])") # 정규식 for patent numbers
                    resultRE = q1.search(i[searchIndex]) # i[4] for valid patents, i[5] for invalid ones
                    if resultRE:
                        resultTMP = resultRE.group()
                        resultTMP = str(resultTMP).split(', ')
                        resultArrayTMP = []
                        resultArrayTMP = resultArrayTMP + resultTMP
                        for j in resultArrayTMP:
                            if (j[-1]=='.'): j = j[:-1] # Erase '.' at the end of str
                            if isPatent:
                                j = j[10:]              # Erase 'US Patent '
                                k = j.replace(",","")   # Erase ','
                            verdictDate = i[1]
                            if searchIndex == 4:
                                validatedJudge = i[6]
                                invalidatedJudge = i[7]
                            else:
                                validatedJudge = i[7]
                                invalidatedJudge = i[6]
                            resultArray.append([j, verdictDate, validatedJudge, invalidatedJudge])
            return resultArray

    def returnTables(self, baseURL, patentNumber):
        self._driver.get(baseURL+patentNumber)
        self._wait_for_element('//table')
        tables = self._driver.find_elements_by_xpath('//table')

        return tables

    def searchPatents(self, patentNumber):
        baseURL = 'http://patft.uspto.gov/netacgi/nph-Parser?Sect2=PTO1&Sect2=HITOFF&p=1&u=%2Fnetahtml%2FPTO%2Fsearch-bool.html&r=1&f=G&l=50&d=PALL&RefSrch=yes&Query=PN%2F'
        tables = self.returnTables(baseURL, patentNumber)

        waiting = True
        while waiting:
            try:
                self._wait_for_element('//table')
                publishedDate = self._driver.find_element_by_xpath('//b[contains(text(), "United States Patent")]/../../../tr[2]/td[2]/b').text.replace('*','')
                waiting = False
            except IndexError:
                try:
                    self._wait_for_element('//table')
                    publishedDate = self._driver.find_element_by_xpath('//b[contains(text(), "Issue Date:")]/../../td[2]/b').text.replace('*','')
                    waiting = False
                except IndexError:
                    print('Waiting')
                    time.sleep(30)
                    tables = self.returnTables(patentNumber)
                    waiting = True
        classification = self._driver.find_element_by_xpath('//b[contains(text(), "Current U.S. Class:")]/../../td[2]/b').text.split('/')[0]
        return (publishedDate, classification)


    def searchReferingPatents(self, patentNumber):
        isNextPage = True
        pageNumber = 1
        referingPatentArray = []
        referingPatentNumberArray = []
        while isNextPage:
            print(pageNumber)
            baseURL = 'http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&p={}&u=%2Fnetahtml%2Fsearch-adv.htm&r=0&f=S&l=50&d=PALL&Query=ref/'
            tables = self.returnTables(baseURL.format(pageNumber),patentNumber) # this is a big table containing citing patents
            
            try:
                referingPatentTable = tables[1].find_elements_by_tag_name('tr')[1:]
                for trs in referingPatentTable:
                    referingPatentNumberArray.append(trs.find_elements_by_tag_name('td')[1].text)
                try:
                    self._driver.find_element_by_xpath('//img[@src="/netaicon/PTO/nextlist.gif"]')# if there is a next page button = if there is a next page
                    pageNumber += 1
                except:
                    isNextPage = False
            except:
                referingPatentNumberArray = []
                isNextPage = False
        for referingPatentNumber in referingPatentNumberArray:
            referingPubDate = self.searchPatents(referingPatentNumber)[0]
            referingPatentArray.append([referingPatentNumber,referingPubDate])
        return referingPatentArray
    """
    some patents are cited more than 50 times. And the result page shows only 50 refering patents at once.
    """

Scraper = USPTOScraper()

isverdictSample = 0
if isverdictSample == 1:
    f = open("classificationChart.txt", 'rb')
    classificationChart = pickle.load(f) # this determines which class fits to 6 classes

    for verdict in [0,1]: # =0 if valid, =1 if invalid
        id = 0
        for validPatent in Scraper.nameCleaner(verdict+4)[:]: # ([patentNumber, verdictDate, validatedJudge, invalidatedJudge])
            time.sleep(1)
            print(validPatent)
            print(verdict,id)
            publishedDate = parse(Scraper.searchPatents(validPatent[0])[0])  # this code gets when validated patents were published
            verdictDate = parse(validPatent[3])
            verdictSample = [validPatent[0], publishedDate, verdict, verdictDate, validPatent[2], validPatent[3]]
            if verdict == 0:
                with open('validVerdictSampleArray.csv', 'a', encoding='utf-8', newline='') as f2:
                    wr = csv.writer(f2)
                    wr.writerow(verdictSample)
            else:
                with open('invalidVerdictSampleArray.csv', 'a', encoding='utf-8', newline='') as f2:
                    wr = csv.writer(f2)
                    wr.writerow(verdictSample)
            id +=1

else:
    with open('validVerdictSampleArray.txt', 'r', encoding='utf-8', newline='') as f:
        verdictSampleArray = list(csv.reader(f, delimiter='\t'))
    with open('invalidVerdictSampleArray.txt', 'r', encoding='utf-8', newline='') as f:
         verdictSampleArray = verdictSampleArray+list(csv.reader(f, delimiter='\t'))
    wholeSample = []
    # for verdictSample in verdictSampleArray[459:500]: # 31이 짧음 245까지 함 459부터 invalidation
    for verdictSample in verdictSampleArray[100:150]: # 31이 짧음 245까지 함 459부터 invalidation
        print(verdictSample)
        referingPatentArray = Scraper.searchReferingPatents(verdictSample[0]) # patents citing verdict sample[Number and pubDate]
        referingPatentDistBefore = []
        referingPatentDistAfter = []
        for referingPatent in referingPatentArray:
            referingDate = parse(referingPatent[1])
            print(referingDate)
            if (referingDate<parse(verdictSample[3])): # i.e. cited before
                print('A patent citing before the verdict')
                referingPatentDistBefore.append(referingPatent[0])
                # referingPatentDistBefore.append([referingPatent[0], len(refreferingPatentArray)]) # code trying to collect patents' quality
            elif (referingDate-relativedelta(years=5)<parse(verdictSample[3])): # cited in 5 year window after the verdict
                print('A patent citing after the verdict')
                referingPatentDistAfter.append(referingPatent[0])
            else:
                print('patent citing after 5 years of the verdict')
                # referingPatentDistAfter.append([referingPatent[0], len(refreferingPatentArray)]) # code trying to collect patents' quality
        #
        #     refreferingPatentArray = Scraper.searchReferingPatents(referingPatent[0]) # patents citing patents those citing verdict sample[Numvber and pubDate]

        with open('wholeSample.csv', 'a', encoding='utf-8', newline='') as f:
                wr = csv.writer(f)
                print(verdictSample+[len(referingPatentDistBefore), len(referingPatentDistAfter)])
                # wr.writerow(verdictSample+[referingPatentDistBefore, referingPatentDistAfter])
                wr.writerow(verdictSample+[len(referingPatentDistBefore), len(referingPatentDistAfter)])
        # wholeSample.append(verdictSample+[referingPatentDistBefore, referingPatentDistAfter])
        wholeSample.append(verdictSample+[len(referingPatentDistBefore), len(referingPatentDistAfter)])
    f = open("wholeSample.txt", 'wb')
    pickle.dump(wholeSample, f)
    f.close()


