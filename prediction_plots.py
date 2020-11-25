import pandas as pd
import altair as alt
import datetime
import numpy as np

def predictions(phrase,state,state_df,coefs,state_pop):
    recent_interest, recent_cases, recent_stdev, big_trend = prediction_setup(phrase,state_df,state,state_pop)
    case_path_1 = choose_case_path(recent_cases, delta = 0)
    case_path_2 = choose_case_path(recent_cases, delta = (recent_cases[-1]-recent_cases[-2]))
    case_path_3 = choose_case_path(recent_cases, delta = (recent_cases[-1] - recent_cases[0])/8)
    case_path_4 = choose_case_path(recent_cases, delta = 0, random_walk = True, stdev = recent_stdev)
    case_path_5 = choose_case_path(recent_cases, delta = 0, random_walk = True, stdev = recent_stdev, drift = big_trend)
    interest_path_1 = make_interest_path(case_path_1,recent_interest,coefs)
    interest_path_2 = make_interest_path(case_path_2,recent_interest,coefs)
    interest_path_3 = make_interest_path(case_path_3,recent_interest,coefs)
    interest_path_4 = make_interest_path(case_path_4,recent_interest,coefs)
    interest_path_5 = make_interest_path(case_path_5,recent_interest,coefs)
    return case_path_1, case_path_2, case_path_3, case_path_4, case_path_5, \
     interest_path_1, interest_path_2, interest_path_3, interest_path_4, \
     interest_path_5
#    altair_json = make_altair(val1, val2, interest1, interst2)

def prediction_setup(phrase,state_df,state,state_pop):
    startday = datetime.date(2020, 11, 15)
    endday = datetime.date(2020, 11, 24)
    numdays = (endday - startday).days
    date_list = [startday + datetime.timedelta(days=x) for x in range(numdays)]
    recent = pd.read_csv(f'recent_data\{phrase}_recent.csv')
    recent.columns = ['State'] + date_list
    melted = recent.melt(id_vars="State",value_vars=date_list)
    melted["Date"] = pd.to_datetime(melted['variable'])
    melted = melted.drop('variable',axis=1)
    melted = melted.rename(columns={'value': 'Interest'})
    recent_interest = melted[melted['State']==state]['Interest']
    daily = state_df.transpose().diff(1)
    daily = daily.rename(columns={state:'Cases'})['Cases']
    daily = (daily / state_pop) * 100000
    #Want to find the movement of new cases for random walk, so will
    #examine second differences.
    second_diff = daily.diff(1)
    recent_stdev = np.std(second_diff[60:])
    big_trend = (daily[-1] - daily[-61]) / 60
    recent_cases = daily[9:]
    return recent_interest, recent_cases, recent_stdev, big_trend

def choose_case_path(cases,delta=0, random_walk = False,stdev = 0, drift=0):
    pred = cases.values
    starting_spot = pred[-1]
    if random_walk:
        steps = np.random.normal(loc = 0, scale = stdev, size = 14)
        steps_with_drift = steps + drift
        for i in range(14):
            new_spot = starting_spot + steps_with_drift[i]
            pred = np.append(pred,new_spot)
            starting_spot = new_spot
    else:
        for i in range(14):
            new_spot = starting_spot + delta
            pred = np.append(pred,new_spot)
            starting_spot = new_spot
    return pred

def make_interest_path(cases_path,interest,coefs):
    #Cases_Path is a array of length 23. Interest is an array of length 9.
    #We will use the future path of cases to predict the path of interest,
    #using the coefficients as steps.
    c1,c2,c3,c4 = coefs[0],coefs[1],coefs[2],coefs[3]
    #The first one added is the 10th interest, at the 9th index.
    #The differences will be from 6-5 to 9-8.
    interest_path = interest.values
    most_recent_step = interest_path[-1]
    for i in range(9,23):
        delta = c4 * (cases_path[i-3] - cases_path[i-4]) \
                + c3 * (cases_path[i-2] - cases_path[i-3]) \
                + c2 * (cases_path[i-1] - cases_path[i-2]) \
                + c1 * (cases_path[i] - cases_path[i-1])
        new_step = most_recent_step + delta
        interest_path = np.append(interest_path,new_step)
        most_recent_step = new_step
    return interest_path

#def make_altair(val1, val2, interest1, interest2):
#    df = pd.DataFrame(val1,val2,interest1,interest2)
#    return df
