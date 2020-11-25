### state should be a capitalized name with spaces.
### ie. 'Delaware' or 'District of Columbia'
import pandas as pd
import datetime
import altair as alt 

def make_covid_plot(state):
    state_df, state_pop = get_data(state)
    altair_json = make_daily_cumul_graph(state_df,state)
    return altair_json

def get_data(state):
    ### GET MOST RECENT COVID DATA
    df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
    df.drop(columns = ['UID','iso2','iso3','code3','FIPS','Admin2','Lat','Long_','Combined_Key'],inplace=True)
    state_df = df[df['Province_State']==state].groupby('Province_State').sum()
    most_recent_date = state_df.columns[-1]
    ###GET STATE POPULATION
    pops = pd.read_csv('https://raw.githubusercontent.com/COVID19Tracking/associated-data/master/us_census_data/us_census_2018_population_estimates_states.csv')
    pop = pops[pops['state_name'] == 'Alabama']['population'][0]
    ###
    return state_df, pop

def make_daily_cumul_graph(state_df,state):
    ### Make series for cumulative cases for Altair.
    cumulative = state_df.transpose()
    cumulative['Date'] = cumulative.index
    cumulative['Date'] = cumulative['Date'].apply(lambda x: pd.to_datetime(x))
    cumulative = cumulative.rename(columns={state:'cases'})
    cumulative = cumulative[cumulative['Date'] >= datetime.datetime(2020,4,1)]

    ### Make series for daily cases for Altair.
    daily = state_df.transpose().diff(1).rolling(7).mean()
    daily['Date'] = daily.index
    daily['Date'] = daily['Date'].apply(lambda x: pd.to_datetime(x))
    daily = daily.rename(columns={state:'cases'})
    daily = daily[daily['Date'] >= datetime.datetime(2020,4,1)]

    brush = alt.selection(type='interval', encodings=['x'], clear=False)

    base = alt.Chart(daily, width=400, height=400).mark_line().encode(
    alt.X('Date:T', scale=alt.Scale(domain=brush)),
    alt.Y('cases:Q', title=" ")
)
    daily_graph = base.properties(height=240,
    width = 600)

    cumulative_graph = alt.Chart(cumulative).mark_line().encode(
    alt.X('Date:T'),
    alt.Y('cases:Q', title=" ")).properties(
    height=200,
    width = 600).add_selection(brush)

    altair_plot = (daily_graph & cumulative_graph).to_json()

    ##returns a json version of the plot to put on website
    return altair_plot
