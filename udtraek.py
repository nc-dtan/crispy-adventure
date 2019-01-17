from data import Data
from utils import is_integer, convert_date_from_str
from datetime import datetime, timedelta


class Udtraek(Data):
    def __init__(self, df):
        self.df = df[['TRANSACTION_DATE', 'EFFECTIVE_DATE', 'NYMFID', 'PARENT_ID', 'SIBLING_ID', 'AMOUNT', 'FT_TYPE_FLG']].copy()
        self.df.sort_values('TRANSACTION_DATE', inplace=True)

    @property
    def sum_amount(self):
        idx = [is_integer(a) for a in self.df['PARENT_ID']]
        return round(sum(self.df.loc[idx, 'AMOUNT']), 2)

    def sum_amount_partial(self, code='DKCSHACT'):
        return self.sum_amount - self.sum_amount_code(code)

    def sum_amount_code(self, code='DKCSHACT'):
        idx = self.df['PARENT_ID'] == code
        return round(sum(self.df.loc[idx, 'AMOUNT']), 2)

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
