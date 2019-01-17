import os
import pickle
import pandas as pd
import validator
from afregning import Afregning
from underretning import Underretning
from udtraek import Udtraek
from udligning import Udligning

class PSRM_CI_FT_BASE:

    def __init__(self, path, fname='PSRM_CI_FT_BASE.xlsx', multi_sheets=None):
        self.path = path
        if multi_sheets is not None:
            # preset data for the second data pull-out
            multi_sheets = {
              'PSRM Afregning': ['CI_FT_BASE.xlsx', 'Sheet1'],
              'Afregning_Underretning': ['Afregninger.xlsx', 'Sheet1'],
              'Udligning': ['Udligninger.xlsx', 'Sheet1'],
              'Udtræk': ['Udtræk.xlsx', 'Sheet1'],
            }
            sheets = {}
            for name in multi_sheets:
                if multi_sheets[name] is None:
                    continue
                sheet_path = os.path.join(self.path, multi_sheets[name][0])
                sheets[name] = pd.read_excel(sheet_path, multi_sheets[name][1])

            self.sheets = sheets

        elif fname is not None:
            self.fname = fname
            self.sheets = self._read_sheets(os.path.join(self.path, self.fname))

    def _read_sheets(self, fname):
        return pd.read_excel(fname, sheet_name=None)

    @property
    def udligning(self):
        # same as afregning
        rename = {'EFIFORDRINGIDENTIFIKATOR': 'NYMFID'}
        df = self.sheets['Udligning'].copy()
        validator.check_udligning(df)
        df.rename(columns=rename, inplace=True)
        return df

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
        rename = {'CUR_AMT': 'AMOUNT'}
        df.rename(columns=rename, inplace=True)
        return df

    @property
    def underretning(self):
        rename = {'EFIFORDRINGIDENTIFIKATOR': 'NYMFID'}
        df = self.sheets['Afregning_Underretning'].copy()
        validator.check_underretning(df)
        df.rename(columns=rename, inplace=True)
        return df

    @property
    def udtraeksdata(self):
        rename = {'EXTERNAL_OBLIGATION_ID' : 'NYMFID'}
        df = self.sheets['Udtræk'].copy()  # load and format PSRM Afregning
        df = df[~df['EXTERNAL_OBLIGATION_ID'].isnull()]  # remove events with no NYMFID
        df['EXTERNAL_OBLIGATION_ID'] = df['EXTERNAL_OBLIGATION_ID'].astype('int64')  # make ID INT
        df.rename(columns=rename, inplace=True)
        df['EFFECTIVE_DATE'] = pd.to_datetime(df['EFFECTIVE_DATE'])
        df['EFFECTIVE_DATE'] = df['EFFECTIVE_DATE'].dt.date
        df['TransDTTM_dt'] = pd.to_datetime(df['TRANSACTION_DATE'])
        df['TransDTTM_value'] = df['TransDTTM_dt'].view('int64')
        return df

    def get_by_id(self, id):
        """Given a NYMFID return afregn, underret, and udtraek"""
        afregn = self.afregning[self.afregning.NYMFID == id]
        underret = self.underretning[self.underretning.NYMFID == id]
        udtraek = self.udtraeksdata[self.udtraeksdata.NYMFID == id]
        udlign = self.udligning[self.udligning.NYMFID == id]
        return Afregning(afregn), Underretning(underret), Udligning(udlign), Udtraek(udtraek)

    def id_check(self, id):
        af, un, udl, ud = self.get_by_id(id)
        print('-'*80)
        print('Afregning\n')
        print(af)
        print('-'*80)
        print('Udligning\n')
        print(udl)
        print('-'*80)
        print('Underretning\n')
        print(un)
        print('-'*80)
        print('Udtræk\n')
        print(ud)
        print('-'*80)
        print('Sum of AFR: %.2f' % af.sum_amount)
        print('Sum of UDL: %.2f' % udl.sum_amount)
        print('Sum of UND: %.2f' % un.sum_amount)
        print('Sum of UDT: %.2f' % ud.sum_amount)
        print('-'*80)


if __name__ == '__main__':
    if os.path.exists('psrm.pkl'):
        with open('psrm.pkl', 'rb') as f:
            psrm = pickle.load(f)
    else:
        psrm = PSRM_CI_FT_BASE('../data')
        with open('psrm.pkl', 'wb') as f:
            pickle.dump(psrm, f)

    def get_random_nymfid(df):
        return df.sample(1).NYMFID.values[0]

    af, un, udl, ud = psrm.get_by_id(get_random_nymfid(psrm.afregning))
