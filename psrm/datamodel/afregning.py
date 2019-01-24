from psrm.datamodel.data import Data
from psrm.utils.utils import to_amount


class Afregning(Data):
    def __init__(self, df):
        self.df = df[['TRANSAKTIONSDATO', 'VIRKNINGSDATO', 'NYMFID', 'PAY_SEG_ID', 'PAY_EVENT_ID', 'AMOUNT', 'FT_TYPE_FLG']].copy()
        self.df.sort_values('TRANSAKTIONSDATO', inplace=True)
        self.df['AMOUNT'] = to_amount(self.df['AMOUNT'])
