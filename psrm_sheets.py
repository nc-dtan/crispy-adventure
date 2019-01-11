import os
import pandas as pd
import datetime as dt

path = '../data'
fname = 'PSRM_CI_FT_BASE.xlsx'
sheets = pd.read_excel(os.path.join(path, fname))


def is_date(df, col):
    """Check the date is on the format: YYYY-MM-DD"""
    return (df[col].str.len() != 10).sum() == 0


def is_int_positive(df, col):
    """Check if the int overflows"""
    return (df[col] < 0).sum() == 0


def is_only_payment_types(df, col):
    return set(df[col].unique()) == {'PX', 'PS'}


def _check_afregningsdata(df):
    assert is_date(df, 'VIRKNINGSDATO')
    assert is_int_positive(df, 'NYMFID')
    assert is_int_positive(df, 'PAY_SEG_ID')
    assert is_int_positive(df, 'PAY_EVENT_ID')
    assert is_int_positive(df, 'BANKID')
    assert is_only_payment_types(df, 'FT_TYPE_FLG')


def has_missing_values(df, col):
    return df[col].isnull().sum() != 0


def is_type(df, col, type):
    return df[col].dtype == dtype(type)


def get_afregningsdata(sheets):
    # Afregningsdata
    df = sheets['PSRM Afregning'].copy()  # load and format PSRM Afregning
    df = df[~df['NYMFID'].isnull()]  # remove the few events with no NYMFID
    df.loc[:, 'NYMFID'] = df['NYMFID'].astype('int64')  # convert ID to correct type
    df.loc[:, 'PAY_SEG_ID'] = df['PAY_SEG_ID'].astype('int64')  # convert ID to correct type
    df.loc[:, 'PAY_EVENT_ID'] = df['PAY_EVENT_ID'].astype('int64')  # convert ID to correct type
    df.loc[:, 'BANKID'] = df['BANKID'].astype('int64')  # convert ID to correct type
    df['VIRKNINGSDATO'] = df['VIRKNINGSDATO'].str[:10]  # cut meaningless timestamp off
    _check_afregningsdata(df)
    df.loc[: ,'ISMATCHED_BOOL'] = df['ISMATCHED'] != 'NO'  # bool value for PSRM match
    return df


# unique error IDs from 'Afregning'
def get_NyMF_errors(df):
    return df[~df['ISMATCHED_BOOL']]['NYMFID'].unique()


def get_underretning(sheets):
    df2 = sheets['Afregning_Underretning'].copy()
    assert is_date(df2, 'VIRKNINGSDATO')
    assert not has_missing_values(df2, 'EFIFORDRINGIDENTIFIKATOR')  # check no missing IDs
    assert is_type(df2, 'EFIFORDRINGIDENTIFIKATOR', 'int64')
    return df2


# Udtræksdata
def format_udtraeksdata(sheets):
    df3 = sheets['Udtræk NCO'].copy()  # load and format PSRM Afregning
    df3 = df3[~df3['NyMF_ID'].isnull()]  # remove events with no NYMFID
    df3['NyMF_ID'] = df3['NyMF_ID'].astype('int64')  # make ID INT
    df3['TransDTTM_dt'] = pd.to_datetime(df3['TransDTTM'])
    df3['TransDTTM_value'] = df3['TransDTTM_dt'].view('int64')
    return df3
