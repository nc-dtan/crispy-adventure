import os
import pickle
from psrm_ci_ft_base import PSRM_CI_FT_BASE

def cache_psrm(cache ='psrm.pkl', psrm_kwargs=None, force=False):
    """Load and create cached psrm class instance.
       psrm_kwargs is PSRM_CI_FT_BASE's arguments."""

    if not os.path.exists(cache) or force == True:
        psrm = PSRM_CI_FT_BASE(**psrm_kwargs)
        with open(cache, 'wb') as f:
            pickle.dump(psrm, f)
    else:
        with open(cache, 'rb') as f:
            psrm = pickle.load(f)
    return psrm

if __name__ == '__main__':
    from default_paths import path_v4, v4
    psrm = cache_psrm(psrm_kwargs={'path': path_v4, 'input': v4})
