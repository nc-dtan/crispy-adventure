from data import Data


class Udligning(Data):
    def __init__(self, df):
        self.df = df[['VIRKNINGSDATO', 'NYMFID', 'EFIBETALINGSIDENTIFIKATOR', 'AMOUNT', 'Daekningstype', 'DMIFordringTypeKategori']].copy()
        self.df.sort_values('VIRKNINGSDATO', inplace=True)
