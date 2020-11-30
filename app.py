import altair as alt
import pandas as pd
from flask import Flask, render_template, request, redirect
import datetime
import build_model
import get_latest_covid
import model_analysis
import prediction_plots
import generate_result_string

app = Flask(__name__)
app.vars={}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index_test.html')
    else:
        app.vars['state'] = request.form['state']
        app.vars['business'] = request.form['business']
        return redirect('/analysis')

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'GET':
        model = build_model.generate_model(app.vars['business'])
        coefs = model.params[1:5]
        business_no_underscore = app.vars['business'].replace('_',' ')
        table_values, f_p_value, output_string = model_analysis.do_some_analysis(model,app.vars['state'],app.vars['business'])
        altair_json, latest_date, state_df, state_pop = get_latest_covid.make_covid_plot(app.vars['state'])
        chart_json_2, most_recent_cases, recent_interest, recent_cases = prediction_plots.predictions(app.vars['business'],app.vars['state'],state_df,coefs,state_pop)
        long_string, short_string = generate_result_string.generate_result_string(model,app.vars['state'],business_no_underscore,state_pop,state_df)
        default = round(most_recent_cases)
        app.vars['coefs'] = coefs
        app.vars['interests'] = recent_interest
        app.vars['cases'] = recent_cases
        return render_template('analysis_test.html',state =app.vars['state'], \
        business = app.vars['business'],  p_value = f_p_value, \
        chart_json = altair_json, date_string = latest_date, \
        chart_json_2 = chart_json_2, recent=most_recent_cases,\
        business_no_underscore = business_no_underscore, \
        short_string = short_string, long_string = long_string, \
        default = default, \
        t1 = round(table_values[0][0],3), t2 = round(table_values[1][0],3),\
        t3 = round(table_values[2][0],3), t4 = round(table_values[3][0],3), \
        t5 = round(table_values[0][1],3), t6 = round(table_values[1][1],3), \
        t7 = round(table_values[2][1],3), t8 = round(table_values[3][1],3), \
        t9 = round(table_values[0][2],3), t10 = round(table_values[1][2],3), \
        t11 = round(table_values[2][2],3), t12 = round(table_values[3][2],3), \
        t13 = round(table_values[0][3],3), t14 = round(table_values[1][3],3), \
        t15 = round(table_values[2][3],3), t16 = round(table_values[3][3],3))
    else:
        cases = list(app.vars['cases'].values)
        for i in range(25,31):
            cases.append(float(request.form[f'nov{i}']))
        for i in range(1,9):
            cases.append(float(request.form[f'dec{i}']))
        interest_path = prediction_plots.make_interest_path(cases,app.vars['interests'],app.vars['coefs'])
        json = prediction_plots.make_user_altair(cases,interest_path)
        return render_template('user_json.html',chart_json=json)
if __name__=='__main__':
    app.run()
