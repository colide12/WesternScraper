import csv
import re

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import requests

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pickle
import time


def nameCleaner(searchIndex, fileName= 'AddedData.csv'):
    resultArray = []
    if (searchIndex == 4) or (searchIndex == 5):
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
                        resultArray.append([j, verdictDate, validatedJudge, invalidatedJudge])  # j is the number
        return resultArray

def judgeNameStr2List(dirtyList):
    """
    Sadly, a list of judges saved in csv files changed to str. This fnc is for transforming the str into a list again
    """
    JudgeArray = ''
    for letters in dirtyList[1:-1]:
        JudgeArray = JudgeArray+letters
    return JudgeArray

def judgeNameCleaner(defectedName):
    validJudgeArray = judgeNameStr2List(defectedName).replace("'", "").split(', ') # to change o'malle y into omalley
    if '' in validJudgeArray:
        validJudgeArray.remove('')
    return validJudgeArray

def invalidationProbability(probArray):
    if len(probArray) == 1:
        prob = probArray[0]
    elif len(probArray) == 2:
        prob = probArray[0]*probArray[1]
    elif len(probArray) == 3:
        prob = probArray[0]*probArray[1]*probArray[2] + (1- probArray[0])*probArray[1]*probArray[2] + probArray[0]*(1- probArray[1])*probArray[2] +probArray[0]*probArray[1]*(1- probArray[2])
    return prob


if __name__ == '__main__':
    for verdict in [0,1]:
        for index, validPatent in enumerate(nameCleaner(verdict+4), 1): # [patentNumber, verdictDate, validatedJudge, invalidatedJudge]
            verdictDate = datetime.date(parse(validPatent[1])).strftime('%Y%m%d')
            verdictSample = [validPatent[0].replace(',', ''), verdict, verdictDate, validPatent[2], validPatent[3]]
            with open('VerdictPatentInfo.csv', 'a', encoding='utf-8', newline='') as f2:
                wr = csv.writer(f2)
                wr.writerow(verdictSample)

    print('Saving VerdictPatentInfo completed')
    judgeNameArray = (
                        'archer', 'bissell', 'bryson', 'clevenger', 'dyk',
                        'gajarsa', 'hughes', 'linn', 'lourie', 'mayer',
                        'michel', 'moore', 'newman', 'plager', 'prost',
                        'rader', 'schall', 'taranto', 'almond', 'baldwin',
                        'bennett', 'cowen', 'davis', 'friedman', 'laramore',
                        'markey', 'miller', 'nies', '"omalley"', 'rich',
                        'skelton', 'smith', 'wallach', 'nichols', 'reyna',
                        'stoll', 'chen', 'kashiwa'
                    )

    invalidationDict = {}
    participationDict = {}

    for judge in judgeNameArray:
        invalidationDict.setdefault(judge, 0)
        participationDict.setdefault(judge, 0)

    with open('VerdictPatentInfo.csv', 'r', encoding='utf-8', newline='') as f:
        verdictSampleArrayWEB = list(csv.reader(f, delimiter=','))

    verdictSampleArray = []
    for verdictSample in verdictSampleArrayWEB: # choose a verdict
        # verdictSample = [PATNO, verdict, verdictDate, validPatent[2], validPatent[3]]

        validJudgeArray = judgeNameCleaner(verdictSample[3])
        invalidJudgeArray = judgeNameCleaner(verdictSample[4])
        panel = validJudgeArray + invalidJudgeArray

        if len(panel)<4:  # non en-banc
            verdictSampleArray.append([verdictSample[0], verdictSample[1], verdictSample[2], validJudgeArray, invalidJudgeArray])
    verdictSampleArray = verdictSampleArray[:-1] # Don't know why but the last element is empty

    for judge in judgeNameArray:  # choose a circuit judge
        decision = 0
        partici = 0
        for verdictSample in verdictSampleArray:
            panel = verdictSample[3] + verdictSample[4]
            if (judge in panel) and (len(panel)<4):
                partici += 1 # if that judge is who I chose before
            if (verdictSample[4]) and (judge in verdictSample[4]) and (len(panel)<4): # if any one made a invalidation decision and if that judge is who I chose before
                decision +=1
        invalidationDict[judge] = decision
        participationDict[judge] = partici

    verdictSampleWithProb = []
    for index, verdictSample in enumerate(verdictSampleArray): # choose a verdict
        validJudgeArray = verdictSample[3]
        invalidJudgeArray = verdictSample[4]
        panel = validJudgeArray + invalidJudgeArray
        probabilityArrayTMP = []
        for particiJudge in panel:
            if particiJudge in validJudgeArray:
                probability = invalidationDict[particiJudge]/(participationDict[particiJudge]-1)
                probabilityArrayTMP.append(probability)
            elif particiJudge in invalidJudgeArray:
                probability = (invalidationDict[particiJudge]-1)/(participationDict[particiJudge]-1)
                probabilityArrayTMP.append(probability)
        panelInvalidProb = invalidationProbability(probabilityArrayTMP)
        verdictSampleWithProb.append(verdictSample+[panelInvalidProb])
    # with open('VerdictPatentInfoWithProb.csv', 'a', encoding='utf-8', newline='') as f2:
    #         wr = csv.writer(f2)
    #         wr.writerow(['cited', 'verdict', 'verdictDate', 'validJudges', 'invalidJudges', 'invalidProb'])
    for i in verdictSampleWithProb:
        with open('VerdictPatentInfoWithProb.csv', 'a', encoding='utf-8', newline='') as f2:
                wr = csv.writer(f2)
                wr.writerow(i)

    print('saving VerdictPatentInfoWithProb completed')