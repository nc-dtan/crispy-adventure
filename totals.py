from utils import is_integer


def sum_amount(df):
    idx = [is_integer(a) for a in df['PARENT_ID']]
    if idx[0] is False and len(idx) == 1:
        return 0
    else:
        return round(sum(df.loc[idx, 'AMOUNT']), 2)


def sum_partial(df):
    return sum_amount(df) - sum_code(df)


def sum_code(df, code='DKCSHACT'):
    idx = df['PARENT_ID'] == code
    if idx.values[0] is False and len(idx) == 1:
        return 0
    else:
        return round(sum(df.loc[idx, 'AMOUNT']), 2)


def udl_split(nymfid, psrm):
    """Get total udligning sum for NYMFID (underretning)."""
    df = psrm.udligning.query('NYMFID == @nymfid')
    df = df.query('Daekningstype != "FORDKORR"')  # TODO: need to test
    hf = df.query('DMIFordringTypeKategori == "HF"')
    ir = df.query('DMIFordringTypeKategori != "HF"')
    return hf['AMOUNT'].sum().round(2), ir['AMOUNT'].sum().round(2)


def afr_split(nymfid, psrm):
    """Get total afregning sum for NYMFID (underretning)."""
    df = psrm.underretning.query('NYMFID == @nymfid')
    df = df.query('Daekningstype != "FORDKORR"')  # TODO: need to test
    hf = df.query('DMIFordringTypeKategori == "HF"')
    ir = df.query('DMIFordringTypeKategori != "HF"')
    return hf['AMOUNT'].sum().round(2), ir['AMOUNT'].sum().round(2)
