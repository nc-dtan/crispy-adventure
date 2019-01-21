import os, pickle, datetime
import pandas, git, psrm_ci_ft_base, tqdm

def load_psrm(path=None, cache_name ='psrm.pkl'):
    """Load and create cached psrm class instance."""
    psrm_path = os.path.join(path, cache_name)
    if os.path.exists(psrm_path):
        with open(psrm_path, 'rb') as f:
            psrm = pickle.load(f)
    else:
        psrm = psrm_ci_ft_base.PSRM_CI_FT_BASE(path, multi_sheets=True)
        with open(psrm_path, 'wb') as f:
            pickle.dump(psrm, f)
    return psrm

def total(df=None):
    return df.groupby('NYMFID')['AMOUNT'].sum().round(2)
    

psrm = load_psrm('../Data/v4/')
afr = total(psrm.afregning).rename('afr')
und = total(psrm.underretning).rename('und')
udl = total(psrm.udligning).rename('udl')
