from utils import is_integer


def sum_amount(df):
    idx = [is_integer(a) for a in df['PARENT_ID']]
    if idx[0] is False and len(idx) == 1:
        return 0
    else:
        return round(sum(df.loc[idx, 'AMOUNT']), 2)


def sum_code(df, code='DKCSHACT'):
    idx = df['PARENT_ID'] == code
    if idx.values[0] is False and len(idx) == 1:
        return 0
    else:
        return round(sum(df.loc[idx, 'AMOUNT']), 2)


def sum_partial(df):
    return sum_amount(df) - sum_code(df)

# A: initial debt 'DKHFEX'
# B: sum(parent id is integer)
# C: summen catu 'DKCSHACT'
# SUM = A + (B - C)


# def udl_split(df):
#     """Get total udligning sum for NYMFID (underretning)."""
#     hf = df.query('DMIFordringTypeKategori == "HF"')
#     ir = df.query('DMIFordringTypeKategori != "HF"')
#     return hf['AMOUNT'].sum().round(2), ir['AMOUNT'].sum().round(2)
#
#
# def afr_split(df):
#     """Get total afregning sum for NYMFID (underretning)."""
#     hf = df.query('DMIFordringTypeKategori == "HF"')
#     ir = df.query('DMIFordringTypeKategori != "HF"')
#     return hf['AMOUNT'].sum().round(2), ir['AMOUNT'].sum().round(2)
