import os, pickle, datetime
import pandas, git, psrm_ci_ft_base

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

dups = []
for i in tqdm.tqdm(df['NYMFID'].values):
    g = psrm.udligning.query('NYMFID == @i')
    g['AMOUNT'] = g['AMOUNT'].round(2)
    dups.append(g.duplicated('AMOUNT').any())
df['dups'] = dups

n_tot = 5811

# n=4266
df[df['2x']]

# n=4243
df[df['2x'] & df['dups']]

# 23 of wierd cases, prob time diff
# these matches udtraek
df[df['2x'] & ~df['dups']]

# conclusion
# most of errors come from 2x events
psrm.id_check(df[df['2x'] & ~df['dups']]['NYMFID'].sample().iloc[0])

weird = df[~df['2x']][['NYMFID', 'afr', 'und', 'udl']]
