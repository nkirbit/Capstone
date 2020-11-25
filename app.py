import altair as alt
import pandas as pd
from flask import Flask, render_template, request, redirect
import datetime
import build_model
import get_latest_covid

app = Flask(__name__)
app.vars={}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        app.vars['state'] = request.form['state']
        app.vars['business'] = request.form['business']
        return redirect('/make_chart')

@app.route('/make_chart', methods=['GET', 'POST'])
def make_chart():
    model = build_model.generate_model(app.vars['business'])
    coefs = model.params[1:5]
    app.vars['average'] = sum(coefs)/4
    altair_json = get_latest_covid.make_covid_plot(app.vars['state'])
    return render_template('make_chart.html',state_html =app.vars['state'], \
    business_html = app.vars['business'], average=app.vars['average'], \
    chart_json = altair_json)

if __name__=='__main__':
    app.run()
