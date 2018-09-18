from Westlaw import WestlawURLScraper, wait_for_page_load, Data_Merging
import time
import csv
import re


judgeNameArray = [
                    'Archer', 'Bissell', 'Bryson', 'Clevenger', 'Dyk',
                    'Gajarsa', 'Hughes', 'Linn', 'Lourie', 'Mayer',
                    'Michel', 'Moore', 'Newman', 'Plager', 'Prost',
                    'Rader', 'Schall', 'Taranto', 'Almond', 'Baldwin',
                    'Bennett', 'Cowen', 'Davis', 'Friedman', 'Laramore',
                    'Markey', 'Miller', 'Nies', "O'Malley", 'Rich',
                    'Skelton', 'Smith', 'Wallach', 'Nichols', 'Reyna',
                    'Stoll', 'Chen', 'Kashiwa',
                ]

# Open a browser and move to Westlaw website through SNU library. And then get URL for the keynumber search.
downloader = WestlawURLScraper()
downloader.logInToSNU()
time.sleep(0.5)

with wait_for_page_load(downloader._driver) as pl:
    KeyNumberURL = downloader.MoveToWestLawKeyNumber()
    # KeyNumberURL: str

# Downloading URL: each downloaded data stored in docURL_Ver.csv
fileNames = [
    'verdictURL_Date_Number.csv',
    'CleanedData']
for i in range(6):
    downloader.iter_search_results(i+1, KeyNumberURL, fileNames)

# Merge downloaded data
DM = Data_Merging(fileNames)
DM._merge()  # merge docURL_Ver files and erase duplicates

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Downloading more info.
with open('CleanedData.txt', 'r', encoding='utf-8', newline='') as f:
    count = 0
    for j in list(csv.reader(f, delimiter='\t'))[count:]:
        # (validPatent, invalidPatent, Majority, Minority) = downloader._get_additional_info(j[3], judgeNameArray)
        print('count is '+str(count))
        Results = downloader._get_additional_info(j[3], judgeNameArray)
        with open('AddedData.csv', 'a', encoding='utf-8', newline='') as f2:
            wr = csv.writer(f2, delimiter='\t')
            wr.writerow(j+Results)
        count +=1




