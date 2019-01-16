from data import Data
from utils import is_integer, convert_from_str
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
        if isinstance(start_date, str):
            start_date = convert_from_str(start_date)
        if isinstance(end_date, str):
            end_date = convert_from_str(end_date)

        mask = (start_date <= self.df['TransDTTM']) & (self.df['TransDTTM'] <= end_date)
        return Udtraek(self.df[mask])

    def select_to_date(self, end_date):
        start_date = self.df['TransDTTM'].values[0]  # Sorted after dates, so first date is start date
        return Udtraek(self.select_between_dates(start_date, end_date))

    def select_from_date(self, start_date):
        end_date = self.df['TransDTTM'].values[-1]  # Sorted after dates, so last date is end date
        return Udtraek(self.select_between_dates(start_date, end_date))

    def select_on_date(self, date):
        if isinstance(date, str):
            date = convert_from_str(date)
        start_date = datetime(date.year, date.month, date.day)
        end_date = start_date + timedelta(days=1)
        return Udtraek(self.select_between_dates(start_date, end_date))
