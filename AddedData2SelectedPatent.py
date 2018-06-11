import csv
import re

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import requests

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

import pickle
import time
"""
Collecting US patent, judge identities
"""

def nameCleaner(searchIndex, fileName= 'AddedData.csv'):
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
def connectTo(baseURL, patentNumber):
    html = requests.get(baseURL+patentNumber, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'}, timeout=10)
    source = html.text
    soup = BeautifulSoup(source, "lxml")
    tables = soup.find_all('table')
    html.close
    return [soup,tables]

def returnTables(baseURL, patentNumber):
    try:
        [soup,tables] = connectTo(baseURL, patentNumber)
    except:
        print('some error opening a page for patent '+patentNumber)
        waitTime = 60
        print('Will try reconnecting %d seconds later' % waitTime)
        time.sleep(waitTime)
        [soup,tables] = connectTo(baseURL, patentNumber)
    return [soup,tables]

def searchPatents(patentNumber):
    baseURL = 'http://patft.uspto.gov/netacgi/nph-Parser?Sect2=PTO1&Sect2=HITOFF&p=1&u=%2Fnetahtml%2FPTO%2Fsearch-bool.html&r=1&f=G&l=50&d=PALL&RefSrch=yes&Query=PN%2F'
    [soup, tables] = returnTables(baseURL, patentNumber)

    waiting = True
    while waiting:
        try:
            publishedDate = soup.find('b', string="United States Patent ").find_parent('tr').find_next_sibling('tr').find_all('td')[1].find('b').text.replace('*','')
            tables[2].find_all('tr')[1].find_all('td')[1].text.replace('*','')
            waiting = False
        except:
            try:
                publishedDate = soup.find('b', string="Issue Date:").parent.parent.find_all('td')[1].find('b').text.replace('*','')
                waiting = False
            except:
                print('Waiting')
                time.sleep(200)
                [soup, tables] = returnTables(patentNumber)
                waiting = True
    classification = soup.find('b', string='Current U.S. Class:').parent.parent.find_all('td')[1].find('b').text.split('/')[0]
    return (publishedDate, classification)


def searchReferingPatents(patentNumber):
    isNextPage = True
    pageNumber = 1
    referingPatentArray = []
    referingPatentNumberArray = []
    while isNextPage:
        baseURL = 'http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&p={}&u=%2Fnetahtml%2Fsearch-adv.htm&r=0&f=S&l=50&d=PALL&Query=ref/'
        [soup, tables] = returnTables(baseURL.format(pageNumber),patentNumber)
        if soup.find('th', string='PAT. NO.'):
            referingPatentTable = tables[1].find_all('tr')[1:]
            for trs in referingPatentTable:
                referingPatentNumberArray.append(trs.find_all('td')[1].text)
            if soup.find('img', attrs={'src':'/netaicon/PTO/nextlist.gif', 'alt':'[NEXT_LIST]'}): # if there is a next page button = if there is a next page
                pageNumber += 1
            else:
                isNextPage = False
        else:
            referingPatentNumberArray = []
            isNextPage = False
    print('Downloading citing patent table ended')
    num = 1
    for referingPatentNumber in referingPatentNumberArray:
        referingPubDate = searchPatents(referingPatentNumber)[0]
        referingPatentArray.append([referingPatentNumber,referingPubDate])
        a = 'Getting patented date %d out of %d done' %(num, len(referingPatentNumberArray) )
        print(a)
        num+=1
    return referingPatentArray

    """
    some patents are cited more than 50 times. And the result page shows only 50 refering patents at once.
    """
# f = open("classificationChart.txt", 'rb')
#     classificationChart = pickle.load(f) # this determines which class fits to 6 classes

def mergeIssuedDate():
    for verdict in [0,1]:
        for index, validPatent in enumerate(nameCleaner(verdict+4), 1): # [patentNumber, verdictDate, validatedJudge, invalidatedJudge, classification]
            print(validPatent)
            print(verdict,index)
            publishedDate = parse(searchPatents(validPatent[0])[0])  # this code gets when validated patents were published
            classification = searchPatents(validPatent[0])[1]
            verdictDate = parse(validPatent[1])
            verdictSample = [validPatent[0], publishedDate, verdict, verdictDate, validPatent[2], validPatent[3], classification]
            print(verdictSample)
            if verdict == 0:
                with open('validVerdictSampleArray.csv', 'a', encoding='utf-8', newline='') as f2:
                    wr = csv.writer(f2)
                    wr.writerow(verdictSample)
            else:
                with open('invalidVerdictSampleArray.csv', 'a', encoding='utf-8', newline='') as f2:
                    wr = csv.writer(f2)
                    wr.writerow(verdictSample)

def mergeReferingPatent(verdictSampleArray, startVerdict):
    tic = time.time()
    wholeSample = []
    for Count, verdictSample in enumerate(verdictSampleArray[startVerdict:], startVerdict+1): # 31이 짧음 245까지 함 459부터 invalidation
        toc1 = time.time()
        print('Start Downloading citing information about US Patent '+verdictSample[0])
        referingPatentArray = searchReferingPatents(verdictSample[0]) # patents citing verdict sample[Number and pubDate]
        referingPatentDistBefore = []
        referingPatentDistAfter = []
        index = 0

        for index, referingPatent in enumerate(referingPatentArray): # sorting the citing patent before, and after the verdict
            print('Getting patented date, %d out of %d sorted, that of %dth sued patent' %(index, len(referingPatentArray), Count ))
            referingDate = parse(referingPatent[1])
            print(referingDate)

            if (referingDate<parse(verdictSample[3])): # i.e. cited before
                referingPatentDistBefore.append(referingPatent[0])
            elif (referingDate-relativedelta(years=5)<parse(verdictSample[3])): # cited in 5 year window after the verdict
                referingPatentDistAfter.append(referingPatent[0])
            else: print('Citing out of the 5 year window')
            #end if
        #end for

        print(verdictSample+[len(referingPatentDistBefore), len(referingPatentDistAfter)])

        with open('wholeSample.csv', 'a', encoding='utf-8', newline='') as f:
            wr = csv.writer(f)
            wr.writerow(verdictSample+[len(referingPatentDistBefore), len(referingPatentDistAfter)])
        #end with

        wholeSample.append(verdictSample+[len(referingPatentDistBefore), len(referingPatentDistAfter)]) # this code is for pickle.dump
        toc2 = time.time()
        tictoc = 'It took about %s Seconds for the %dth patent, %s Second per patent' %(toc2-toc1, Count, (toc2-tic)/Count)
        print(tictoc)
        estLeftTime = 'About %s Seconds left to finish downloading %d patent data' %((len(verdictSampleArray)-Count)*(toc2-tic)/Count,len(verdictSampleArray)-Count)
        print(estLeftTime)
        print('='*len(tictoc))
    #end for

    f = open("wholeSample.txt", 'wb')
    pickle.dump(wholeSample, f)
    f.close()
    #end def

with open('validVerdictSampleArray.csv', 'r', encoding='utf-8', newline='') as f:
    verdictSampleArray = list(csv.reader(f, delimiter=','))
with open('invalidVerdictSampleArray.csv', 'r', encoding='utf-8', newline='') as f:
     verdictSampleArray = verdictSampleArray+list(csv.reader(f, delimiter=','))

startVerdict = 0 # Count는 1부터 시작하기 때문에, 코드가 멈춘 patent에 해당하는 숫자=끝까지 돌아간 patent의 Count
mergeReferingPatent(['4,001,460'], startVerdict)