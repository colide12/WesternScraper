import pandas as pd
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import date
import time
import numpy as np


step = 3
parser = lambda date: pd.datetime.strptime(date, '%Y%m%d')

if step == 1:
    VerdictPatentInfoWithProb = pd.read_csv('VerdictPatentInfoWithProb.csv', usecols=[0, 1, 2, 5], names= ['cited', 'verdict', 'verdictDate', 'invalidProb'], dtype={'cited':str, 'verdict':'int8', 'invalidProb':'float'}, parse_dates=['verdictDate'], date_parser=parser)
# ['cited', 'verdict', 'verdictDate', 'validJudges', 'invalidJudges', 'invalidProb']

    print(VerdictPatentInfoWithProb.info())

    df2 = pd.concat(
            [
                pd.read_csv('D:/Data/acite75_99/cite75_99.txt', dtype={'CITED':str, 'CITING':str}).rename(index=str, columns={'CITING':'citing', 'CITED':'cited'}),
                pd.read_csv('C:/Users/Markov/Desktop/PracPy/cite0518.csv', names=['cited', 'citing'], dtype={'cited':str, 'citing':str}).rename(index=str, columns={'citing':'citing'})
            ], sort=False)
    df2 = df2.drop_duplicates()
    print(df2.info())

    df3 = pd.merge(VerdictPatentInfoWithProb, df2, on='cited', how='left', validate='m:m')
    df3.to_csv('verdict_citinglink.csv')
    print(df3.info())

elif step == 2:
    df1 = pd.read_csv('C:/Users/Markov/Documents/GitHub/WesternScraper/verdict_citinglink.csv', dtype={'cited':str, 'citing':str}, index_col=0)
    # df1 = df1.dropna(subset=['citing'])
    # df1['citing'] = df1['citing'].astype('int32').astype(str)

    df2_1 = pd.read_csv('D:/Data/application.tsv/data/20180528/bulk-downloads/application.tsv', sep='\t', header=0, usecols=[1,5], dtype={'patent_id':str}, parse_dates=['date']).rename(index=str, columns={'patent_id':'PATENT', 'date':'AYEAR'})
    df2_1['AYEAR'] = pd.to_datetime(df2_1['AYEAR'], format='%Y-%m-%d', errors='coerce')
    df2_1.dropna(subset=['AYEAR'])

    # df2_1['GYEAR'] = df2_1['GYEAR'].astype('int32')
    # df2_1['date'] = df2_1['date'].str.replace('-00','-01')
    # df2_1['date'] = df2_1['date'].str.replace('9173-','1973-')

    df2 = pd.read_csv('C:/Users/Markov/Desktop/PracPy/basic0518.csv', usecols=[0,2], names=['PATENT', 'AYEAR'], dtype={'PATENT':str}, parse_dates=['AYEAR'], date_parser=parser)

    df2 = pd.concat([df2_1, df2], sort=False)
    df2 = df2.drop_duplicates()
    print(df2.info(memory_usage='deep'))

    df3 = pd.merge(df1, df2, left_on='cited', right_on='PATENT', how='left', validate='m:m')
    df3 = pd.merge(df3, df2, left_on='citing', right_on='PATENT', how='left', validate='m:m')
    print(df3.head())
    df3.to_csv('test1.csv')

elif step == 3:
    df1 = pd.read_csv('test1.csv', parse_dates=['verdictDate', 'AYEAR_x', 'AYEAR_y'])
    # print(df1.groupby(['cited', 'verdict']).size())
    df1['diff'] = df1['verdictDate'] - df1['AYEAR_y']


    print(df1['diff'])
    df1['preCite'] = np.where((pd.to_timedelta(1, unit='D')<=df1['diff']), 1, 0)
    df1['postCite'] = np.where((pd.to_timedelta(1, unit='D')>df1['diff']) & (df1['diff'] > -pd.to_timedelta(365*5, unit='D')), 1, 0)
    print(df1.info())
    df1 = df1[(df1.preCite == 1) | (df1.postCite == 1)]
    df2 = df1.groupby(['cited', 'verdictDate', 'preCite'])['preCite'].count().reset_index(name='citeFreq')
    print(df2.head())
    VerdictPatentInfoWithProb = pd.read_csv('VerdictPatentInfoWithProb.csv', usecols=[0, 1, 2, 5], names= ['cited', 'verdict', 'verdictDate', 'invalidProb'], dtype={'cited':str, 'verdict':'int8', 'invalidProb':'float'}, parse_dates=['verdictDate'], date_parser=parser)
    df3 = pd.merge(VerdictPatentInfoWithProb, df2, on=['cited', 'verdictDate'], how='left', validate='1:m')
    print(df3.head())


