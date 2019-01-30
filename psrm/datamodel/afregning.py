from psrm.datamodel.data import Data
from psrm.utils.utils import to_amount


class Afregning(Data):
    def __init__(self, df):
        self.df = df[['TRANSAKTIONSDATO', 'VIRKNINGSDATO', 'NYMFID', 'PAY_SEG_ID', 'PAY_EVENT_ID', 'AMOUNT', 'FT_TYPE_FLG']].copy()
        self.df.sort_values('TRANSAKTIONSDATO', inplace=True)
        self.df['AMOUNT'] = to_amount(self.df['AMOUNT'])

    def check_samtidighed(self, nymfid=None):
        if nymfid is not None:
            df = self.df[self.df.NYMFID == nymfid]
        else:
            df = self.df
        transaktions_dato = df.TRANSAKTIONSDATO.values
        return not (len(transaktions_dato) == len(set(transaktions_dato)))