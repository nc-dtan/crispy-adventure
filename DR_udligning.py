import numpy
import pandas
from tqdm import tqdm
from psrm_utils import cache_psrm
from default_paths import path_v4, v4
from utils import is_integer
from cachetools import cached
import swifter
import multiprocessing
from utils import d


# df = psrm.afregning.join(afr, on='NYMFID')
# df = df.join(und, on='NYMFID').join(udl, on='NYMFID')
# df = df.query('(afr != udl) & (afr == und)')
# df['2x'] = df['afr'] == (df['udl'] / 2).round(2)
# wd = df[~df['2x']][['NYMFID', 'afr', 'und', 'udl']]
# missing = wd[wd['udl'].isnull()]  # n=69
# wd = wd[~wd['udl'].isnull()]
# ud_sums = []
# for i in wd.NYMFID.values:
#     af, un, ul, ud = psrm.get_by_id(i)
#     b = ul.sum_amount == -ud.sum_amount
#     print(b)
#     ud_sums.append(b)
# wd['ud_sums'] = ud_sums


def udligning_debt_interest(nymfid, psrm):
    df = psrm.udligning.query('NYMFID == @nymfid')
    hf = df.query('DMIFordringTypeKategori == "HF"')
    ir = df.query('DMIFordringTypeKategori != "HF"')
    return hr['AMOUNT'].sum()

def total(df=None):
    return df.groupby('NYMFID')['AMOUNT'].sum().round(2)


def find_payid(payid):
    global acl
    af = acl.query('PAY_EVENT_ID == @payid')
    if len(af) == 0:
        af = acl.query('PAY_ID == @payid')
    idx = [is_integer(a) for a in af['PARENT_ID']]
    af = af[idx]
    if len(af) == 0:
        return numpy.NaN
    if len(af['TRANSACTION_DATE'].unique()) == 1:
        return af['TRANSACTION_DATE'].iloc[0]
    else:
        return numpy.NaN
    raise NotImplementedError


@cached(cache={})
def get_udligning(psrm):
    afr_tot = total(psrm.afregning).rename('afr_total')
    udl_tot = total(psrm.udligning).rename('udl_total')
    udl = psrm.udligning.join(udl_tot, on='NYMFID')
    udl = udl.join(afr_tot, on='NYMFID')
    udl = udl[~udl['afr_total'].isnull()]
    udl = udl.query('Daekningstype != "FORDKORR"')
    udl = udl.query('(afr_total != udl_total)').copy()
    udl['double'] = udl['afr_total'] == (udl['udl_total'] / 2).round(2)
    return udl  # .head(20000)


@cached(cache={})
def get_acl(psrm):
    return psrm.udtraeksdata[~psrm.udtraeksdata['PAY_ID'].isnull()]


def get_afs(payids):
    with multiprocessing.Pool(7) as p:
        return list(tqdm(p.imap(find_payid, payids), total=len(payids)))


if __name__ == '__main__':
    psrm = cache_psrm(path=path_v4, input=v4)
    udl = get_udligning(psrm)
    global acl
    acl = get_acl(psrm)
    payids = udl['EFIBETALINGSIDENTIFIKATOR'].values
    udl['TRANSACTION_DATE'] = get_afs(payids)

    df = udl.query('~double & ~TRANSACTION_DATE.isnull()')
    df = df[df['TRANSACTION_DATE'] <= '2018-12-31']


#     for idx, efi in tqdm(enumerate(udligning['EFIBETALINGSIDENTIFIKATOR'])):
#         af += [find_payid(efi)]
#     af = pandas.Serie s(af)
    # af = udligning['EFIBETALINGSIDENTIFIKATOR'].swifter.apply(find_payid)
    # make a nicely formatted excel sheet
    # utils.df_to_excel(psrm.afregning.sample(50))
# NYMFID==11000002839
#
