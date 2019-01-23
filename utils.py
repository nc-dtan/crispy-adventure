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
    """Create a nicely formated Excel file."""
    if path is None:
        path = 'report.xlsx'
    if sheet_name is None:
        sheet_name = os.path.splitext(os.path.basename(path))[0]
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
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


def check_requirements():
    """Check that requirements.txt is fulfilled."""
    dependencies = [line.strip() for line in open('requirements.txt', 'r')]
    pkg_resources.require(dependencies)


def get_short_hash():
    """Get the 7 first characters of the current git hash."""
    repo = git.Repo(search_parent_directories=True)
    return repo.head.object.hexsha


def get_date():
    """Get string version of todays date."""
    return datetime.datetime.today().strftime('%d-%m-%Y')


def to_amount(series):
    return list(map(lambda x: round(x, 2), series))
