import os
import pickle
import pandas as pd
import numpy
from psrm_ci_ft_base import PSRM_CI_FT_BASE


def cache_psrm(cache='psrm.pkl', force=False, *args, **kwargs):
    """Load and create cached psrm class instance.
       psrm_kwargs is PSRM_CI_FT_BASE's arguments."""

    if not os.path.exists(cache) or force:
        psrm = PSRM_CI_FT_BASE(*args, **kwargs)
        with open(cache, 'wb') as f:
            pickle.dump(psrm, f)
    else:
        with open(cache, 'rb') as f:
            psrm = pickle.load(f)
    return psrm


def load_dw_rpt(path, cache='fordringsaldo.pkl'):
    """Load weird rpt from DW export."""
    if not os.path.exists(cache):
        arr = numpy.genfromtxt(path, skip_header=2, skip_footer=1)
        header = ['NYMFID', 'FH_Saldo', 'IR_Saldo']  # custom header
        df = pd.DataFrame(arr, columns=header)
        df['NYMFID'] = df['NYMFID'].astype('int64')
        df.to_pickle(cache)
    else:
        df = pd.read_pickle(cache)
    return df


if __name__ == '__main__':
    from default_paths import path_v4, v4
    psrm = cache_psrm(path=path_v4, input=v4)
