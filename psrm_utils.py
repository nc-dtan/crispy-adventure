import os
import pickle
import pandas as pd
import numpy
from psrm_ci_ft_base import PSRM_CI_FT_BASE
from utils import to_amount


def time_cut(df, start_date='2000-01-01', end_date='2019-01-01'):
    """Return time slice between TRANSACTION_DATEs."""
    query = '@start_date <= TRANSACTION_DATE & TRANSACTION_DATE <= @end_date'
    return df.query(query)


def cache_psrm(cache='psrm.pkl', force=False, *args, **kwargs):
    """Load and create cached psrm class instance.
       psrm_kwargs is PSRM_CI_FT_BASE's arguments."""
    if not os.path.exists(cache) or force:
        print('Loading data from excel...')
        psrm = PSRM_CI_FT_BASE(*args, **kwargs)
        with open(cache, 'wb') as f:
            pickle.dump(psrm, f)
    else:
        print('Loading data from cache...')
        with open(cache, 'rb') as f:
            psrm = pickle.load(f)
    return psrm


def load_dw_rpt(path, cache='fordringsaldo.pkl'):
    """Load weird rpt from DW export."""
    if not os.path.exists(cache):
        arr = numpy.genfromtxt(path, skip_header=2, skip_footer=1)
        header = ['NYMFID', 'SALDO_HF', 'SALDO_RENTER']  # custom header
        df = pd.DataFrame(arr, columns=header)
        df['NYMFID'] = df['NYMFID'].astype('int64')
        df['SALDO_HF'] = to_amount(df['SALDO_HF'])
        df['SALDO_RENTER'] = to_amount(df['SALDO_RENTER'])
        df.set_index('NYMFID', inplace=True)
        df.to_pickle(cache)
    else:
        df = pd.read_pickle(cache)
    return df


if __name__ == '__main__':
    from default_paths import path_v4, v4
    psrm = cache_psrm(path=path_v4, input=v4)
