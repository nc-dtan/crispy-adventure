import pandas
rep = pandas.read_pickle('rep.pkl')
#rep = rep.query('PAYMENT != 0 & INTEREST != 0 & REMAIN != 0')
#assert all(rep['UDL'].isnull() == rep['AFR'].isnull())
