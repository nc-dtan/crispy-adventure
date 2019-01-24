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

    @property
    def connect(self):
        dsn_tns = cx_Oracle.makedsn(self.ip, self.port, self.sid)
        self.connection = cx_Oracle.connect(self.username, self.password, dsn_tns)

    def _query(self, query):
        return pd.read_sql(query, con=self.connection)

    def get_table(self, table):
        query = f'SELECT * FROM {table}'
        return self._query(query)

    @property
    def get_bank_accounts(self):
        return self.get_table('BANK_ACCOUNTS')

    @property
    def get_ftgls(self):
        query = """SELECT *
                    FROM CISADM.CI_FT FT
                    JOIN CISADM.CI_FT_GL FTGL ON FT.FT_ID = FTGL.FT_ID"""
        return self._query(query)

    def get_payType(self, perId):
        query = f"""SELECT CI_PER_ID.PER_ID_NBR,
                        EXTRACTVALUE(xmltype('<?xml version="1.0" standalone="no" ?><schema>' || CI_PER.C1_PER_DATA_AREA || '</schema>'), '/schema/payType')
                    FROM CISADM.CI_PER_ID
                    JOIN CISADM.CI_PER ON CI_PER_ID.PER_ID = CI_PER.PER_ID
                    WHERE CI_PER_ID.PER_ID_NBR = {perId}"""
        df = self._query(query)
        df.columns = ('PER_ID_NBR', 'PAY_TYPE')
        return df

    def _get_ACL(self, accounts, dkcshact):
        accounts = f"({', '.join(map(str, accounts))})"
        if dkcshact:
            dkcshact = "PARENT_ID='DKCSHACT'"
        else:
            dkcshact = "PARENT_ID<>'DKCSHACT'"

        query = f"""SELECT TRANSACTION_DATE,
                        EFFECTIVE_DATE,
                        ACCOUNTING_DATE,
                        CLAIMANT_ID,
                        GL_ACCT,
                        EXTERNAL_OBLIGATION_ID,
                        SA_ID,
                        ADJ_ID,
                        PAY_EVENT_ID,
                        PAY_ID,
                        PARENT_ID,
                        SIBLING_ID,
                        FT_TYPE_FLG,
                        FT_ID,
                        AMOUNT
                    FROM CISADM.DK_ACL_DATA
                        WHERE (GL_ACCT IN {accounts} AND {dkcshact})"""
        df = self._query(query)
        df['GL_ACCT'] = df['GL_ACCT'].astype('int')
        df['CLAIMANT_ID'] = df['CLAIMANT_ID'].astype('int')
        df['SA_ID'] = df['SA_ID'].astype('int')
        df['SIBLING_ID'] = df['SIBLING_ID'].astype('int')
        df['FT_ID'] = df['FT_ID'].astype('int')
        df['AMOUNT'] = df['AMOUNT'].astype('float')
        return df

    @property
    def get_ACL1(self):
        '''Extract data from the ACL.
        Parameters:
          GL_ACCT = 3974
          PARENT_ID = DKCSHACT
        '''
        return self._get_ACL(('3974'), True)

    @property
    def get_ACL2(self):
        '''Extract data from the ACL.
        Parameters:
          GL_ACCT IN (9110, 3970)
          PARENT_ID <> DKCSHACT
        '''
        return self._get_ACL(('9110', '3970'), False)

    @property
    def get_ACL3(self):
        '''Extract data from the ACL.
        Parameters:
          GL_ACCT = 3977
          PARENT_ID <> DKCSHACT
        '''
        return self._get_ACL(('3977'), False)

    @property
    def get_ACL4(self):
        '''Extract data from the ACL.
        Parameters:
          GL_ACCT = 3982
          PARENT_ID <> DKCSHACT
        '''
        return self._get_ACL(('3982'), False)


if __name__ == '__main__':
    psrmDb = PsrmDB('VAL04')
    psrmDb.connect

    def get_random_perId():
        ci_per_id = psrmDb.get_table('CI_PER_ID')
        return ci_per_id.PER_ID_NBR.sample(1).values[0]

    print(psrmDb.get_payType(get_random_perId()))
