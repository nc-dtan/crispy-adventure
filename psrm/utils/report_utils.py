import pandas as pd
from psrm.utils import utils
from psrm.enums.justeringstype import JusteringsType as JT


def annotate_acl(acl, end_date='2018-12-29', claimant=None):
    """Timecut and annotate ACL-udtraek."""
    end_date = pd.to_datetime(end_date)  # cutdate
    acols = ['NYMFID', 'EFFECTIVE_DATE', 'TRANSACTION_DATE',
             'PARENT_ID', 'AMOUNT', 'CLAIMANT_ID']
    acl = acl[acols].copy()
    acl['EFFECTIVE_DATE'] = pd.to_datetime(acl['EFFECTIVE_DATE'])
    acl['TRANSACTION_DATE'] = pd.to_datetime(acl['TRANSACTION_DATE'])
    acl.query('EFFECTIVE_DATE < @end_date', inplace=True)
    if claimant is not None:
        acl.query('CLAIMANT_ID == @claimant', inplace=True)  # CLAMAINT
    acl['ISDEBT'] = ((acl['PARENT_ID'] == JT.DKHFEX.value) |
                     (acl['PARENT_ID'] == JT.DKOGEX.value) |
                     (acl['PARENT_ID'] == JT.DKOREX.value) |
                     (acl['PARENT_ID'] == JT.DKIGEX.value) )
    acl['ISPAY'] = [utils.is_integer(x) for x in acl['PARENT_ID'].values]
    acl['ISCATU'] = acl['PARENT_ID'] == JT.DKCSHACT.value
    assert ~acl.isnull().sum().sum()  # check no nulls in acl
    return acl


def annotate_udl(udl, end_date='2018-12-29'):
    """Prepare udligning underretning."""
    end_date = pd.to_datetime(end_date)  # cutdate
    udl = udl.copy()
    udl['VIRKNINGSDATO'] = pd.to_datetime(udl['VIRKNINGSDATO'])
    udl.query('VIRKNINGSDATO < @end_date', inplace=True)
    udl.query('~Daekningstype.isnull()', inplace=True)
    udl['ISHF'] = udl['DMIFordringTypeKategori'].isin(['IG', 'OG', 'HF', 'OR'])
    return udl[['NYMFID', 'ISHF', 'AMOUNT', 'VIRKNINGSDATO']]


def annotate_afr(afr, end_date='2018-12-29'):
    """Prepare afregning underretning."""
    end_date = pd.to_datetime(end_date)  # cutdate
    afr = afr.copy()
    afr['VIRKNINGSDATO'] = pd.to_datetime(afr['VIRKNINGSDATO'])
    afr.query('VIRKNINGSDATO < @end_date', inplace=True)
    afr.query('~Daekningstype.isnull()', inplace=True)
    afr['ISHF'] = afr['DMIFordringTypeKategori'].isin(['IG', 'OG', 'HF', 'OR'])
    return afr[['NYMFID', 'ISHF', 'AMOUNT']]


def acl_debt(acl):
    """Calculate the initial debt per NYMFID."""
    debt = acl.query('ISDEBT').groupby('NYMFID')
    debt = debt['AMOUNT'].sum().round(2).reset_index()
    debt.rename(columns={'AMOUNT': 'DEBT'}, inplace=True)
    debt.set_index('NYMFID', inplace=True)
    return debt


def acl_pay(acl):
    """Calculate sum of all payments per NYMFID."""
    pays = acl.query('ISPAY').groupby('NYMFID')
    pays = pays['AMOUNT'].sum().round(2).reset_index()
    pays.rename(columns={'AMOUNT': 'PAYMENT'}, inplace=True)
    pays['PAYMENT'] = -pays['PAYMENT']
    pays.set_index('NYMFID', inplace=True)
    return pays


def acl_interest(acl):
    """Calculate sum of all interests on NYMFID."""
    intr = acl.query('ISCATU').groupby('NYMFID')
    intr = intr['AMOUNT'].sum().round(2).reset_index()
    intr.rename(columns={'AMOUNT': 'ACL_IR'}, inplace=True)
    intr['ACL_IR'] = -intr['ACL_IR']
    intr.set_index('NYMFID', inplace=True)
    return intr


def sum_NYMF(df, HF=True):
    """Calculate the total per NYMFID on HF/~HF."""
    cond = 'ISHF'
    if HF is not True:
        cond = '~' + cond
    gr = df.query(cond).groupby('NYMFID')
    gr = gr['AMOUNT'].sum().round(2).reset_index()
    return gr.set_index('NYMFID')


def saldo_DR(path='../Data/Fordringer med diff iflg DR.xlsx'):
    """Load DR's total data."""
    dr = pd.read_excel(path)
    del dr['Ventende_beløb_TS2']
    del dr['Fakturanummer']
    del dr['Saldo_PSRM']  # tested, same as Saldo in 20181231_exp_psrm....
    dr['Saldo_DR'] = dr['Saldo_DR'].round(2)
    dr['Difference'] = dr['Difference'].round(2)
    dr.rename(columns={'Fordringsid': 'NYMFID'}, inplace=True)
    assert dr['NYMFID'].is_unique
    return dr


def saldo_PSRM(path='../Data/20181231_exp_psrm_dr_afstemningsleverance.txt'):
    """Load PSRM's total data."""
    df = pd.read_csv(path, sep=';')
    df['Saldo'] = df['Saldo'].round(2)
    del df['HovedfordringID']
    del df['FordringshaverReference']
    del df['Udtraeksdato']
    del df['#FordringshaverKode']
    df.rename(columns={'FordringID': 'NYMFID'}, inplace=True)
    return df
