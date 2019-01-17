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


if __name__ == '__main__':
    query = "SELECT * FROM BANK_ACCOUNTS"
    for env in profiles.keys():
        print(f'Trying to connect to {env}...')
        psrmDb = PsrmDB(env=env)
        try:
            psrmDb.connect()
            print(psrmDb.query(query))
        except cx_Oracle.DatabaseError:
            print(f'Could not connect to {env}.')
