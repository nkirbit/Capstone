import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import statsmodels.stats as sm_stat
import statsmodels.tsa as smt
import scipy.optimize as optimize
import statsmodels.formula.api as smf
import re

def generate_model(phrase):
    cases = pd.read_csv('WeightedCases.csv')
    interest = pd.read_csv(phrase +'_cleaned.csv')
    df,num_states,eligible_states = get_dataframe(cases, interest)
    model = x_lags_week(df,4,num_states,eligible_states)    
    return model

def get_dataframe(cases,interest):
    eligible_states = list(interest['State'])
    num_states = len(eligible_states)
    melted_interest = melt_interest(interest)
    melted_cases = melt_cases(cases,eligible_states)
    eligible_states = [add_underscore(state) for state in eligible_states]
    x = melted_cases
    y = melted_interest.iloc[:,1]
    x['y'] = y
    df = x.rename(columns={'Cases':'x'})
    return df, num_states, eligible_states

def melt_interest(interest):
    analysis_start = pd.to_datetime('2020-04-15')
    melted = pd.melt(interest, id_vars=['State'],var_name='Date',value_name='Interest').reset_index(drop=True)
    melted['DateTime'] = pd.to_datetime(melted['Date'])
    melted = melted.drop('Date',axis=1).rename({'DateTime':'Date'},axis = 1).sort_values(['State','Date'])
    melted = melted[melted['Date'] > analysis_start].reset_index(drop = True)
    return melted

def melt_cases(cases,eligible_states):
    analysis_start = pd.to_datetime('2020-04-15')
    melted_cases = pd.melt(cases, id_vars=['State'],var_name='Date',value_name='Cases').reset_index(drop=True)
    melted_cases['DateTime'] = pd.to_datetime(melted_cases['Date'])
    melted_cases = melted_cases.drop('Date',axis=1).rename({'DateTime':'Date'},axis = 1).sort_values(['State','Date'])
    melted_cases = melted_cases[melted_cases['Date'] < pd.to_datetime('2020-09-30')]
    melted_cases = melted_cases[melted_cases['Date'] > analysis_start]
    melted_cases = melted_cases[melted_cases['State'].isin(eligible_states)]
    melted_cases['Day'] = melted_cases['Date'].apply(lambda x: x.dayofweek)
    melted_cases['Month'] = melted_cases['Date'].apply(lambda x: x.month)
    melted_cases['State'] = melted_cases['State'].apply(lambda x: add_underscore(x))
    melted_cases = pd.get_dummies(melted_cases,columns=['Day','State','Month'])
    melted_cases = melted_cases.drop('Date',axis='columns').reset_index(drop=True)
    return melted_cases

def x_lags_week(df, num_lags, num_states,eligible_states):
    lag_string = make_lag_string(num_lags)
    equation_string = 'y ~ 1' + lag_string +'+ Day_0 + Day_1 + Day_2 + Day_3 + Day_4 + Day_5 +Month_4 + Month_5 + Month_6 + Month_7 + Month_8 + Month_9 + State_California' + make_state_dummy_string(eligible_states)
    model_est = smf.ols(equation_string, data = df)
    model_fit = model_est.fit()
    return model_fit

def lag(x, n,num_states):
    if n == 0:
        return x
    x = x.copy()
    x[n:] = x[0:-n]
    num_days = len(x) / num_states
    for i in range(num_states):
        start = int(i * num_days)
        end = start + n
        x[start:end] = np.nan
    return x

def make_state_dummy_string(state_list):
    string = ''
    for state in state_list[:-1]:
        string += f'+ State_{state}'
    return string

def make_lag_string(num_lags):
    string = ''
    for i in range(1,num_lags+1):
        string += f' + lag(x,{i},num_states)'
    return string

def add_underscore(state_name):
    change = re.sub(' ','_',state_name)
    return change
