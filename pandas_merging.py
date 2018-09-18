import pandas as pd
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import date
import time
import numpy as np


step = 3
parser = lambda date: pd.datetime.strptime(date, '%Y%m%d')
for step in range(step,4):
    print('Step '+str(step))
    if step == 1:
        """
        step 1 is for getting citation link w.r.t. sued patents
        """
        VerdictPatentInfoWithProb = pd.read_csv('VerdictPatentInfoWithProb.csv', usecols=[0, 1, 2, 5], names= ['cited', 'verdict', 'verdictDate', 'invalidProb'], dtype={'cited':'int32', 'verdict':'int8', 'invalidProb':'float'}, parse_dates=['verdictDate'], date_parser=parser)
    # ['cited', 'verdict', 'verdictDate', 'validJudges', 'invalidJudges', 'invalidProb']

        print(VerdictPatentInfoWithProb.info())

        df2 = pd.read_csv('C:/Users/Markov/OneDrive/Writing/PatentJurisdiction/PracPy/USPTO_generated/cite7618.csv', dtype={'cited':'int32', 'citing':'int32'})
        df2 = df2.drop_duplicates()
        print(df2.info())

        df3 = pd.merge(VerdictPatentInfoWithProb, df2, on='cited', how='left', validate='m:m')
        df3.to_csv('verdict_citinglink.csv')
        print(df3.info())

    elif step == 2:
        """
        step 2 is for merging application dates to the citation link
        """
        df1 = pd.read_csv('verdict_citinglink.csv', dtype={'cited':'int32'}, index_col=0)
        df1['citing'] = df1['citing'].fillna(0).astype('int32')
        print(df1.info())

        # df2_1.dropna(subset=['ayear'])

        df2 = pd.read_csv('C:/Users/Markov/OneDrive/Writing/PatentJurisdiction/PracPy/USPTO_generated/basic7618.csv', dtype={'wku':'int32'}, parse_dates=['ayear'])
        df2['ayear'] = pd.to_datetime(df2['ayear'], format='%Y-%m-%d', errors='coerce')
        df2 = df2.drop_duplicates()
        print(df2.info(memory_usage='deep'))

        df3 = pd.merge(df1, df2, left_on='cited', right_on='wku', how='left', validate='m:m')
        df3 = pd.merge(df3, df2, left_on='citing', right_on='wku', how='left', validate='m:m')
        print(df3.head())
        df3.to_csv('verdict_citinglink_date.csv')

    elif step == 3:
        df1 = pd.read_csv('verdict_citinglink_date.csv', dtype={'cited':'int32', 'verdict':'int8'}, parse_dates=['verdictDate', 'ayear_x', 'ayear_y'])
        # print(df1.groupby(['cited', 'verdict']).size())
        df1['diff'] = df1['verdictDate'] - df1['ayear_y']
        df1['preCite'] = np.where((pd.to_timedelta(1, unit='D')<=df1['diff']), 1, np.nan)
        df1['postCite'] = np.where((pd.to_timedelta(1, unit='D')>df1['diff']) & (df1['diff'] > -pd.to_timedelta(365*5, unit='D')), 1, np.nan)
        # df1 = df1[(df1.preCite == 1) | (df1.postCite == 1)]  # 요 부분을 바꿔야 한다!! 어떻게?
        df2_1 = df1.groupby(['cited', 'verdictDate', 'preCite'])['preCite'].count().reset_index(name='preCiteFreq').dropna(subset=['preCite'])
        df2_2 = df1.groupby(['cited', 'verdictDate', 'postCite'])['postCite'].count().reset_index(name='postCiteFreq').dropna()
        df2 = pd.merge(df2_1, df2_2, on=['cited', 'verdictDate'], how='left', validate='1:1')
        df2.drop(['preCite', 'postCite'], axis=1, inplace=True)
        VerdictPatentInfoWithProb = pd.read_csv('VerdictPatentInfoWithProb.csv', usecols=[0, 1, 2, 5], names= ['cited', 'verdict', 'verdictDate', 'invalidProb'], dtype={'cited':'int32', 'verdict':'int8', 'invalidProb':'float'}, parse_dates=['verdictDate'], date_parser=parser)
        df3 = pd.merge(VerdictPatentInfoWithProb, df2, on=['cited', 'verdictDate'], how='left', validate='1:m')
        # df3['invalidProb'] = np.where(df3['preCite'] == 1, df3['invalidProb'], 0)
        print(df3.head())
        df3.to_csv('pat_verdict_date_prob_freq.csv')