from numpy import dtype

def is_date(df, col):
    """Check the date is on the format: YYYY-MM-DD"""
    return (df[col].str.len() != 10).sum() == 0


def is_int_positive(df, col):
    """Check if the int overflows"""
    return (df[col] < 0).sum() == 0


def is_only_payment_types(df, col):
    return set(df[col].unique()) == {'PX', 'PS'}


def has_missing_values(df, col):
    return df[col].isnull().sum() != 0


def is_type(df, col, type):
    return df[col].dtype == dtype(type)


def check_afregningsdata(df):
    assert is_date(df, 'VIRKNINGSDATO')
    assert is_int_positive(df, 'NYMFID')
    assert is_int_positive(df, 'PAY_SEG_ID')
    assert is_int_positive(df, 'PAY_EVENT_ID')
    assert is_int_positive(df, 'BANKID')
    assert is_only_payment_types(df, 'FT_TYPE_FLG')


def check_underretning(df):
    assert is_date(df, 'VIRKNINGSDATO')
    assert not has_missing_values(df, 'EFIFORDRINGIDENTIFIKATOR')  # check no missing IDs
    assert is_type(df, 'EFIFORDRINGIDENTIFIKATOR', 'int64')


def check_udligning(df):
    assert is_date(df, 'VIRKNINGSDATO')
    assert not has_missing_values(df, 'EFIFORDRINGIDENTIFIKATOR')  # check no missing IDs
    assert is_type(df, 'EFIFORDRINGIDENTIFIKATOR', 'int64')
