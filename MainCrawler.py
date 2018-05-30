from Westlaw import WestlawURLScraper, wait_for_page_load, Data_Merging
import time
import csv
import re

judgeNameArray = [
    'Archer',
    'Bissell',
    'Bryson',
    'Clevenger',
    'Dyk',
    'Gajarsa',
    'Hughes',
    'Linn',
    'Lourie',
    'Mayer',
    'Michel',
    'Moore',
    'Newman',
    'Plager',
    'Prost',
    'Rader',
    'Schall',
    'Taranto',
    'Almond',
    'Baldwin',
    'Bennett',
    'Cowen',
    'Davis',
    'Friedman',
    'Laramore',
    'Markey',
    'Miller',
    'Nies',
    "O'Malley",
    'Rich',
    'Skelton',
    'Smith',
    'Wallach',
    'Nichols',
    'Reyna',
    'Stoll',
    'Chen',
    'Kashiwa',
    ]
downloader = WestlawURLScraper()
downloader.logInToSNU()
time.sleep(0.5)
with wait_for_page_load(downloader._driver) as pl:
    KeyNumberURL = downloader.MoveToWestLawKeyNumber()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Downloading URL
# for i in range(6):
#     downloader.iter_search_results(i+1, KeyNumberURL)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# # Merge downloaded data
# fileNames = [
#     'docURL_Ver1',
#     'docURL_Ver2',
#     'docURL_Ver3',
#     'docURL_Ver4',
#     'docURL_Ver5',
#     'docURL_Ver6',
#     'MergedData',
#     'CleanedData']
# DM = Data_Merging(fileNames)
# # DM._merge()
# DM._erase_duplication()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Downloading more info.
with open('CleanedData.csv', 'r', encoding='utf-8', newline='') as f:
    count = 1070
    for j in list(csv.reader(f, delimiter=','))[count:]:
        # (validPatent, invalidPatent, Majority, Minority) = downloader._get_additional_info(j[3], judgeNameArray)
        print('count is '+str(count))
        Results = downloader._get_additional_info(j[3], judgeNameArray)
        with open('AddedData.csv', 'a', encoding='utf-8', newline='') as f2:
            wr = csv.writer(f2)
            wr.writerow(j+Results)
        count +=1



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Collecting US patent, judge identities
# PatentArray = []
# with open('AddedData.csv', 'r', encoding='utf-8', newline='') as f:
#     for i in csv.reader(f, delimiter=','):
#         q1 = re.compile("US Patent.+[,][0-9]{3}(([,]\s)|[.])") # 정규식 for patent numbers
#         PatentRE = q1.search(i[4]) # i[4] for valid patents, i[5] for invalid ones
#         if PatentRE:
#             PatentTMP = PatentRE.group()
#             PatentTMP = str(PatentTMP).split(', ')
#             PatentArray = PatentArray + PatentTMP

# print(len(PatentArray))
# print(len(list(set(PatentArray))))
