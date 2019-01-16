import os, multiprocessing, datetime
import pandas, tqdm, git
import psrm_ci_ft_base


print('Under development!')
path = '../Data'  # local path
repo = git.Repo(search_parent_directories=True)
today = datetime.datetime.today().strftime('%d-%m-%Y')
sha = repo.head.object.hexsha
print(today, sha[:7])

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
    report = {'NYMFID': nymfid, 'ERROR': 'NO'}

    # trans time collision
    if len(afregn) > 1:
        time_collision = not afregn['TRANSAKTIONSDATO'].is_unique
    else:
        time_collision = False
    report['TRANS_COLLISION'] = time_collision

    # virk time collision
    if len(afregn) > 1:
        virk_time_collision = not afregn['VIRKNINGSDATO'].is_unique
    else:
        virk_time_collision = False
    report['VIRK_COLLISION'] = virk_time_collision

    # ISMATCHED == NO in group
    report['ISMATCHED'] = not any(afregn['ISMATCHED'] == 'NO')

    # PSRM_MATCHED == NO in group
    pmatched = not any(underret['PSRM_MATCHED'] == 'NO')
    report['PSRM_MATCHED'] = pmatched

    # cash ballance
    afstemt = (round(sum(afregn['AMOUNT']), 2) ==
               round(sum(underret['AMOUNT']), 2))
    report['BALLANCED'] = afstemt

    # miss match payid
    for i in range(len(afregn)):
        seg = afregn['PAY_SEG_ID'].iloc[i]
        event = afregn['PAY_EVENT_ID'].iloc[i]
        t1 = any(underret['EFIBETALINGSIDENTIFIKATOR'] == seg)
        t2 = any(underret['EFIBETALINGSIDENTIFIKATOR'] == event)
        if t1 or t2:
            report['MISSING_PAY_ID'] = False
        else:
            report['MISSING_PAY_ID'] = True

    # ERRORS, sequential (early return)
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

    # TODO: ERRORS
    # early first WDEX leads to false payment, but not always!!

    # DOORSTOPS
    if ps < px:  # cannot be more send backs than payments
        raise NotImplementedError
    
    # no error found
    return report


def df_to_excel(df, fname=None):
    sheet_path = os.path.join(path, fname)
    print('saving xlsx', sheet_path)
    writer = pandas.ExcelWriter(sheet_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=fname.split('.')[0], index=False)
    worksheet = writer.sheets[fname.split('.')[0]]


    #worksheet.autofilter(0, 0, df.shape[0], df.shape[1]-1)
    #worksheet.set_column(0, df.shape[1]-1, 20)
    writer.book.nan_inf_to_errors = True
    worksheet.add_table(0, 0, df.shape[0], df.shape[1]-1,
                        {'header_row': False,
                         'autofilter': True,
                         'data': df.values.tolist(),
                        },
    )
    writer.save()
    
def get_report(fname=None, ids=None, path=None, ncpus=1, force=False):
    if not os.path.exists(os.path.join(path, fname)) or force:
        print('creating report')
        if ncpus > 1:
            with multiprocessing.Pool(processes=ncpus) as pool:
                report = pool.map(check_NYMFID, ids)
        else:
            report = [check_NYMFID(x) for x in tqdm.tqdm(ids)]
        report = pandas.DataFrame(report).set_index('NYMFID')
        report.to_csv(os.path.join(path, fname))
        df_to_excel(report, fname=fname)
    report = pandas.read_csv(os.path.join(path, fname))
    return report

report_name = f'report_{today}_{sha[:7]}.xlsx'
report = get_report(fname=report_name, ids=nymfids, path=path, ncpus=8)
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
