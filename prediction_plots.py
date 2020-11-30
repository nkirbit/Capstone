import pandas as pd
import altair as alt
import datetime
import numpy as np

def predictions(phrase,state,state_df,coefs,state_pop):
    recent_interest, recent_cases, recent_stdev, big_trend = prediction_setup(phrase,state_df,state,state_pop)
    c1 = choose_case_path(recent_cases, delta = 0)
    c2 = choose_case_path(recent_cases, delta = (recent_cases[-1]-recent_cases[-2]))
    c3 = choose_case_path(recent_cases, delta = (recent_cases[-1] - recent_cases[0])/8)
    c4 = choose_case_path(recent_cases, delta = 0, random_walk = True, stdev = recent_stdev)
    c5 = choose_case_path(recent_cases, delta = 0, random_walk = True, stdev = recent_stdev, drift = big_trend)
    i1 = make_interest_path(c1,recent_interest,coefs)
    i2 = make_interest_path(c2,recent_interest,coefs)
    i3 = make_interest_path(c3,recent_interest,coefs)
    i4 = make_interest_path(c4,recent_interest,coefs)
    i5 = make_interest_path(c5,recent_interest,coefs)
    json = make_altair(c1,c2,c3,c4,c5,i1,i2,i3,i4,i5)
    most_recent_cases = np.round(recent_cases[-1],2)
    return json, most_recent_cases, recent_interest, recent_cases
#    altair_json = make_altair(val1, val2, interest1, interst2, other stuf)

def prediction_setup(phrase,state_df,state,state_pop):
    startday = datetime.date(2020, 11, 15)
    endday = datetime.date(2020, 11, 24)
    numdays = (endday - startday).days
    date_list = [startday + datetime.timedelta(days=x) for x in range(numdays)]
    recent = pd.read_csv(f'recent_data/{phrase}_recent.csv')
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
    recent_cases = daily[-9:]
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

def make_altair(c1,c2,c3,c4,c5,i1,i2,i3,i4,i5):
    interests = np.round(np.concatenate((i1,i2,i3,i4,i5)),2)
    covids = np.round(np.concatenate((c1,c2,c3,c4,c5)),2)
    labels = np.concatenate((np.full(23,'Constant'),np.full(23,'Most recent change'),np.full(23,'Average change'),np.full(23,'Random walk'),np.full(23,'Random walk with drift')))
    dates = np.tile([pd.to_datetime(datetime.datetime(2020,11,15) + datetime.timedelta(days=x)) for x in range(23)],5)
    data = np.array([dates,interests,covids,labels]).transpose()

    label_list = pd.DataFrame({'Type of Path': ['Constant', 'Most recent change', 'Average change','Random walk','Random walk with drift']})

    df = pd.DataFrame(data, columns = ['Date','interest','covid','Type of Path'])
    df = df[df['Date']>pd.to_datetime(datetime.datetime(2020,11,23))]

    selection = alt.selection_multi(fields=['Type of Path'])
    color = alt.condition(selection, alt.Color('Type of Path:N'), alt.value('lightgray'))
    label_selector = alt.Chart(label_list).mark_rect().encode(y='Type of Path', color=color).add_selection(selection)
    covid_chart = alt.Chart(df).mark_line().encode(alt.X('Date:T'), y=alt.Y('covid',title='Possible Covid Path'), color='Type of Path').transform_filter(selection)
    interest_chart = alt.Chart(df).mark_line().encode(alt.X('Date:T'), y=alt.Y('interest',title='Predicted Interest Path'), color='Type of Path').transform_filter(selection)


    json = (label_selector & (covid_chart | interest_chart)).to_json()
    return json

def make_user_altair(cases,interest):
    dates = [pd.to_datetime(datetime.datetime(2020,11,15) + datetime.timedelta(days=x)) for x in range(23)]
    data = np.array([dates,cases,interest]).transpose()
    df = pd.DataFrame(data, columns = ['Date','covid','interest'])
    melted = pd.melt(df,id_vars = 'Date')
    chart = alt.Chart(melted).mark_line().encode(
        x='Date:T',
        y=alt.Y('value:Q',title='Interest in search term'),
        color='variable')
    json = chart.to_json()
    return json
