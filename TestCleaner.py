import pickle
import csv

"""
Import verdict + citation data

Then change their classification numbers into NBER classification numbers

Then add invalidation probabilirt of the given panel
"""

with open('wholeSample.csv', 'r', encoding='utf-8', newline='') as f:
    verdictSampleArrayWEnBanc = list(csv.reader(f, delimiter='\t'))

verdictSampleArray = []
for verdictSample in verdictSampleArrayWEnBanc:
    if len(verdictSample[])