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

# App layout
app.layout = html.Div([
    html.H1("US Gun Violence Analysis (1985-2018)", className="header-title"),
    html.P("An interactive analysis of gun violence incidents in the United States from 1985 to 2018.", className="header-description"),
    
    # Dropdown for selecting visualization
    dcc.Dropdown(
        id='visualization-dropdown',
        options=[
            {'label': 'Victim Demographics', 'value': 'victim_demographics'},
            {'label': 'Weapon Used', 'value': 'weapon_used'},
            {'label': 'Circumstances of Incidents', 'value': 'incident_circumstances'},
            {'label': 'Geographical Analysis', 'value': 'geographical_analysis'},
            {'label': 'Relationship between Offender and Victim', 'value': 'relationship_offender_victim'}
        ],
        value='victim_demographics',
        clearable=False
    ),
    
    # Div for displaying selected visualization
    html.Div(id='visualization-output')
])

# Callback to update visualization based on dropdown selection
@app.callback(
    Output('visualization-output', 'children'),
    [Input('visualization-dropdown', 'value')]
)
def update_visualization(selected_option):
    if selected_option == 'victim_demographics':
        # Victim Demographics: Age distribution
        age_fig = px.histogram(df, x='victim_age', title='Age Distribution of Gun Violence Victims')
        return dcc.Graph(figure=age_fig)
    
    elif selected_option == 'weapon_used':
        # Weapon Used: Types of weapons
        weapon_fig = px.bar(df['weapon_used'].value_counts(), x=df['weapon_used'].value_counts().index, y=df['weapon_used'].value_counts().values, 
                             labels={'x': 'Weapon Type', 'y': 'Count'}, title='Types of Weapons Used in Gun Violence Incidents')
        return dcc.Graph(figure=weapon_fig)
    
    elif selected_option == 'incident_circumstances':
        # Circumstances of Incidents: Top 10 circumstances
        circumstance_fig = px.bar(df['circumstance'].value_counts().head(10), x=df['circumstance'].value_counts().head(10).index, y=df['circumstance'].value_counts().head(10).values,
                                  labels={'x': 'Circumstance', 'y': 'Count'}, title='Top 10 Circumstances of Gun Violence Incidents')
        return dcc.Graph(figure=circumstance_fig)
    
    elif selected_option == 'geographical_analysis':
        # Geographical Analysis: Incidents by state
        state_fig = px.choropleth(df.groupby('state').size().reset_index(name='count'), 
                                   locations='state', locationmode='USA-states', color='count', 
                                   scope="usa", title='Gun Violence Incidents by State')
        return dcc.Graph(figure=state_fig)
    
    elif selected_option == 'relationship_offender_victim':
        # Relationship between Offender and Victim
        relationship_fig = px.histogram(df, x='offenders_relationship_to_victim_grouping', title='Relationship between Offender and Victim')
        return dcc.Graph(figure=relationship_fig)
    
    else:
        return html.P("Please select a visualization option.")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
