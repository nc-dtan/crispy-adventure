import psrm_ci_ft_base
import os, multiprocessing, pandas, tqdm

print('Under development!')

path = '/mnt/c/Users/MAEN/Documents/PSRM_CI_FT_BASE/'  # local path

# cache afregning and underretning
if (not os.path.exists(os.path.join(path, 'afregning.pkl')) or
    not os.path.exists(os.path.join(path, 'underretning.pkl'))):
    print('creating cache')
    psrm = psrm_ci_ft_base.PSRM_CI_FT_BASE(path)
    psrm.afregning.to_pickle(os.path.join(path, 'afregning.pkl'))
    psrm.underretning.to_pickle(os.path.join(path, 'underretning.pkl'))

afregning = pandas.read_pickle(os.path.join(path, 'afregning.pkl'))
underretning = pandas.read_pickle(os.path.join(path, 'underretning.pkl'))

# only checking afregning NYMFIDs
nymfids = afregning['NYMFID'].unique()
def check_NYMFID(nymfid):
    underret = underretning[underretning['NYMFID'] == nymfid]
    afregn = afregning[afregning['NYMFID'] == nymfid]
    report = {'NYMFID': nymfid, 'ERROR': ''}

    # time collision
    if len(afregn) > 1:
        time_collision = not afregn['TRANSAKTIONSDATO'].is_unique
    else:
        time_collision = False
    report['TIME_COLLISION'] = time_collision

    # ISMATCHED == NO in group
    ismatched = NyMF_errors[NyMF_errors['NYMFID'] == nymfid]['ISMATCHED']
    assert ismatched.iloc[0] != any(afregn['ISMATCHED'] == 'NO')
    report['ISMATCHED'] = ismatched.iloc[0]

    # PSRM_MATCHED == NO in group
    pmatched = not any(underret['PSRM_MATCHED'] == 'NO')
    report['PSRM_MATCHED'] = pmatched

    # cash ballance
    afstemt = (round(sum(afregn['AMOUNT']), 2) ==
               round(sum(underret['AMOUNT']), 2))
    report['BALLANCED'] = afstemt

    # ERRORS, only one error should be returned
    if len(afregn) and not len(underret):
        report['ERROR'] = 'MISSING_UNDERRET'
        return report
        
    ps = len(afregn[afregn['FT_TYPE_FLG'] == 'PS'])
    px = len(afregn[afregn['FT_TYPE_FLG'] == 'PX'])

    if ps == px:
        if any(underret['DMIFordringTypeKategori'] == 'OR'):
            if len(afregn) != len(underret):
                assert afstemt == False
                report['ERROR'] = 'OR_PS_PX'
                return report

    if ps != px and ps + px > 2:
        if all(underret['DMIFordringTypeKategori'] == 'HF'):
            if not afstemt == False:
                pass

    if ps < px:  # cannot be more send backs than payments!
        raise NotImplementedError

    # return report normally
    return report
    
def get_report(fname='report.csv', nymfids=None, ncpus=1, force=False):
    # uses global nymfids and path
    if not os.path.exists(os.path.join(path, fname)) or force:
        print('creating report')
        if ncpus > 1:
            with multiprocessing.Pool(processes=ncpus) as pool:
                report = pool.map(check_NYMFID, nymfids)
        else:
            report = [check_NYMFID(x) for x in tqdm.tqdm(nymfids)]
        report = pandas.DataFrame(report).set_index('NYMFID')
        report.to_csv(os.path.join(path, fname))
    report = pandas.read_csv(os.path.join(path, fname))
    return report

# not done
def df_to_excel(df, fname='report.xlsx'):
    sheet_path = os.path.join(path, fname)
    print('saving xlsx', sheet_path)
    writer = pandas.ExcelWriter(sheet_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=fname.split('.')[0], index=False)
    worksheet = writer.sheets[fname.split('.')[0]]
    worksheet.autofilter(0, 0, df.shape[0], df.shape[1]-1)
    writer.save()

report = get_report(ncpus=8, nymfids=nymfids)
df_to_excel(report)

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
