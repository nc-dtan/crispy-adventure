import pandas as pd
import psrm
from psrm.utils import utils
from psrm.utils import psrm_utils

if __name__ == '__main__':
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

    # Load and define relevant columns
    ps = psrm.psrm_utils.cache_psrm(path=psrm.path_v4, input=psrm.v4)
    acols = ['NYMFID', 'EFFECTIVE_DATE', 'PARENT_ID', 'AMOUNT', 'CLAIMANT_ID']

    # Timecut and annotate ACL-udtraek
    end_date = pd.to_datetime('2018-12-28')  # cutdate
    acl = ps.udtraeksdata[acols]
    acl['EFFECTIVE_DATE'] = pd.to_datetime(acl['EFFECTIVE_DATE'])
    acl = acl.query('EFFECTIVE_DATE < @end_date')
    acl = acl.query('CLAIMANT_ID == 1229')  # only DR

    acl['ISDEBT'] = ((acl['PARENT_ID'] == 'DKHFEX') |
                     (acl['PARENT_ID'] == 'DKOGEX') |
                     (acl['PARENT_ID'] == 'DKOREX') |
                     (acl['PARENT_ID'] == 'DKIGEX') )
    acl['ISPAY'] = [utils.is_integer(x) for x in acl['PARENT_ID'].values]
    acl['ISCATU'] = acl['PARENT_ID'] == 'DKCSHACT'
    assert ~acl.isnull().sum().sum()  # check no nulls in acl

    # Calculate the initial debt per NYMFID
    debt = acl.query('ISDEBT').groupby('NYMFID')
    debt = debt['AMOUNT'].sum().round(2).reset_index()
    debt.rename(columns={'AMOUNT': 'DEBT'}, inplace=True)
    debt.set_index('NYMFID', inplace=True)

    # Calculate sum of all payments per NYMFID
    pays = acl.query('ISPAY').groupby('NYMFID')
    pays = pays['AMOUNT'].sum().round(2).reset_index()
    pays.rename(columns={'AMOUNT': 'PAYMENT'}, inplace=True)
    pays['PAYMENT'] = -pays['PAYMENT']
    pays.set_index('NYMFID', inplace=True)

    # Calculate sum of all interests on NYMFID
    intr = acl.query('ISCATU').groupby('NYMFID')
    intr = intr['AMOUNT'].sum().round(2).reset_index()
    intr.rename(columns={'AMOUNT': 'INTEREST'}, inplace=True)
    intr['INTEREST'] = -intr['INTEREST']
    intr.set_index('NYMFID', inplace=True)

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
    ids = rep['NYMFID'].unique()

    # Relevant columns for underretninger
    ucols = ['NYMFID', 'Daekningstype', 'AMOUNT', 'DMIFordringTypeKategori',
             'EFIAFREGNINGSDATO', 'VIRKNINGSDATO']

    # Prepare udligning underretning
    udl = ps.udligning[ucols]
    udl['VIRKNINGSDATO'] = pd.to_datetime(udl['VIRKNINGSDATO'])
    end_date = pd.to_datetime('2018-12-28')  # cutdate
    udl = udl.query('VIRKNINGSDATO < @end_date')
    udl = udl[udl['NYMFID'].isin(ids)]
    udl = udl.query('~Daekningstype.isnull()')
    udl['ISHF'] = udl['DMIFordringTypeKategori'].isin(['IG', 'OG', 'HF'])

    # Calculate the total udligning underretning on HF per NYMFID
    udl_hf = udl.query('ISHF').groupby('NYMFID')
    udl_hf = udl_hf['AMOUNT'].sum().round(2).reset_index()
    udl_hf.rename(columns={'AMOUNT': 'UDL_HF'}, inplace=True)
    udl_hf.set_index('NYMFID', inplace=True)
    rep = pd.merge(rep, udl_hf, on='NYMFID', how='left')

    # Calculate the total udligning underretning on INTEREST per NYMFID
    udl_ir = udl.query('~ISHF').groupby('NYMFID')
    udl_ir = udl_ir['AMOUNT'].sum().round(2).reset_index()
    udl_ir.rename(columns={'AMOUNT': 'UDL_INTEREST'}, inplace=True)
    udl_ir.set_index('NYMFID', inplace=True)
    rep = pd.merge(rep, udl_ir, on='NYMFID', how='left')

    # Prepare afregning underretning
    afr = ps.underretning[ucols]
    afr['EFIAFREGNINGSDATO'] = pd.to_datetime(afr['EFIAFREGNINGSDATO'])
    afr = afr[afr['NYMFID'].isin(ids)]
    afr = afr.query('~Daekningstype.isnull()')
    afr['ISHF'] = afr['DMIFordringTypeKategori'].isin(['IG', 'OG', 'HF'])

    # Calculate the total afregning underretning on HF per NYMFID
    afr_hf = afr.query('ISHF').groupby('NYMFID')
    afr_hf = afr_hf['AMOUNT'].sum().round(2).reset_index()
    afr_hf.rename(columns={'AMOUNT': 'AFR_HF'}, inplace=True)
    afr_hf.set_index('NYMFID', inplace=True)
    rep = pd.merge(rep, afr_hf, on='NYMFID', how='left')

    # Calculate the total afregning underretning on INTEREST per NYMFID
    afr_ir = afr.query('~ISHF').groupby('NYMFID')
    afr_ir = afr_ir['AMOUNT'].sum().round(2).reset_index()
    afr_ir.rename(columns={'AMOUNT': 'AFR_INTEREST'}, inplace=True)
    afr_ir.set_index('NYMFID', inplace=True)
    rep = pd.merge(rep, afr_ir, on='NYMFID', how='left')
    rep = rep.fillna(0)
    rep.set_index('NYMFID', inplace=True)

    # Mark errors
    rep['AFR_HF_OK'] = rep['ACL_HF'] == rep['AFR_HF']
    rep['AFR_IR_OK'] = rep['INTEREST'] == rep['AFR_INTEREST']
    rep['UDL_HF_OK'] = rep['ACL_HF'] == rep['UDL_HF']
    rep['UDL_IR_OK'] = rep['INTEREST'] == rep['UDL_INTEREST']
    rep['ALL_OK'] = (rep['AFR_HF_OK'] & rep['AFR_IR_OK'] & rep['UDL_HF_OK'] & 
            rep['UDL_IR_OK'])

    # Save
    assert rep.index.is_unique
    rep.to_pickle('rep.pkl')
