from data import Data
from utils import is_integer
from datetime import datetime, timedelta


class Udtraek(Data):
    def __init__(self, df):
        self.df = df[['TransDTTM', 'EffectiveDate', 'NYMFID', 'Parent', 'Sibling_ID', 'AMOUNT', 'FT_FLG']].copy()
        self.df.sort_values('TransDTTM', inplace=True)

    @property
    def sum_amount(self):
        idx = [is_integer(a) for a in self.df['Parent']]
        return round(sum(self.df.loc[idx, 'AMOUNT']), 2)

    def duplicate_transDTTM(self):
        idx = self.df.TransDTTM.duplicated()
        return self.df.TransDTTM[idx]

    def select_between_dates(self, start_date, end_date):
        mask = (start_date <= self.df['TransDTTM']) & (self.df['TransDTTM'] <= end_date)
        return self.df[mask]

    def select_to_date(self, end_date):
        start_date = self.df['TransDTTM'].values[0]  # Sorted after dates, so first date is start date
        return self.select_between_dates(start_date, end_date)

    def select_from_date(self, start_date):
        end_date = self.df['TransDTTM'].values[-1]  # Sorted after dates, so last date is end date
        return self.select_between_dates(start_date, end_date)

    def select_on_date(self, date):
        start_date = datetime(date.year, date.month, date.day)
        end_date = start_date + timedelta(days=1)
        return self.select_between_dates(start_date, end_date)
