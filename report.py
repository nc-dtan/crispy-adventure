import os, multiprocessing, datetime
from timeit import default_timer as timer
import pandas, git
from tqdm import tqdm
import psrm_ci_ft_base


print('Under development!')
path = '../Data/v2/'  # local path
repo = git.Repo(search_parent_directories=True)
today = datetime.datetime.today().strftime('%d-%m-%Y')
sha = repo.head.object.hexsha
print(today, sha[:7])

# cache afregning and underretning
if (not os.path.exists(os.path.join(path, 'afregning.pkl')) or
    not os.path.exists(os.path.join(path, 'underretning.pkl'))):
    print('creating cache')
    psrm = psrm_ci_ft_base.PSRM_CI_FT_BASE(path, multi_sheets=True)
    psrm.afregning.to_pickle(os.path.join(path, 'afregning.pkl'))
    psrm.underretning.to_pickle(os.path.join(path, 'underretning.pkl'))

afregning = pandas.read_pickle(os.path.join(path, 'afregning.pkl'))
underretning = pandas.read_pickle(os.path.join(path, 'underretning.pkl'))

# only checking afregning NYMFIDs
nymfids = afregning['NYMFID'].unique()
def check_NYMFID(nymfid, ISMATCHED=False):
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

    if ISMATCHED:
        # ISMATCHED == NO in group
        report['ISMATCHED'] = not any(afregn['ISMATCHED'] == 'NO')
    
        # PSRM_MATCHED == NO in group
        report['PSRM_MATCHED'] = not any(underret['PSRM_MATCHED'] == 'NO')

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


def df_to_excel(df, report_path=None):
    sheet_path = report_path + '.xlsx'
    writer = pandas.ExcelWriter(sheet_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='report')
    worksheet = writer.sheets['report']
    columns = [{'header': x} for x in df.columns.tolist()]
    worksheet.add_table(0, 1, df.shape[0], df.shape[1],
                        {'header_row': True,
                         'autofilter': True,
                         'data': df.values.tolist(),
                         'columns': columns,
                        },
    )
    worksheet.set_column(0, df.shape[1], 18)
    writer.save()
    
def get_report(report_path, ids=None, ncpus=1):
    if not os.path.exists(report_path):
        if ncpus > 1:
            with multiprocessing.Pool(processes=ncpus) as p:
                report = list(tqdm(p.imap(check_NYMFID, ids), total=len(ids)))
        else:
            report = [check_NYMFID(x) for x in tqdm.tqdm(ids)]
        report = pandas.DataFrame(report)
        report.to_pickle(report_path)
        df_to_excel(report, report_path=report_path)
        return report
    report = pandas.read_pickle(report_path)
    return report

start = timer()
report_name = f'report_{today}_{sha[:7]}.pkl'
report_path = os.path.join(path, report_name)
report = get_report(report_path, ids=nymfids, ncpus=8)
print('total run time', round(timer() - start, 2))
