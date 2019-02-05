import pandas as pd
import psrm
from psrm.enums.fordringshaver import FordringsHaver as FH
from psrm import report_utils as ru

# Load data
ps = psrm.psrm_utils.cache_psrm(path=psrm.path_v4, input=psrm.v4)
acl = ru.annotate_acl(ps.udtraeksdata, claimant=FH.DR.value['Claimant_ID'])
udl = ru.annotate_udl(ps.udligning)
afr = ru.annotate_afr(ps.underretning)
dr = ru.saldo_DR()
rm = ru.saldo_PSRM()

# Calculate totals of 'underretninger' on HF/~HF per NYMFID
afr_hf = ru.sum_NYMF(afr).rename(columns={'AMOUNT': 'AFR_HF'})
afr_ir = ru.sum_NYMF(afr, HF=False).rename(columns={'AMOUNT': 'AFR_IR'})
udl_hf = ru.sum_NYMF(udl).rename(columns={'AMOUNT': 'UDL_HF'})
udl_ir = ru.sum_NYMF(udl, HF=False).rename(columns={'AMOUNT': 'UDL_IR'})

# Calculate debt, payments and interests per NYMFID
debt = ru.acl_debt(acl)
pays = ru.acl_pay(acl)
intr = ru.acl_interest(acl)

# Create report, merge debt
rep = pd.DataFrame(acl['NYMFID'].unique(), columns=['NYMFID'])
rep = pd.merge(rep, debt, on='NYMFID', how='left')
rep = pd.merge(rep, pays, on='NYMFID', how='left')
rep = pd.merge(rep, intr, on='NYMFID', how='left')

# Merge totals to report
rep = pd.merge(rep, afr_hf, on='NYMFID', how='left')
rep = pd.merge(rep, afr_ir, on='NYMFID', how='left')
rep = pd.merge(rep, udl_hf, on='NYMFID', how='left')
rep = pd.merge(rep, udl_ir, on='NYMFID', how='left')
rep = rep.fillna(0)

# Calculate remaining debt per NYMFID
rep['DEBT_REMAIN'] = (rep['DEBT']-rep['PAYMENT']+rep['ACL_IR']).round(2)
rep['ACL_HF'] = (rep['PAYMENT'] - rep['ACL_IR']).round(2)
rep = pd.merge(rep, rm, on='NYMFID', how='left')
if not rep['NYMFID'].is_unique:
    raise psrm.errors.NyMFError('NYMFIDs are not unique.')
if not len(rep) == len(acl['NYMFID'].unique()):
    raise psrm.errors.NyMFError('Report df does not have the right length.')

# Mark ballance errors
rep['UDL_HF_OK'] = rep['ACL_HF'] == rep['UDL_HF']
rep['AFR_HF_OK'] = rep['ACL_HF'] == rep['AFR_HF']
rep['UDL_IR_OK'] = rep['ACL_IR'] == rep['UDL_IR']
rep['AFR_IR_OK'] = rep['ACL_IR'] == rep['AFR_IR']
ok = (rep['AFR_HF_OK'] & rep['AFR_IR_OK'] & rep['UDL_HF_OK'] & rep['UDL_IR_OK'])
rep['ALL_OK'] = ok

# Mark DB round error for 1 øre
dr['Fejlkategori'] = False
dr.loc[dr['Difference'] == -0.01, 'Fejlkategori'] = 'DB fejl'
rep.query('~ALL_OK', inplace=True)

# Test for missing underretning
for i, row in dr.iterrows():
    if row['Fejlkategori'] != False:
        continue
    nymfid = row['NYMFID']
    a = afr.query('NYMFID==@nymfid')
    u = udl.query('NYMFID==@nymfid')
    if len(a) == 0 and len(u) == 0:
        dr.loc[dr['NYMFID']==nymfid, 'Fejlkategori'] = 'ingen aktivitet'
        ac = acl.query('NYMFID==@nymfid')
        if len(ac.query('ISPAY')) != 0:
            raise psrm.errors.NyMFError('Payments should not possible here.')

dr = dr.set_index('NYMFID')
rep = pd.merge(rep, dr, on='NYMFID', how='left')

bool_sort = ['UDL_HF_OK', 'AFR_HF_OK','UDL_IR_OK','AFR_IR_OK']
rep.sort_values(bool_sort, inplace=True)
rep.to_csv('total_dr_test.csv', index=False)
