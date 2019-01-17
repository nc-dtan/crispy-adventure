# NON DR

non_DR = report[report['FHID'] != 1229]
good_ids = non_DR[non_DR['UDL_BALLANCED']]['NYMFID'].values
bad_ids = non_DR[~non_DR['UDL_BALLANCED']]['NYMFID'].values
bad = afregning[afregning['NYMFID'].isin(bad_ids)]
good = afregning[afregning['NYMFID'].isin(good_ids)]

print('latest good', good['TRANSAKTIONSDATO'].max())
print('first bad', bad['TRANSAKTIONSDATO'].min())
