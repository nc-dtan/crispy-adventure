import psrm
from psrm.enums.fordringshaver import FordringsHaver as FH
from tqdm import tqdm
from report_utils import *


# Load data
ps = psrm.psrm_utils.cache_psrm(path=psrm.path_v4, input=psrm.v4)
acl = annotate_acl(ps.udtraeksdata, claimant=FH.DR.value['Claimant_ID'])
udl = annotate_udl(ps.udligning)
afr = annotate_afr(ps.underretning)
dr = saldo_DR()
rm = saldo_PSRM()

# Calculate totals of 'underretninger' on HF/~HF per NYMFID
afr_hf = sum_NYMF(afr).rename(columns={'AMOUNT': 'AFR_HF'})
afr_ir = sum_NYMF(afr, HF=False).rename(columns={'AMOUNT': 'AFR_IR'})
udl_hf = sum_NYMF(udl).rename(columns={'AMOUNT': 'UDL_HF'})
udl_ir = sum_NYMF(udl, HF=False).rename(columns={'AMOUNT': 'UDL_IR'})

# Calculate debt, payments and interests per NYMFID
debt = acl_debt(acl)
pays = acl_pay(acl)
intr = acl_interest(acl)

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
assert rep['NYMFID'].is_unique
assert len(rep) == len(acl['NYMFID'].unique())

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

#rep.query('~ALL_OK & Saldo_DR.isnull()', inplace=True)
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
            raise ValueError

dr = dr.set_index('NYMFID')
rep = pd.merge(rep, dr, on='NYMFID', how='left')

assert all(rep['Difference'] != 0)
bool_sort = ['UDL_HF_OK', 'AFR_HF_OK','UDL_IR_OK','AFR_IR_OK']
rep.sort_values(bool_sort, inplace=True)
rep.to_csv('total_dr_test.csv', index=False)

# samtidighed

#rep = read_pickle('rep.pkl')
#dr = dr.join(rep['ALL_OK'], how='left')
#dr = dr.fillna(-1)
#
## Test for DR IR not included
#for nymfid, row in dr[dr['Forklaring']==False].iterrows():
#    a = afr.query('NYMFID==@nymfid')
#    u = udl.query('NYMFID==@nymfid')
#    ac = acl.query('NYMFID==@nymfid')
#    debt = ac.query('ISDEBT')['AMOUNT'].sum().round(2)
#    pay_hf = udl.query('NYMFID==@nymfid').query('ISHF')['AMOUNT'].sum().round(2)
#    hr_remain = round(debt - pay_hf, 2)
#    if row['Saldo_DR'] == hr_remain:
#        dr.loc[nymfid, 'Forklaring'] = 'mangler renter'
