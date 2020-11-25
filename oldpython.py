import altair as alt
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

def generate_chart(filename):

    df_long = pd.read_csv(f'{filename}.csv')
    state_names = ["Alaska", "Alabama", "Arkansas", "Arizona", "California", \
    "Colorado", "Connecticut", "District of Columbia", "Delaware", "Florida", \
    "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", \
    "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan",\
    "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina",\
    "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", \
    "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",\
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",\
    "Utah", "Virginia", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]
    base = alt.Chart(df_long).mark_line().encode(
    alt.X('Date:T'),
    alt.Y('Cases', title=" "),
    color = "State:N"
    )

    # A dropdown filter
    columns=state_names[0:19]
    column_dropdown = alt.binding_select(options=columns)
    column_select = alt.selection_single(
        fields=['State'],
        on='doubleclick',
        clear=False,
        bind=column_dropdown,
        name="y ",
        init={'State': "Alabama"}
        )

    filter_columns = base.add_selection(
            column_select
            ).transform_filter(
            column_select
            )

    chart = filter_columns.to_json()
    return chart


@app.route('/', methods=['GET', 'POST'])
def index():

    chart_json = generate_chart('altair')

    return render_template('index.html', chart_json=chart_json)

if __name__=='__main__':
    app.run()
