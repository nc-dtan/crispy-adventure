import tqdm
acl = ps.udtraeksdata
acl = acl.sort_values('TRANSACTION_DATE')
b100 = rep.query('DEBT == 100')
df = rep.query('DEBT != 100')
acl = acl[acl['NYMFID'].isin(b100.NYMFID)]
#for i in tqdm.tqdm(b100.NYMFID):
#    a=ps.underretning.query('NYMFID==@i')
#    b=acl.query('NYMFID==@i')
#    b = b.sort_values('TRANSACTION_DATE')
#    #b=afr.query('NYMFID==@i')
#    ftk = set(a['DMIFordringTypeKategori'])
#    assert b['PARENT_ID'].iloc[0] == 'DKOGEX'
#    assert len(ftk - {'IR', 'OG'}) == 0


