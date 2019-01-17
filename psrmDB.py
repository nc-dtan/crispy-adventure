import json
import cx_Oracle
import pandas as pd


with open('profiles.json') as f:
    profiles = json.load(f)


class PsrmDB:
    def __init__(self, env='VAL04'):
        self.ip = profiles[env]['ip']
        self.port = profiles[env]['port']
        self.sid = profiles[env]['sid']
        self.username = profiles[env]['username']
        self.password = profiles[env]['password']

    def connect(self):
        dsn_tns = cx_Oracle.makedsn(self.ip, self.port, self.sid)
        self.connection = cx_Oracle.connect(self.username, self.password, dsn_tns)

    def query(self, query):
        return pd.read_sql(query, con=self.connection)

    def get_table(self, table):
        query = f'SELECT * FROM {table}'
        return self.query(query)

    @property
    def get_bank_accounts(self):
        return self.get_table('BANK_ACCOUNTS')

    @property
    def get_ftgls(self):
        query = """SELECT *
                    FROM CISADM.CI_FT FT
                    JOIN CISADM.CI_FT_GL FTGL ON FT.FT_ID = FTGL.FT_ID"""
        return self.query(query)

    def get_payType(self, perId):
        query = f"""SELECT CI_PER_ID.PER_ID_NBR,
                        EXTRACTVALUE(xmltype('<?xml version="1.0" standalone="no" ?><schema>' || CI_PER.C1_PER_DATA_AREA || '</schema>'), '/schema/payType')
                    FROM CISADM.CI_PER_ID
                    JOIN CISADM.CI_PER ON CI_PER_ID.PER_ID = CI_PER.PER_ID
                    WHERE CI_PER_ID.PER_ID_NBR = {perId}"""
        df = self.query(query)
        df.columns = ('PER_ID_NBR', 'PAY_TYPE')
        return df


if __name__ == '__main__':
    psrmDb = PsrmDB('DEVC')
    psrmDb.connect()
    def get_random_perId():
        ci_per_id = psrmDb.get_table('CI_PER_ID')
        return ci_per_id.PER_ID_NBR.sample(1).values[0]

    print(psrmDb.get_payType(get_random_perId()))
