import pandas as pd
import psrm
from psrm.utils import psrm_utils
from report_utils import *


# Assumptions
# ------------
# - Limited to claimant id 1229 (DR)
# - Main debt, OG and IG is on seperate NYMFID
# - ACL udtraek is cut to all time before 2018-12-28 (EFFECTIVE_DATE)
# - underetninger are cut to all time before 2018-12-28 (VIRKNINGSDATO)
# - Limited to NYMFIDs where ACL reports debt remaining
#
#
# HF remaining debt per NYMFID calculation
# ----------------------------------------
# DEBT = 'DKHFEX' or 'DKOGEX' or 'DKIGEX' (the initial debt)
# PAYMENT = PARENT_ID is integer (debitor payments)
# INTEREST = 'DKCSHACT' (the catu calculation)
# DEBT_REMAIN = DEBT - PAYMENT + INTEREST

# Load data
ps = psrm.psrm_utils.cache_psrm(path=psrm.path_v4, input=psrm.v4)
DR_ID = psrm.enums.fordringshaver.FordringsHaver.DR.value['Claimant_ID']
acl = annotate_acl(ps.udtraeksdata, claimant=DR_ID)
debt = acl_debt(acl)
pays = acl_pay(acl)
intr = acl_interest(acl)
udl = annotate_udl(ps.udligning)
afr = annotate_afr(ps.underretning)

# Create report - one row per NYMFID
rep = pd.DataFrame(acl['NYMFID'].unique(), columns=['NYMFID'])
rep = pd.merge(rep, debt, on='NYMFID', how='left')
rep = pd.merge(rep, pays, on='NYMFID', how='left')
rep = pd.merge(rep, intr, on='NYMFID', how='left')
rep = rep.fillna(0)

# Calculate remaining debt per NYMFID
rep['DEBT_REMAIN'] = (rep['DEBT']-rep['PAYMENT']+rep['INTEREST']).round(2)
rep['ACL_HF'] = (rep['PAYMENT'] - rep['INTEREST']).round(2)
assert rep['NYMFID'].is_unique

# Only look at NYMFID where debt is remaining and something happend
rep = rep.query('DEBT_REMAIN != 0')
rep = rep.query('PAYMENT != 0 & INTEREST != 0')
assert all(rep['PAYMENT'] >= 0)
assert all(rep['INTEREST'] >= 0)

# Calculate totals on HF/~HF per NYMFID
udl_hf = sum_NYMF(udl).rename(columns={'AMOUNT': 'UDL_HF'})
rep = pd.merge(rep, udl_hf, on='NYMFID', how='left')
udl_ir = sum_NYMF(udl, HF=False).rename(columns={'AMOUNT': 'UDL_INTEREST'})
rep = pd.merge(rep, udl_ir, on='NYMFID', how='left')
afr_hf = sum_NYMF(afr).rename(columns={'AMOUNT': 'AFR_HF'})
rep = pd.merge(rep, afr_hf, on='NYMFID', how='left')
afr_ir = sum_NYMF(afr, HF=False).rename(columns={'AMOUNT': 'AFR_INTEREST'})
rep = pd.merge(rep, afr_ir, on='NYMFID', how='left')

rep = rep.fillna(0)
rep.set_index('NYMFID', inplace=True)

# Mark errors
rep['AFR_HF_OK'] = rep['ACL_HF'] == rep['AFR_HF']
rep['AFR_IR_OK'] = rep['INTEREST'] == rep['AFR_INTEREST']
rep['UDL_HF_OK'] = rep['ACL_HF'] == rep['UDL_HF']
rep['UDL_IR_OK'] = rep['INTEREST'] == rep['UDL_INTEREST']
ok = (rep['AFR_HF_OK'] & rep['AFR_IR_OK'] & rep['UDL_HF_OK'] & rep['UDL_IR_OK'])
rep['ALL_OK'] = ok

# Save
assert rep.index.is_unique
rep.to_pickle('rep.pkl')
