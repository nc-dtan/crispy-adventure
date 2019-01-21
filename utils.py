import os
import pkg_resources
import datetime
from dateutil import parser
import pandas as pd
import git


def is_integer(a):
    try:
        _ = int(a)
    except ValueError:
        return False
    return True

def convert_date_from_str(date):
    return parser.parse(date)

def df_to_excel(df=None, path=None, sheet_name=None):
    if path is None:
        path = 'report.xlsx'
    if sheet_name is None:
        sheet_name =
     """Create a nicely formated Excel file."""
    sheet_path = report_path + '.xlsx'
    writer = pd.ExcelWriter(sheet_path, engine='xlsxwriter')
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

#def repo = git.Repo(search_parent_directories=True)
#today = datetime.datetime.today().strftime('%d-%m-%Y')
#sha = repo.head.object.hexsha
#print(today, sha[:7])

def check_requirements():
    """Check that requirements.txt is fulfilled.""
    dependencies = [line.strip() for line in open('requirements.txt', 'r')]
    pkg_resources.require(dependencies)
