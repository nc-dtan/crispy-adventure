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


def load_dw_rpt(path):
    """Load weird rpt from DW export."""
    with open(path, 'r') as f:
        lines = f.readlines()
    # custom header for now
    header = ['FordringID', 'FordringSaldo', 'InddrivelsesrenterAkk']
    # delete header and footer
    del lines[:2]
    del lines[-3:]
    arr = numpy.loadtxt(lines)
    df = pd.DataFrame(arr, columns=header)
    df['FordringID'] = df['FordringID'].astype('int64')
    rename = {'FordringID': 'NYMFID'}
    df.rename(columns=rename, inplace=True)
    return df


if __name__ == '__main__':
    from default_paths import path_v4, v4
    psrm = cache_psrm(path=path_v4, input=v4)
