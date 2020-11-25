import altair as alt
import pandas as pd
from flask import Flask, render_template, request, redirect
import datetime
import build_model
import get_latest_covid
import model_analysis

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
    average = sum(coefs)/4
    table_values, f_p_value, output_string = model_analysis.do_some_analysis(model,app.vars['state'],app.vars['business'])
    altair_json, latest_date = get_latest_covid.make_covid_plot(app.vars['state'])
    return render_template('make_chart.html',state_html =app.vars['state'], \
    business_html = app.vars['business'], average=average, \
    chart_json = altair_json, date_string = latest_date, \
    t1 = round(table_values[0][0],3), t2 = round(table_values[1][0],3),\
    t3 = round(table_values[2][0],3), t4 = round(table_values[3][0],3), \
    t5 = round(table_values[0][1],3), t6 = round(table_values[1][1],3), \
    t7 = round(table_values[2][1],3), t8 = round(table_values[3][1],3), \
    t9 = round(table_values[0][2],3), t10 = round(table_values[1][2],3), \
    t11 = round(table_values[2][2],3), t12 = round(table_values[3][2],3), \
    t13 = round(table_values[0][3],3), t14 = round(table_values[1][3],3), \
    t15 = round(table_values[2][3],3), t16 = round(table_values[3][3],3))

if __name__=='__main__':
    app.run()
