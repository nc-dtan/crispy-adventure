from multiprocessing import Pool
import pandas as pd
from tqdm import tqdm
from default_paths import path_v4, v4
from utils import is_integer
import psrm_utils
import totals


def amount_sum(df):
    return df['AMOUNT'].sum().round(2)


def settlement(nymfid, acl_HF, udl_hf, udl_ir, afr_hf, afr_ir):
    """Sum total by NYMFID from all report sheets."""


    udl_HF, udl_IR = amount_sum(udl_hf), amount_sum(udl_ir)

    afr_HF, afr_IR = amount_sum(afr_hf), amount_sum(afr_ir)

    return {'NYMFID': nymfid,
            'acl_HF': acl_HF,
            'acl_IR': totals.sum_code(acl),
            'und_udl_HF': udl_HF,
            'und_udl_IR': udl_IR,
            'und_afr_HF': afr_HF,
            'und_afr_IR': afr_IR, }


def remaining_debt(x):
    debt = x.query('ISDEBT')['AMOUNT'].sum()
    payments = x.query('ISPAYMENT')['AMOUNT'].sum()
    interests = x.query('ISCATU')['AMOUNT'].sum()
    return debt - (payments + interests)

if __name__ == '__main__':
    psrm = psrm_utils.cache_psrm(path=path_v4, input=v4)
    cols = ['NYMFID', 'TRANSACTION_DATE', 'PARENT_ID', 'AMOUNT', 'CLAIMANT_ID']

    acl = psrm_utils.time_cut(psrm.udtraeksdata[cols])
    acl = acl.query('CLAIMANT_ID == 1229')  # only DR

    #acl.groupby('NYMFID')['AMOUNT'].sum().round(2).reset_index()

    # A: initial debt 'DKHFEX'  debt
    # B: sum(parent id is integer)  payments
    # C: summen catu 'DKCSHACT'  interests
    # SUM = A + (B - C)

    acl['ISDEBT'] = ((acl['PARENT_ID'] == 'DKHFEX') |
                     (acl['PARENT_ID'] == 'DKOGEX') |
                     (acl['PARENT_ID'] == 'DKIGEX') )
            # A
    acl['ISPAY'] = [is_integer(x) for x in acl['PARENT_ID'].values]  # B
    acl['ISCATU'] = acl['PARENT_ID'] == 'DKCSHACT'  # C

    assert ~acl.isnull().sum().sum()  # make sure that acl is complete
    debt = acl.query('ISDEBT').groupby('NYMFID')['AMOUNT'].sum().reset_index()
    debt.rename(columns={'AMOUNT': 'DEBT'}, inplace=True)
    debt.set_index('NYMFID', inplace=True)

    pays = acl.query('ISPAY').groupby('NYMFID')['AMOUNT'].sum().reset_index()
    pays.rename(columns={'AMOUNT': 'PAYMENT'}, inplace=True)
    pays.set_index('NYMFID', inplace=True)

    intr = acl.query('ISCATU').groupby('NYMFID')['AMOUNT'].sum().reset_index()
    intr.rename(columns={'AMOUNT': 'INTEREST'}, inplace=True)
    intr.set_index('NYMFID', inplace=True)

    rep = pd.DataFrame(acl['NYMFID'].unique(), columns=['NYMFID'])
    rep = pd.merge(rep, debt, on='NYMFID', how='left')
    rep = pd.merge(rep, pays, on='NYMFID', how='left')
    rep = pd.merge(rep, intr, on='NYMFID', how='left')

    rep = rep.fillna(0)
    rep['REMAIN'] = round(rep['DEBT'] + (rep['PAYMENT'] - rep['INTEREST']), 2)
    assert rep['NYMFID'].is_unique

    # find sums in underretninger (afr/udl)
    ids = rep.query('REMAIN != 0.')['NYMFID'].unique()

    udl = psrm.udligning
    udl = udl[udl['NYMFID'].isin(ids)]
    udl = udl.query('Daekningstype != "FORDKORR"')  # TODO: confirm
    udl['ISHF'] = udl['DMIFordringTypeKategori'] == 'HF'
    udl = udl.query('ISHF').groupby('NYMFID')['AMOUNT'].sum().reset_index()
    udl.rename(columns={'AMOUNT': 'UDL'}, inplace=True)
    udl.set_index('NYMFID', inplace=True)
    rep = pd.merge(rep, udl, on='NYMFID', how='left')

    afr = psrm.underretning
    afr = afr[afr['NYMFID'].isin(ids)]
    afr = afr.query('Daekningstype != "FORDKORR"')  # TODO: confirm
    afr['ISHF'] = afr['DMIFordringTypeKategori'] == 'HF'
    afr = afr.query('ISHF').groupby('NYMFID')['AMOUNT'].sum().reset_index()
    afr.rename(columns={'AMOUNT': 'AFR'}, inplace=True)
    afr.set_index('NYMFID', inplace=True)
    rep = pd.merge(rep, afr, on='NYMFID', how='left')
    rep.set_index('NYMFID', inplace=True)
    assert rep.index.is_unique
    rep.to_pickle('rep.pkl')
