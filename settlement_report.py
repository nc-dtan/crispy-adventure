from multiprocessing import Pool
import pandas as pd
from tqdm import tqdm
from default_paths import path_v4, v4
import psrm_utils
import totals


def settlement_by_id(nymfid):
    """Sum total by NYMFID from all report sheets."""
    global psrm
    acl = psrm.udtraeksdata.query('NYMFID == @nymfid')
    acl_HF = totals.sum_code(acl, code='DKHFEX') + totals.sum_partial(acl)
    udl_HF, udl_IR = totals.udl_split(nymfid, psrm)
    afr_HF, afr_IR = totals.afr_split(nymfid, psrm)
    return {'NYMFID': nymfid,
            'acl_HF': acl_HF,
            'acl_IR': totals.sum_code(acl),
            'und_udl_HF': udl_HF,
            'und_udl_IR': udl_IR,
            'und_afr_HF': afr_HF,
            'und_afr_IR': afr_IR, }


if __name__ == '__main__':
    global psrm
    psrm = psrm_utils.cache_psrm(path=path_v4, input=v4)
    cols = ['NYMFID', 'TRANSACTION_DATE', 'PARENT_ID', 'AMOUNT']
    acl = psrm_utils.time_cut(psrm.udtraeksdata[cols])
    ids = acl['NYMFID'].unique()
    ids = ids[:200]
    with Pool(7) as p:
        results = list(tqdm(p.imap(settlement_by_id, ids), total=len(ids)))
    settle = pd.DataFrame(results).set_index('NYMFID')
    settle.to_csv('settlement.csv', index=False)

    # compare our total with DW totals
    dw_settle = psrm_utils.load_dw_rpt('../Data/v4/fordringsaldo.rpt')
    compare = dw_settle.join(settle, on='NYMFID')
