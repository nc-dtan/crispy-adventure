import numpy as np
import pandas as pd
import pickle
import multiprocessing
import time
from tqdm import tqdm
from utils import is_integer
from udtraek import Udtraek
import concurrent.futures


def settlement_id(nymfid):
    #global temp
    #idx = temp['NYMFID'] == nymfid
    #print(len(temp))
    d = temp.loc[temp['NYMFID'] == nymfid, :]
    #temp = temp.loc[~idx, :]
    return {'NYMFID' : nymfid,
            'total_HF' : sum_amount_partial(d),
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

#b = Udtraek(a.udtraeksdata)
df = a.udtraeksdata
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
result = pd.DataFrame(results)
