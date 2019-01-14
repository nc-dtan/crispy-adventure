import psrm_ci_ft_base
import os, multiprocessing, pandas, tqdm


path = '/mnt/c/Users/MAEN/Documents/PSRM_CI_FT_BASE/'

# cache afregning and underretning
if (not os.path.exists(os.path.join(path, 'afregning.pkl')) or
    not os.path.exists(os.path.join(path, 'underretning.pkl')) or
    not os.path.exists(os.path.join(path, 'NyMF_errors.pkl'))
    ):
    psrm = psrm_ci_ft_base.PSRM_CI_FT_BASE(path)
    psrm.afregning.to_pickle(os.path.join(path, 'afregning.pkl'))
    psrm.underretning.to_pickle(os.path.join(path, 'underretning.pkl'))
    psrm.NyMF_errors.to_pickle(os.path.join(path, 'NyMF_errors.pkl'))

afregning = pandas.read_pickle(os.path.join(path, 'afregning.pkl'))
underretning = pandas.read_pickle(os.path.join(path, 'underretning.pkl'))
NyMF_errors = pandas.read_pickle(os.path.join(path, 'NyMF_errors.pkl'))

# init report
nymfids = afregning['NYMFID'].unique()

def check_NYMFID(nymfid):
    underret = underretning[underretning['NYMFID'] == nymfid]
    afregn = afregning[afregning['NYMFID'] == nymfid]

    report = {'NYMFID': nymfid, 'ERRORTYPE': ''}
    afregn = afregning[afregning['NYMFID'] == nymfid]

    # time collision
    if len(afregn) > 1:
        time_collision = not afregn['TRANSAKTIONSDATO'].is_unique
    elif len(afregn) == 1:
        time_collision = False
    report['TRANS_TIME_COLLISION'] = time_collision

    # ISMATCHED == NO in group
    matched = NyMF_errors[NyMF_errors['NYMFID'] == nymfid]['ISMATCHED']
    report['ALL_ISMATCHED'] = matched.iloc[0]

    # cash ballance
    afstemt = (round(sum(afregn['CUR_AMT']), 2) ==
               round(sum(underret['AMOUNT']), 2))
    report['BALLANCED'] = afstemt
    
    # ERRORTYPES
    if any(underret['DMIFordringTypeKategori']) == 'OR':
        if (len(afregn[afregn['FT_TYPE_FLG'] == 'PS']) ==
            len(afregn[afregn['FT_TYPE_FLG'] == 'PX'])):
            if len(afregn) != len(underret):
                assert afstemt == False
                report['ERRORTYPE'] = 'OR_PS_PX'

    return report

if not os.path.exists(os.path.join(path, 'report.csv')):
    with multiprocessing.Pool(processes=7) as pool:
        report = pool.map(check_NYMFID, nymfids)
    report = pandas.DataFrame(report).set_index('NYMFID')
    report.to_csv(os.path.join(path, 'report.csv'))

report = pandas.read_csv(os.path.join(path, 'report.csv'))

assert 0
report = pandas.DataFrame(afregning['NYMFID'].drop_duplicates())
report['ERRORTYPE'] = ''
report['BALLANCED'] = False
# per NYMFID characteristics
if not os.path.exists(os.path.join(path, 'report.csv')):
    for nymfid, underret in tqdm.tqdm(underretning.groupby('NYMFID')):
        afregn = afregning[afregning['NYMFID'] == nymfid]

        # time collision
        if len(afregn) > 1:
            time_collision = not afregn['TRANSAKTIONSDATO'].is_unique
        elif len(afregn) == 1:
            time_collision = False
        report.loc[report['NYMFID'] == nymfid, 'TRANS_SAME'] = time_collision

        # ISMATCHED == NO in group
        matched = NyMF_errors[NyMF_errors['NYMFID'] == nymfid]['ISMATCHED']
        report.loc[report['NYMFID'] == nymfid, 'ISMATCHED'] = matched

        # cash ballance
        afstemt = (round(sum(afregn['CUR_AMT']), 2) ==
                   round(sum(underret['AMOUNT']), 2))
        report.loc[report['NYMFID'] == nymfid, 'BALLANCED'] = afstemt

        if any(underret['DMIFordringTypeKategori']) == 'OR':
            if (len(afregn[afregn['FT_TYPE_FLG'] == 'PS']) ==
                len(afregn[afregn['FT_TYPE_FLG'] == 'PX'])):
                if len(afregn) != len(underret):
                    assert afstemt == False
                    report.loc[report['NYMFID'] == nymfid, 'ERRORTYPE'] = 'OR_PS_PX'
    report.to_csv(os.path.join(path, 'report.csv'), index=False)

report = pandas.read_csv(os.path.join(path, 'report.csv'))


#not_ballanced = report[~report['BALLANCED']]
##for nymfid, g in tqdm.tqdm(not_ballanced.groupby('NYMFID')):
#for nymfid, underret in not_ballanced.groupby('NYMFID'):
#    afregn = afregning[afregning['NYMFID'] == nymfid]
#    if len(afregn) > 1:
#    #print(afregn['TRANSAKTIONSDATO'])
#        kollision = not afregn['TRANSAKTIONSDATO'].is_unique
#        if kollision:
#            assert False
#        

# generel fejl, nok ikke pga. af OR specifikt error at paybacks and 'OR' 
# claimant type.
#
# samtidighedsfejl: [11:10 AM] Emil Joachim Pedersen
# Og det behøver ikke være alle betalinger, men så længe der er 2 med 
# samme transaktion dato går den i ged
#
# la Cour: liste over nymfid-grupper med ISMATHED==NO
