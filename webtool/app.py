from flask import Flask,render_template, request
import pandas as pd
import numpy as np
import psrm
app = Flask(__name__)
   

def _html(df):
    return df.to_html(classes=['w3-table', 'w3-striped'], index=False)


@app.route("/")
def index():
    return render_template("index.html", df=None)


@app.route('/', methods=['POST'])
def my_form_post():
    nymfid = request.form['nymfid']
    if nymfid == '':
        nymfid = 100052710938
    else:
        nymfid = int(nymfid)
    return render_template("index.html",
                           afregn=_html(afregn.query('NYMFID==@nymfid')),
                           underret=_html(underret.query('NYMFID==@nymfid')),
                           udlign=_html(udlign.query('NYMFID==@nymfid')),
                           udtraek=_html(udtraek.query('NYMFID==@nymfid')))


if __name__ == "__main__":
    ps = psrm.psrm_utils.cache_psrm(path=psrm.path_v4, input=psrm.v4)
    cols = ['NYMFID', 'VIRKNINGSDATO', 'EFIBETALINGSIDENTIFIKATOR', 'AMOUNT',
            'Daekningstype', 'DMIFordringTypeKategori']
    afregn = ps.afregning[['NYMFID', 'VIRKNINGSDATO', 'AMOUNT', 'FT_TYPE_FLG']]
    underret = ps.underretning[cols]
    udlign = ps.udligning[cols]
    udtraek = ps.udtraeksdata
    app.run(debug=False)
