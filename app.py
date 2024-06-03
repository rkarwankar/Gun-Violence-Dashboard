import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os

# Load data
data_path = 'data/US_gun_deaths_1985-2018.csv'

# Check if data file exists
if not os.path.exists(data_path):
    raise FileNotFoundError(f"The data file '{data_path}' does not exist.")

# Load the data
df = pd.read_csv(data_path)

# Initialize the app
app = dash.Dash(__name__)

# Extract unique values for dropdown options
years = sorted(df['year'].unique())
states = ['All States'] + sorted(df['state'].unique())
genders = ['All Genders'] + sorted(df['victim_sex'].unique())
age_groups = ['All Ages'] + sorted(df['victim_age'].dropna().astype(str).unique())

# App layout
app.layout = html.Div(className="container", children=[
    html.H1("US Gun Violence Analysis (1985-2018)", className="header-title"),
    html.P("An interactive analysis of gun violence incidents in the United States from 1985 to 2018.", className="header-description"),

    html.Div(className="controls-container", children=[
        html.Div(className="dropdown-container", children=[
            html.Label("Select Year:"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in years],
                value=years[0],
                clearable=False,
                className="dropdown"
            )
        ]),
        html.Div(className="dropdown-container", children=[
            html.Label("Select State:"),
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in states],
                value='All States',
                clearable=False,
                className="dropdown"
            )
        ]),
        html.Div(className="dropdown-container", children=[
            html.Label("Select Gender:"),
            dcc.Dropdown(
                id='gender-dropdown',
                options=[{'label': gender, 'value': gender} for gender in genders],
                value='All Genders',
                clearable=False,
                className="dropdown"
            )
        ]),
        html.Div(className="dropdown-container", children=[
            html.Label("Select Age Group:"),
            dcc.Dropdown(
                id='age-group-dropdown',
                options=[{'label': age, 'value': age} for age in age_groups],
                value='All Ages',
                clearable=False,
                className="dropdown"
            )
        ])
    ]),

    html.Div(id='main-visualization', className="graph-container"),
    html.Div(id='weapon-visualization', className="graph-container"),
    html.Div(id='circumstance-visualization', className="graph-container"),
    html.Div(id='relationship-visualization', className="graph-container")
])

# Callback to update main visualization based on filters
@app.callback(
    [Output('main-visualization', 'children'),
     Output('weapon-visualization', 'children'),
     Output('circumstance-visualization', 'children'),
     Output('relationship-visualization', 'children')],
    [Input('year-dropdown', 'value'),
     Input('state-dropdown', 'value'),
     Input('gender-dropdown', 'value'),
     Input('age-group-dropdown', 'value')]
)
def update_visualizations(selected_year, selected_state, selected_gender, selected_age_group):
    filtered_df = df[df['year'] == selected_year]

    if selected_state != 'All States':
        filtered_df = filtered_df[filtered_df['state'] == selected_state]

    if selected_gender != 'All Genders':
        filtered_df = filtered_df[filtered_df['victim_sex'] == selected_gender]

    if selected_age_group != 'All Ages':
        filtered_df = filtered_df[filtered_df['victim_age'].astype(str) == selected_age_group]

    # Main Visualization: Geographical Analysis
    fig_geo = px.scatter_geo(
        filtered_df,
        locations="state",
        locationmode="USA-states",
        color="victim_race_plus_hispanic",
        hover_name="state",
        size="multiple_victim_count",
        title="Gun Violence Incidents in the US",
        scope="usa"
    )

    fig_geo.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        geo=dict(bgcolor='rgba(0,0,0,0)')
    )

    # Weapon Used Visualization
    weapon_counts = filtered_df['weapon_used'].value_counts().reset_index()
    weapon_counts.columns = ['weapon_used', 'count']
    fig_weapon = px.bar(
        weapon_counts,
        x='weapon_used', y='count',
        labels={'weapon_used': 'Weapon Type', 'count': 'Count'},
        title='Types of Weapons Used in Gun Violence Incidents'
    )

    # Circumstances Visualization
    circumstance_counts = filtered_df['circumstance'].value_counts().reset_index().head(10)
    circumstance_counts.columns = ['circumstance', 'count']
    fig_circumstance = px.bar(
        circumstance_counts,
        x='circumstance', y='count',
        labels={'circumstance': 'Circumstance', 'count': 'Count'},
        title='Top 10 Circumstances of Gun Violence Incidents'
    )

    # Relationship between Offender and Victim Visualization
    fig_relationship = px.histogram(
        filtered_df,
        x='offenders_relationship_to_victim_grouping',
        title='Relationship between Offender and Victim'
    )

    return (
        dcc.Graph(figure=fig_geo),
        dcc.Graph(figure=fig_weapon),
        dcc.Graph(figure=fig_circumstance),
        dcc.Graph(figure=fig_relationship)
    )

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
