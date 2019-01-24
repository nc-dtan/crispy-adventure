from psrm.datamodel.data import Data
from psrm.utils.utils import to_amount


class Udligning(Data):
    def __init__(self, df):
        self.df = df[['VIRKNINGSDATO', 'NYMFID', 'EFIBETALINGSIDENTIFIKATOR', 'AMOUNT', 'Daekningstype', 'DMIFordringTypeKategori']].copy()
        self.df.sort_values('VIRKNINGSDATO', inplace=True)
        self.df['AMOUNT'] = to_amount(self.df['AMOUNT'])
