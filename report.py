import psrm_ci_ft_base
import os, multiprocessing, pandas, tqdm

print('Under development!')

path = '/mnt/c/Users/MAEN/Documents/PSRM_CI_FT_BASE/'  # local path

# cache afregning and underretning
if (not os.path.exists(os.path.join(path, 'afregning.pkl')) or
    not os.path.exists(os.path.join(path, 'underretning.pkl')) or
    not os.path.exists(os.path.join(path, 'NyMF_errors.pkl'))
    ):
    print('creating cache')
    psrm = psrm_ci_ft_base.PSRM_CI_FT_BASE(path)
    psrm.afregning.to_pickle(os.path.join(path, 'afregning.pkl'))
    psrm.underretning.to_pickle(os.path.join(path, 'underretning.pkl'))
    psrm.NyMF_errors.to_pickle(os.path.join(path, 'NyMF_errors.pkl'))

afregning = pandas.read_pickle(os.path.join(path, 'afregning.pkl'))
underretning = pandas.read_pickle(os.path.join(path, 'underretning.pkl'))
NyMF_errors = pandas.read_pickle(os.path.join(path, 'NyMF_errors.pkl'))

nymfids_1 = set(afregning['NYMFID'].unique())
nymfids_2 = set(underretning['NYMFID'].unique())
nymfids = list(nymfids_1.union(nymfids_2))


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
    matched = NyMF_errors[NyMF_errors['NYMFID'] == nymfid]['ISMATCHED']
    report['ALL_ISMATCHED'] = matched.iloc[0]

    # cash ballance
    afstemt = (round(sum(afregn['AMOUNT']), 2) ==
               round(sum(underret['AMOUNT']), 2))
    report['BALLANCED'] = afstemt

    # ERRORS, only one error should be returned
    if len(afregn) and not len(underret):
        report['ERROR'] = 'MISSING_UNDERRET'
        return report

    if len(underret) and not len(afregn):
        report['ERROR'] = 'MISSING_AFREGN'
        return report
        
    ps = len(afregn[afregn['FT_TYPE_FLG'] == 'PS'])
    px = len(afregn[afregn['FT_TYPE_FLG'] == 'PX'])

    if ps == px:
        if any(underret['DMIFordringTypeKategori'] == 'OR'):
            if len(afregn) != len(underret):
                assert afstemt == False
                report['ERROR'] = 'OR_PS_PX'
<<<<<<< HEAD
                return report

    if ps != px and ps + px > 2:
        if all(underret['DMIFordringTypeKategori'] == 'HF'):
            if not afstemt == False:
                print('nyfejl forkert', nymfid)
    
def get_report(fname='report.csv', ncpus=1, force=False):
    # uses global nymfids and path
    if not os.path.exists(os.path.join(path, fname)) or force:
        print('creating report')
        if ncpus > 1:
            with multiprocessing.Pool(processes=ncpus) as pool:
                report = pool.map(check_NYMFID, nymfids)
        else:
            report = [check_NYMFID(x) for x in tqdm.tqdm(nymfids)]
        #report = pandas.DataFrame(report).set_index('NYMFID')
        report = pandas.DataFrame(report)
        report.to_csv(os.path.join(path, fname))
    report = pandas.read_csv(os.path.join(path, fname))
    return report

# not done
def df_to_excel(df):
    sheet_path = os.path.join(path, 'report.xlsx')
    writer = pandas.ExcelWriter(sheet_path, engine='xlsxwriter')
    report.to_excel(writer, sheet_name='report', index=False)
    workbook  = writer.book
    worksheet = writer.sheets['report']
    worksheet.autofilter(0, 0, report.shape[0], report.shape[1])
    writer.save()

#report = get_report(ncpus=8)

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
