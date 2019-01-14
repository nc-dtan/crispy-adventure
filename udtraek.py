from data import Data
from utils import is_integer


class Udtraek(Data):
    def __init__(self, df):
        self.df = df[['TransDTTM', 'EffectiveDate', 'NYMFID', 'Parent', 'Sibling_ID', 'AMOUNT', 'FT_FLG']]

    @property
    def sum_amount(self):
        idx = [is_integer(a) for a in self.df['Parent']]
        return sum(self.df.loc[idx, 'AMOUNT'])
