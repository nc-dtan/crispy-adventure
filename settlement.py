import numpy as np
import pandas as pd
import pickle
import multiprocessing
import time
import concurrent.futures
from tqdm import tqdm
from utils import is_integer
from udtraek import Udtraek
import os

def settlement_id(nymfid):
    #global temp
    #idx = temp['NYMFID'] == nymfid
    #print(len(temp))
    d = temp.loc[temp['NYMFID'] == nymfid, :]
    #temp = temp.loc[~idx, :]
    #Total_HF = sum_amount_code(d, code='DKHFEX')
    return {'NYMFID' : nymfid,
            'total_HF' : sum_amount_code(d, code='DKHFEX') + sum_amount_partial(d),
            'total_IR' : sum_amount_code(d)
            }

def sum_amount(df):

    idx = [is_integer(a) for a in df['PARENT_ID']]
    if idx[0] == False and len(idx) == 1:
        return 0
    else:
        return round(sum(df.loc[idx, 'AMOUNT']),2)

def sum_amount_partial(df):
        return sum_amount(df) - sum_amount_code(df)

def sum_amount_code(df, code='DKCSHACT'):
    idx = df['PARENT_ID'] == code
    if idx.values[0] == False and len(idx) == 1:
        return 0
    else:
        return round(sum(df.loc[idx, 'AMOUNT']),2)

with open('psrm_udtraek.pkl', 'rb') as f:
    a = pickle.load(f)

df = a.udtraeksdata
if os.path.exists('settlement.csv'):
    settlement = pd.read_csv('settlement.csv')
else:
    start_date = '2000-01-01'
    end_date = '2019-01-01'
    cols = ['NYMFID', 'TRANSACTION_DATE', 'PARENT_ID', 'AMOUNT']
    mask = (start_date <= df['TRANSACTION_DATE']) & (df['TRANSACTION_DATE'] <= end_date)
    temp = df[mask]
    temp = temp.loc[:, cols]
    nymfids = temp['NYMFID'].unique()
    
    time_start = time.time()
    with multiprocessing.Pool(processes = 8) as p:
        results = list(tqdm(p.imap(settlement_id, nymfids), total=len(nymfids)))
    #with concurrent.futures.ThreadPoolExecutor() as executor:
    #    results = list(tqdm(executor.map(settlement_id, nymfids), total=len(nymfids)))
    #results = list(tqdm(map(settlement_id, nymfids), total=len(nymfids)))
    
    time_end = time.time()
    print("         ", time_end-time_start)
    settlement = pd.DataFrame(results)
    settlement.to_csv('settlement.csv', index=False)
    
DW_settle = np.genfromtxt('../Data/DataV3/fordringsaldo.rpt', skip_header=2, skip_footer=2)
DW_settle = pd.DataFrame(DW_settle, columns=['NYMFID', 'SALDO_HF','SALDO_RENTER'])
DW_settle['NYMFID'] = DW_settle['NYMFID'].astype('int64')
#DW_settle = DW_settle.sort_values(by=['NYMFID'])
#DW_settle = DW_settle.reset_index(drop=True)
#settlement = settlement.sort_values(by=['NYMFID'])
#settlement = settlement.reset_index(drop=True)
DW_settle.set_index('NYMFID', inplace=True)
settlement.set_index('NYMFID', inplace=True)
Settle_compare = DW_settle.join(settlement, on='NYMFID')
