from data import Data


class Afregning(Data):
    def __init__(self, df):
        self.df = df[['TRANSAKTIONSDATO', 'VIRKNINGSDATO', 'NYMFID', 'PAY_SEG_ID', 'AMOUNT', 'FT_TYPE_FLG']].copy()
        self.df.sort_values('TRANSAKTIONSDATO', inplace=True)
