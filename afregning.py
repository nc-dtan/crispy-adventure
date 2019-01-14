from data import Data


class Afregning(Data):
    def __init__(self, df):
        self.df = df[['TRANSAKTIONSDATO', 'VIRKNINGSDATO', 'NYMFID', 'PAY_SEG_ID', 'AMOUNT', 'FT_TYPE_FLG']]

    @property
    def sum_amount(self):
        return sum(self.df['AMOUNT'])
