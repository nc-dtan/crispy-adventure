from data import Data
from utils import is_integer, convert_date_from_str
from datetime import datetime, timedelta
from tqdm import tqdm
import pandas as pd
from utils import to_amount
from pathos.multiprocessing import ProcessingPool
from pathos.multiprocessing import cpu_count

class Udtraek(Data):
    def __init__(self, df):
        self.df = df[['TRANSACTION_DATE', 'EFFECTIVE_DATE', 'NYMFID', 'PARENT_ID', 'SIBLING_ID', 'AMOUNT', 'FT_TYPE_FLG']].copy()
        self.df.sort_values('TRANSACTION_DATE', inplace=True)
        self.df['TRANSACTION_DATE'] = pd.to_datetime(self.df['TRANSACTION_DATE'])
        self.df['AMOUNT'] = to_amount(self.df['AMOUNT'])

    def sum_amount(self, df=None):
        if df is None:
            temp = self.df
        else:
            temp = df
        idx = [is_integer(a) for a in temp['PARENT_ID']]
        if idx[0] == False and len(idx) == 1:
            return 0
        else:
            return round(sum(temp.loc[idx,'AMOUNT']),2)

    def sum_amount_partial(self,df, code='DKCSHACT'):
        return self.sum_amount(df) - self.sum_amount_code(df, code)

    def sum_amount_code(self,df, code='DKCSHACT'):
        idx = df['PARENT_ID'] == code
        if idx.values[0] == False and len(idx) == 1:
            return 0
        else:
            return round(sum(df.loc[idx, 'AMOUNT']),2)

    def duplicate_transDTTM(self):
        idx = self.df.TransDTTM.duplicated()
        return self.df.TransDTTM[idx]

    def select_between_dates(self, start_date, end_date):
        if isinstance(start_date, str):
            start_date = convert_date_from_str(start_date)
        if isinstance(end_date, str):
            end_date = convert_date_from_str(end_date)

        mask = (start_date <= self.df['TRANSACTION_DATE']) & (self.df['TRANSACTION_DATE'] <= end_date)
        return Udtraek(self.df[mask])

    def select_to_date(self, end_date):
        start_date = self.df['TRANSACTION_DATE'].values[0]  # Sorted after dates, so first date is start date
        return self.select_between_dates(start_date, end_date)

    def select_from_date(self, start_date):
        end_date = self.df['TRANSACTION_DATE'].values[-1]  # Sorted after dates, so last date is end date
        return self.select_between_dates(start_date, end_date)

    def select_on_date(self, date):
        if isinstance(date, str):
            date = convert_date_from_str(date)
        start_date = datetime(date.year, date.month, date.day)
        end_date = start_date + timedelta(days=1)
        return self.select_between_dates(start_date, end_date)

    def multi_CATU(self):
        res = []
        cols = ['NYMFID', 'TRANSACTION_DATE', 'PARENT_ID']
        temp = self.df.loc[:, cols]
        nymfids = temp['NYMFID'].unique()
        for nymfid in tqdm(nymfids):
            d = temp.loc[temp['NYMFID'] == nymfid, :]
            d = d.loc[d['PARENT_ID'] == 'DKCSHACT', :]
            if len(d) < 3:
                continue

            timestamps = d['TRANSACTION_DATE'].unique()
            for timestamp in timestamps:
                if len(d.loc[d['TRANSACTION_DATE'] == timestamp, :]) == 3:
                    # TODO: Make to a generator and yield nymfid instead.
                    res.append(nymfid)
                    break
        return res

    def ident_CATU(self):
        res = []
        cols = ['NYMFID', 'TRANSACTION_DATE', 'PARENT_ID', 'AMOUNT']
        temp = self.df.loc[:, cols]
        nymfids = temp['NYMFID'].unique()
        for nymfid in tqdm(nymfids):
            d = temp.loc[temp['NYMFID'] == nymfid, :]
            d = d.loc[d['PARENT_ID'] == 'DKCSHACT', :]
            if len(d) <= 3:
                continue
            timestamps = d['TRANSACTION_DATE'].unique()
            for timestamp in timestamps:
                amounts = d.loc[d['TRANSACTION_DATE'] == timestamp, 'AMOUNT']
                if len(amounts) == 3:
                    AMT = abs(amounts).unique()
                    if len(AMT) == 1:
                        res.append(nymfid)
                        break
        
        return res

    def settlement(self, start_date = '2000-01-01', end_date = '2019-01-01'):
        cols = ['NYMFID', 'TRANSACTION_DATE', 'PARENT_ID', 'AMOUNT']
        temp = self.select_between_dates(start_date, end_date).df
        temp = temp.loc[:, cols]
        nymfids = temp['NYMFID'].unique()
        results = []
        for nymfid in tqdm(nymfids):
            d = temp.loc[temp['NYMFID'] == nymfid, :]
            mfr = {'NYMFID' : nymfid, 
                    'total_HF' : self.sum_amount_partial(d),
                    'total_IR' : self.sum_amount_code(d)
                    }
            results.append(mfr)
        return pd.DataFrame(results)

    def multi_wdex(self, ncpus=None):
        if ncpus is None:
            ncpus = cpu_count() - 1
        cols = ['NYMFID', 'TRANSACTION_DATE', 'PARENT_ID', 'AMOUNT', 'FT_TYPE_FLG']
        temp = self.df.loc[:, cols]
        nymfids = temp['NYMFID'].unique()
        temp['AMOUNT'] = to_amount(temp['AMOUNT'])
        pool = ProcessingPool(ncpus=ncpus)
        result = pool.map(lambda x: _multi_wdex_worker(temp, x), nymfids)
        return list(filter(None, result))

def _multi_wdex_worker(df, nymfid):
    d = df.loc[df['NYMFID'] == nymfid]
    d = d.loc[d['PARENT_ID'].str[-4:] == 'WDEX']
    if len(d) >= 2:
        for date, g in d.groupby(d.TRANSACTION_DATE.dt.date):
            if len(g) >= 2:
                AD_len = len(g.loc[g['FT_TYPE_FLG'] == 'AD'])
                AX_len = len(g.loc[g['FT_TYPE_FLG'] == 'AX'])
                if AD_len == AX_len:
                    continue
                elif AD_len == AX_len+2:
                    if not g['AMOUNT'].is_unique:
                        return nymfid
