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
        df.loc[:, 'ISMATCHED_BOOL'] = df['ISMATCHED'] != 'NO'  # bool value for PSRM match
        return df

    @property
    def NyMF_errors(self):
        af = self.afregning[['NYMFID', 'ISMATCHED']]
        errors = pd.DataFrame(af['NYMFID'].drop_duplicates())
        errors['ISMATCHED'] = True
        for nymfid, g in af.groupby('NYMFID'):
            if any(g['ISMATCHED'] == 'NO'):
                errors.loc[errors['NYMFID']==nymfid,'ISMATCHED'] = False
        assert errors['NYMFID'].is_unique
        return errors

    @property
    def underretning(self):
        df = self.sheets['Afregning_Underretning'].copy()
        validator.check_underretning(df)
        df.rename(columns={'EFIFORDRINGIDENTIFIKATOR': 'NYMFID'}, inplace=True)
        return df

    @property
    def udtraeksdata(self):
        df = self.sheets['Udtræk NCO'].copy()  # load and format PSRM Afregning
        df = df[~df['NyMF_ID'].isnull()]  # remove events with no NYMFID
        df['NyMF_ID'] = df['NyMF_ID'].astype('int64')  # make ID INT
        df.rename(columns={'NyMF_ID': 'NYMFID'}, inplace=True)
        df['TransDTTM_dt'] = pd.to_datetime(df['TransDTTM'])
        df['TransDTTM_value'] = df['TransDTTM_dt'].view('int64')
        return df

    def get_by_id(self, id):
        """Given a NYMFID return afregn, underret, and udtraek"""
        afregn = self.afregning[self.afregning.NYMFID == id]
        underret = self.underretning[self.underretning.NYMFID == id]
        udtraek = self.udtraeksdata[self.udtraeksdata.NYMFID == id]
        return afregn, underret, udtraek


if __name__ == '__main__':
    psrm = PSRM_CI_FT_BASE('../data')
    afregning = psrm.afregning
    def get_random_nymfid(df):
        return df.sample(1).NYMFID.values[0]

    data = psrm.get_by_id(get_random_nymfid(afregning))
    print('Afregning\n', data[0])
    print('Underretning\n', data[1])
    print('Udtraek\n', data[2])
