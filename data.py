class Data:
    def __init__(self, df):
        self.df = df

    def __str__(self):
        return self.df.to_string()

    def __repr__(self):
        return self.df.to_string()

    @property
    def sum_amount(self):
        return round(sum(self.df['AMOUNT']), 2)
