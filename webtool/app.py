from flask import Flask,render_template, request
import pandas as pd
import numpy as np
import psrm
app = Flask(__name__)

@app.route("/")
def index():
    import psrm

    ps = psrm.psrm_utils.cache_psrm(path=psrm.path_v4, input=psrm.v4)
    return render_template("index.html", ps=ps)


@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    return processed_text

if __name__ == "__main__":
    app.run(debug=True)
