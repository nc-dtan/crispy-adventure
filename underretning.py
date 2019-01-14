from data import Data


class Underretning(Data):
    def __init__(self, df):
        self.df = df[['VIRKNINGSDATO', 'NYMFID', 'EFIBETALINGSIDENTIFIKATOR', 'AMOUNT', 'Daekningstype']]

    @property
    def sum_amount(self):
        return sum(self.df['AMOUNT'])
