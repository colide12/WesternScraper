import csv
import re

def judgeNameClearing(dirtyList):
    """
    Sadly, a list of judges saved in csv files changed to str. This fnc is for transforming the str into a list again
    """
    JudgeArray = ''
    for letters in dirtyList[1:-1]:
        JudgeArray = JudgeArray+letters
    return JudgeArray

def invalidationProbability(probArray):
    if len(probArray) == 1:
        prob = probArray[0]
    elif len(probArray) == 2:
        prob = probArray[0]*probArray[1]
    elif len(probArray) == 3:
        prob = probArray[0]*probArray[1]*probArray[2] + (1- probArray[0])*probArray[1]*probArray[2] + probArray[0]*(1- probArray[1])*probArray[2] +probArray[0]*probArray[1]*(1- probArray[2])
    return prob
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

with open('wholeSample.csv', 'r', encoding='utf-8', newline='') as f:
    verdictSampleArrayWEB = list(csv.reader(f, delimiter='\t'))

verdictSampleArray = []
for verdictSample in verdictSampleArrayWEB: # choose a verdict
    # verdictSample = [validPatent[0], publishedDate, verdict, verdictDate, validPatent[2], validPatent[3], classification]
    validJudgeArrayDefected = verdictSample[4] # o'malley's name should be cleaned
    validJudgeArray = judgeNameClearing(validJudgeArrayDefected).replace("'", "").split(', ') # to change o'malle y into omalley
    if '' in validJudgeArray:
        validJudgeArray.remove('')
    invalidJudgeArrayDefected = verdictSample[5]
    invalidJudgeArray = judgeNameClearing(invalidJudgeArrayDefected).replace("'", "").split(', ')
    if '' in invalidJudgeArray:
        invalidJudgeArray.remove('')
    panel = validJudgeArray + invalidJudgeArray

    if len(panel)<4:
        verdictSampleArray.append([verdictSample[0], verdictSample[1], verdictSample[2], verdictSample[3], validJudgeArray, invalidJudgeArray, verdictSample[6], verdictSample[7]])
verdictSampleArray = verdictSampleArray[:-1] # Don't know why but the last element is empty

for judge in judgeNameArray:  # choose a circuit judge
    decision = 0
    partici = 0
    for verdictSample in verdictSampleArray:
        panel = verdictSample[4] + verdictSample[5]
        if (judge in panel) and (len(panel)<4):
            partici += 1 # if that judge is who I chose before
        if (verdictSample[5]) and (judge in verdictSample[5]) and (len(panel)<4): # if any one made a validation decision and if that judge is who I chose before
            decision +=1
    invalidationDict[judge] = decision
    participationDict[judge] = partici

probabilityArray = []
for verdictSample in verdictSampleArray: # choose a verdict
    validJudgeArray = verdictSample[4]
    invalidJudgeArray = verdictSample[5]
    panel = validJudgeArray + invalidJudgeArray
    for particiJudge in panel:
        probabilityArrayTMP = []
        if particiJudge in validJudgeArray:
            probability = invalidationDict[particiJudge]/(participationDict[particiJudge]-1)
            probabilityArrayTMP.append(probability)
        elif particiJudge in invalidJudgeArray:
            probability = (invalidationDict[particiJudge]-1)/(participationDict[particiJudge]-1)
            probabilityArrayTMP.append(probability)
    probabilityArray.append(probabilityArrayTMP)

panelProbArray = []
for panelProb in probabilityArray:
    panelProbArray.append(invalidationProbability(panelProb))


verdict_Prob_NumOfCitation_Sample = []
for i, verdictSample in enumerate(verdictSampleArray):
    k = verdictSample+[panelProbArray[i]]
    verdict_Prob_NumOfCitation_Sample.append(k)
print(verdict_Prob_NumOfCitation_Sample)

for i in verdict_Prob_NumOfCitation_Sample:
    with open('verdict_Prob_NumOfCitation_Sample.csv', 'a', encoding='utf-8', newline='') as f2:
            wr = csv.writer(f2)
            wr.writerow(i)