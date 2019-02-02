from flask import Flask,render_template, request
import pandas as pd
import numpy as np
import psrm
app = Flask(__name__)
   

def _html(df):
    return df.to_html(classes=['w3-table-all'], index=False)


@app.route("/")
def index():
    return render_template("index.html", df=None)


@app.route('/', methods=['POST'])
def my_form_post():
    nymfid = request.form['nymfid']
    nymfid = 100052710938
    afregn, underret, udlign, udtraek = ps.get_by_id(nymfid)
    cols = ['VIRKNINGSDATO', 'EFIBETALINGSIDENTIFIKATOR', 'AMOUNT',
            'Daekningstype', 'DMIFordringTypeKategori']
    afregn = afregn.df[['VIRKNINGSDATO', 'AMOUNT', 'FT_TYPE_FLG']]
    underret = underret.df[cols]
    udlign = udlign.df[cols]
    udtraek = udtraek.df
    del udtraek['NYMFID']
    return render_template("index.html",
                           afregn=_html(afregn),
                           underret=_html(underret),
                           udlign=_html(udlign),
                           udtraek=_html(udtraek),)


if __name__ == "__main__":
    ps = psrm.psrm_utils.cache_psrm(path=psrm.path_v4, input=psrm.v4)
    app.run(debug=True)
