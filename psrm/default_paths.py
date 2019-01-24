# The input data format
# ---------------------
# 'path' is the path where all file data is assumed to be in
# 'input' is a dictionary with information of where to find the tables:
# 'PSRM Afregning', 'Afregning_Underretning', 'Udligning', 'Udtræk'.
#
# Each value in the dictornary is a list of length 2.
# First value is a file name or a list of file names.
# Second value is a sheet name.
#
# If multiple file names are given as a value then the program will concatinate 
# the content to one table.
#
# Multiple Excel file or sheets are currently not implemented.
#

# The particular data locations
# ---------------------------
#
# We have so far recieved updated data multiple times which we organized i 
# version folders. Running this file as a script should test all the locations.  
# Typical directory structure looks like this:
#
# Data/
# ├── v1
# │   ├── PSRM_CI_FT_BASE.xlsx
# ├── v2
# │   ├── Afregninger.xlsx
# │   ├── CI_FT_BASE.xlsx
# │   ├── Udligninger.xlsx
# ├── v3
# │   ├── Afregninger.xlsx
# │   ├── CI_FT_BASE.xlsx
# │   ├── Udligninger.xlsx
# │   ├── Udtræk.xlsx
# └── v4
#     ├── 3977.txt
#     ├── 3982.txt
#     ├── Afregninger.xlsx
#     ├── CI_FT_BASE.xlsx
#     ├── Test.txt
#     ├── Udligninger.xlsx
#
# 
# Notes
# ------
#
# 'EXTERNAL_OBLIGATION_ID' is not found in v1 of udtraeksdata
# 
#
# Here are the default locations for the different locations:

# first data pull-out
path_v1 = '../Data/v1'
v1 = {
  'PSRM Afregning': ['PSRM_CI_FT_BASE.xlsx', 'PSRM Afregning'],
  'Afregning_Underretning': ['PSRM_CI_FT_BASE.xlsx', 'Afregning_Underretning'],
  'Udligning': [None, None],
  'Udtræk': ['PSRM_CI_FT_BASE.xlsx', 'Udtræk NCO'],
}

# second data pull-out
path_v2 = '../Data/v2'
v2 = {
  'PSRM Afregning': ['CI_FT_BASE.xlsx', 'Sheet1'],
  'Afregning_Underretning': ['Afregninger.xlsx', 'Sheet1'],
  'Udligning': ['Udligninger.xlsx', 'Sheet1'],
  'Udtræk': [None, None],
}

# third data pull-out
path_v3 = '../Data/v3'
v3 = {
  'PSRM Afregning': ['CI_FT_BASE.xlsx', 'Sheet1'],
  'Afregning_Underretning': ['Afregninger.xlsx', 'Sheet1'],
  'Udligning': ['Udligninger.xlsx', 'Sheet1'],
  'Udtræk': ['Udtræk.xlsx', 'Sheet1'],
}

# third excel data + the full ACL history data from Daniel
path_v4 = '../Data/v4'
v4 = {
  'PSRM Afregning': ['CI_FT_BASE.xlsx', 'Sheet1'],
  'Afregning_Underretning': ['Afregninger.xlsx', 'Sheet1'],
  'Udligning': ['Udligninger.xlsx', 'Sheet1'],
  'Udtræk': [['3977.txt', 'Test.txt', '3982.txt'], None],
}


if __name__ == '__main__':
    from psrm.psrm_ci_ft_base import PSRM_CI_FT_BASE
    psrm_v1 = PSRM_CI_FT_BASE(path=path_v1, input=v1)
    psrm_v2 = PSRM_CI_FT_BASE(path=path_v2, input=v2)
    psrm_v3 = PSRM_CI_FT_BASE(path=path_v3, input=v3)
    psrm_v4 = PSRM_CI_FT_BASE(path=path_v4, input=v4)


