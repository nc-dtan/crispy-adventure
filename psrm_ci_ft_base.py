import os
import pandas as pd
import validator


class PSRM_CI_FT_BASE:

    def __init__(self, path, fname='PSRM_CI_FT_BASE.xlsx'):
        self.path = path
        self.fname = fname
        self.sheets = self._read_sheets(os.path.join(self.path, self.fname))

    def _read_sheets(self, fname):
        return pd.read_excel(fname, sheet_name=None)

    @property
    def afregning(self):
        df = self.sheets['PSRM Afregning'].copy()  # load and format PSRM Afregning
        df = df[~df['NYMFID'].isnull()]  # remove the few events with no NYMFID
        df.loc[:, 'NYMFID'] = df['NYMFID'].astype('int64')  # convert ID to correct type
        df.loc[:, 'PAY_SEG_ID'] = df['PAY_SEG_ID'].astype('int64')  # convert ID to correct type
        df.loc[:, 'PAY_EVENT_ID'] = df['PAY_EVENT_ID'].astype('int64')  # convert ID to correct type
        df.loc[:, 'BANKID'] = df['BANKID'].astype('int64')  # convert ID to correct type
        df['VIRKNINGSDATO'] = df['VIRKNINGSDATO'].str[:10]  # cut meaningless timestamp off
        validator.check_afregningsdata(df)
        df.loc[: ,'ISMATCHED_BOOL'] = df['ISMATCHED'] != 'NO'  # bool value for PSRM match
        self.afregning = df
        return self.afregning

    @property
    def NyMF_errors(self):
        return self.afrening[~self.afrening['ISMATCHED_BOOL']]['NYMFID'].unique()

    @property
    def underretning(self):
        df = self.sheets['Afregning_Underretning'].copy()
        validator.check_underretning(df)
        return df

    @property
    def udtraeksdata(self):
        df = self.sheets['Udtræk NCO'].copy()  # load and format PSRM Afregning
        df = df[~df['NyMF_ID'].isnull()]  # remove events with no NYMFID
        df['NyMF_ID'] = df['NyMF_ID'].astype('int64')  # make ID INT
        df['TransDTTM_dt'] = pd.to_datetime(df['TransDTTM'])
        df['TransDTTM_value'] = df['TransDTTM_dt'].view('int64')
        return df


if __name__ == '__main__':
    psrm = PSRM_CI_FT_BASE('../data')
    afregning = psrm.afregning
