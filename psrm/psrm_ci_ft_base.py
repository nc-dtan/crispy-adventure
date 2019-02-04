import os
import pickle
import pandas as pd
from psrm import validator
from psrm.datamodel.afregning import Afregning
from psrm.datamodel.underretning import Underretning
from psrm.datamodel.udtraek import Udtraek
from psrm.datamodel.udligning import Udligning
from psrm.utils import utils
from psrm.errors.errors import NyMFError

class PSRM_CI_FT_BASE:

    def __init__(self, path=None, input=None):
        utils.check_requirements()
        self.path = path
        self._udligning = None
        self._afregning = None
        self._underretning = None
        self._udtraeksdata = None
        sheets = {}
        for name in input:
            data = input[name][0]
            sname = input[name][1]
            if data is None:
                continue
            if type(data) == str:
                if data.split('.')[-1] != 'xlsx':
                    raise NotImplementedError('not a Excel file')
                sheet_path = os.path.join(self.path, data)
                sheets[name] = pd.read_excel(sheet_path, sname)
            if type(data) != str:
                if sname is not None:
                    raise NotImplementedError('multi sheets not working')
                dfs = []
                for x in data:
                    fpath = os.path.join(self.path, x)
                    if x.split('.')[-1] == 'txt':
                        dfs.append(pd.read_csv(fpath, sep=';'))
                    if x.split('.')[-1] == 'csv':
                        dfs.append(pd.read_csv(fpath, sep=','))
                sheets[name] = pd.concat(dfs)

            self.sheets = sheets


    def _get_udligning(self):
        # same as afregning
        rename = {'EFIFORDRINGIDENTIFIKATOR': 'NYMFID'}
        df = self.sheets['Udligning'].copy()
        validator.check_udligning(df)
        df.rename(columns=rename, inplace=True)
        self._udligning = df
        return self._udligning

    @property
    def udligning(self):
        if self._udligning is None:
            return self._get_udligning()
        return self._udligning

    def _get_afregning(self):
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
        self._afregning = df
        return self._afregning

    @property
    def afregning(self):
        if self._afregning is None:
            return self._get_afregning()
        return self._afregning

    def _get_underretning(self):
        rename = {'EFIFORDRINGIDENTIFIKATOR': 'NYMFID'}
        df = self.sheets['Afregning_Underretning'].copy()
        validator.check_underretning(df)
        df.rename(columns=rename, inplace=True)
        self._underretning = df
        return self._underretning

    @property
    def underretning(self):
        if self._underretning is None:
            return self._get_underretning()
        return self._underretning

    def _get_udtraeksdata(self):
        rename = {'EXTERNAL_OBLIGATION_ID' : 'NYMFID'}
        df = self.sheets['Udtræk'].copy()  # load and format PSRM Afregning
        df = df[~df['EXTERNAL_OBLIGATION_ID'].isnull()]  # remove with no NYMFID
        df['EXTERNAL_OBLIGATION_ID'] = df['EXTERNAL_OBLIGATION_ID'].astype('int64')  # make ID INT
        df.rename(columns=rename, inplace=True)
        df['EFFECTIVE_DATE'] = pd.to_datetime(df['EFFECTIVE_DATE'])
        df['EFFECTIVE_DATE'] = df['EFFECTIVE_DATE'].dt.date
        df['TransDTTM_dt'] = pd.to_datetime(df['TRANSACTION_DATE'])
        df['TransDTTM_value'] = df['TransDTTM_dt'].view('int64')
        self._udtraeksdata = df
        return self._udtraeksdata

    @property
    def udtraeksdata(self):
        if self._udtraeksdata is None:
            return self._get_udtraeksdata()
        return self._udtraeksdata

    def get_by_id(self, nymfid):
        """Given a NYMFID return afregn, underret, and udtraek"""
        afregn = self.afregning.query('NYMFID == @nymfid')
        underret = self.underretning.query('NYMFID == @nymfid')
        udtraek = self.udtraeksdata.query('NYMFID == @nymfid')
        udlign = self.udligning.query('NYMFID == @nymfid')
        if not len(afregn) and not len(underret) and not len(udtraek) and not len(udlign):
            raise NyMFError(f'NyMF id is not found: {nymfid}')
        return Afregning(afregn), Underretning(underret), Udligning(udlign), Udtraek(udtraek)

    def check_id(self, nymfid):
        af, un, udl, ud = self.get_by_id(nymfid)
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
        print('Sum of UDT: %.2f' % ud.sum_amount())
        print('-'*80)


if __name__ == '__main__':
    from psrm.utils.psrm_utils import cache_psrm
    import psrm

    # load psrm data with cache
    psrm = cache_psrm(path=psrm.path_v4, input=psrm.v4)

    # make a nicely formatted excel sheet
    utils.df_to_excel(psrm.afregning.sample(50))

    # get a single random id
    def get_random_nymfid(df):
        return df.sample(1).NYMFID.values[0]
    af, un, udl, ud = psrm.get_by_id(get_random_nymfid(psrm.afregning))
