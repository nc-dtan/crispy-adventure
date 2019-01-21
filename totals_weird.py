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
    

psrm = load_psrm('../Data/v3/')
afr = total(psrm.afregning).rename('afr')
und = total(psrm.underretning).rename('und')
udl = total(psrm.udligning).rename('udl')
df = psrm.afregning.join(afr, on='NYMFID')
df = df.join(und, on='NYMFID').join(udl, on='NYMFID')
df = df.query('(afr != udl) & (afr == und)')
df['2x'] = df['afr'] == (df['udl'] / 2).round(2)
wd = df[~df['2x']][['NYMFID', 'afr', 'und', 'udl']]
missing = wd[wd['udl'].isnull()]  # n=69
wd = wd[~wd['udl'].isnull()]

ud_sums = []
for i in wd.NYMFID.values:
    af, un, ul, ud = psrm.get_by_id(i)
    b = ul.sum_amount == -ud.sum_amount
    print(b)
    ud_sums.append(b)
wd['ud_sums'] = ud_sums
