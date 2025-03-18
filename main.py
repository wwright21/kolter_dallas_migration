import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# set page configurations
st.set_page_config(
    page_title=f"Migration Explorer",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"  # 'collapsed' or 'expanded'
)

# whole page variables
metro_var = "Dallas-Fort Worth"
default_county = "Dallas"
state_var = "Texas"
stateAbbrev_var = "TX"
map_starting_zoom = 8
map_starting_extent = [32.9935342827898, -96.90176513963999]

# sidebar containing st.multiselect for county selection
with st.sidebar:
    widget_font_size = 18
    widget_font_color = '#36454F'
    widget_font_weight = 700

    # multi-select label
    st.markdown(
        f"""
        <div style='text-align: center; margin-top: 0px; margin-bottom: 0px;'>
            <span style='font-size: {widget_font_size}px; color: {widget_font_color}; font-weight: {widget_font_weight};'>
                Select counties:
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    county_var = st.multiselect(
        label="",
        options=[
            "Dallas",
            "Tarrant",
            "Collin",
            "Denton"
        ],
        default=[default_county],
    )

    st.divider()

    # Radio label
    st.markdown(
        f"""
        <div style='text-align: center; margin-top: 0px; margin-bottom: 25px;'>
            <span style='font-size: {widget_font_size}px; color: {widget_font_color}; font-weight: {widget_font_weight};'>
                Select migration variable:
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Radio buttons
    dash_variable = st.radio(
        "",
        ["People", "Dollars"],
        horizontal=True,
        label_visibility='collapsed'
    )


# -v-v-v-v-v- main section v-v-v-v-v-

# dashboard title
title_font_size = 30
title_margin_top = 0
title_margin_bottom = 20

# Dashboard title
st.markdown(
    f"""
    <div style='margin-top: {title_margin_top}px; margin-bottom: {title_margin_bottom}px; text-align: center;'>
        <span style='font-size: {title_font_size}px; font-weight: 700; color: #36454F;'>
            {metro_var} Migration Dashboard
        </span>
    </div>
    """,
    unsafe_allow_html=True
)


# define a function to display the selected counties
def format_county_names(county_list):
    if not county_list:
        return "No counties selected"

    if len(county_list) == 1:
        return f"{county_list[0]}"

    if len(county_list) == 2:
        return f"{county_list[0]} & {county_list[1]}"

    return f"{', '.join(county_list[:-1])}, & {county_list[-1]}"


# Format the county names
formatted_counties = format_county_names(county_var)


# insert text below map to instruct the user to make selections in the sidebar using st.markdown
if len(county_var) == 0:
    st.markdown(
        f"""
        <div style='margin-top: 00px; margin-bottom: 10px; text-align: center;'>
            <span style='font-size: 18px; font-weight: 200; color: #36454F;'>
                <em>No counties selected. Add one or more counties in the sidebar dropdown menu.</em>
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"""
        <div style='margin-top: 00px; margin-bottom: 10px; text-align: center;'>
            <span style='font-size: 18px; font-weight: 200; color: #36454F;'>
                <em>{formatted_counties} County (shown in blue) migration data only. Expand the sidebar to add or remove other metro counties from the dashboard as well as change the migration variable.</em>
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

# -v-v-v-v-v- CONTEXT MAP v-v-v-v-v-
# load the Geopackage file
county_outlines = gpd.read_file(
    'Assets/county_outlines.gpkg',
)

# Set the 'selected' column to True for the 'Dallas' county
county_outlines['selected'] = county_outlines['NAME'].isin(county_var)
county_outlines['selected'] = county_outlines['selected'].map(
    {True: 'Selected', False: 'Not Selected'})

# Create a Plotly Express map with the loaded Geopackage data
fig = px.choropleth_mapbox(
    county_outlines,
    geojson=county_outlines.geometry,
    locations=county_outlines.index,
    color='selected',
    color_discrete_map={
        "Selected": "rgba(8,48,107,0.7)",  # Navy blue fill for selected
        "Not Selected": "rgba(0,0,0,0)"    # Transparent for not selected
    },
    custom_data=['NAME'],
    center={'lat': map_starting_extent[0], 'lon': map_starting_extent[1]},
    zoom=map_starting_zoom,
    mapbox_style='streets',
    labels={'NAME': 'County'},
)


# Update the map layout
fig.update_layout(
    mapbox_accesstoken='pk.eyJ1Ijoid3dyaWdodDIxIiwiYSI6ImNsZTV3NWplcDBiam4zbnBoMDRqOGJhY2QifQ.Y8ZdfLVFyETj4qc8JNiaHw',
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    showlegend=False,
)

# Will color all county borders, regardless of selection
fig.update_traces(
    hovertemplate="<b>%{customdata[0]} County</b><extra></extra>",
    marker_line_color='black',
    marker_line_width=1,
    hoverlabel=dict(
        bgcolor="#fffaf6",     # Background color
        font_size=14,        # Font size
        font_family="Monospace",  # Font family
        font_color="black",  # Text color
        bordercolor="black",  # Border color
    )
)

# hide modebar
config = {'displayModeBar': False}

# Display the map
st.plotly_chart(
    fig,
    config=config,
    theme='streamlit',
    use_container_width=True
)


# horizontal line
st.write('---')

st.write("")


# -v-v-v-v-v-v-v LINE CHART v-v-v-v-v-v-v-v
# read in data
df = pd.read_csv('Assets/migration_data.csv')
df = df[df['primary_county'].isin(county_var)]
line_chart_data = df[df['migration_type'] == 'total']
line_chart_summary = line_chart_data.groupby('year').sum().reset_index()


dash_variable_dict = {
    "People": [
        "people_net",  # dataframe column
        ",.0f",       # y-axis formatting
        "%{y:,.0f}",  # hover label formatting
        5000,          # y-axis dtick
        "",  # y-axis prefix for bar chart
        "%{x:,.0f}",
    ],
    "Dollars": [
        "agi_net",
        None,
        "%{y:$,.0f}",
        500000000,
        "$",  # y-axis prefix for bar chart
        "%{x:$,.0f}",
    ]
}

if len(county_var) == 0:
    line_chart_title = "Please select a county from the sidebar to see annual trends"
else:
    line_chart_title = f'Net Migration of {dash_variable} into {formatted_counties} County Since 2016'

# create fig object
fig = px.line(
    line_chart_summary,
    x='year',
    y=dash_variable_dict[dash_variable][0],
    title=line_chart_title,
    height=440,
)

# update fig layout
fig.update_layout(
    margin=dict(l=20, r=20, t=50, b=0),
    hovermode='x unified',
    hoverlabel=dict(
        font_size=16,
        bgcolor='#36454F',
        font_color='#fffaf6'
    ),
    title={
        'font': {
            'color': '#000',
            'weight': 'normal'
        },
        'x': 0.5,
        'y': 0.97,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis=dict(
        title='',
        tickfont=dict(
            size=16,
            color='#000'
        ),
        gridcolor='#000'
    ),
    yaxis=dict(
        title='',
        tickfont=dict(
            size=16,
            color='#000'
        ),
    ),
    plot_bgcolor='#fffaf6',
    paper_bgcolor='#fffaf6'
)

# Custom y-axis formatting for Dollars
if dash_variable == "Dollars":
    if len(county_var) == 0:
        st.error("Please select at least one county.")
    else:
        y_values = line_chart_summary[dash_variable_dict[dash_variable][0]].values
        min_y = min(y_values)
        # set max_y to be the max of y_values plus a little extra
        max_y = max(y_values) * 1.1
        dtick = dash_variable_dict[dash_variable][3]

        tickvals = list(range(int(min_y), int(max_y) + 1, dtick))
        ticktext = [f"${val / 1000000000:.1f}B" for val in tickvals]

        fig.update_layout(yaxis=dict(tickvals=tickvals, ticktext=ticktext))
else:
    if len(county_var) == 0:
        st.error("Please select at least one county.")
    else:
        fig.update_layout(yaxis=dict(
            tickformat=dash_variable_dict[dash_variable][1]))

# customize line trace
line_color = '#08306b'
fig.update_traces(
    hovertemplate=dash_variable_dict[dash_variable][2],
    mode='lines+markers',
    line=dict(
        color=line_color,
        width=3,
        dash='solid'
    ),
    marker=dict(
        size=8
    )
)

fig.update_xaxes(
    showline=True,
    linewidth=1,
    linecolor='#000'
)
fig.update_yaxes(
    showline=True,
    linewidth=1,
    linecolor='#000',
    showgrid=False
)

config = {'displayModeBar': False}
st.plotly_chart(
    fig,
    config=config,
    theme='streamlit',
    use_container_width=True,
)

# KPI readout
var_KPI = line_chart_summary[dash_variable_dict[dash_variable][0]].sum()

if dash_variable == 'People':
    kpi_formatter = ''
else:
    kpi_formatter = '$'

st.markdown(
    f"""
    <div style='margin-top: 5px; margin-bottom: 0px; text-align: center'>
        <span style='font-size: 16px; font-weight: 100; color: #36454F;'>
            Cumulative Total Since 2016: <b>{kpi_formatter}{var_KPI:,}</b>
            <br><i>Note: 2023 data scheduled for release in June 2025.</i>
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
st.write('---')


# -v-v-v-v-v-v- METRO BAR CHART -v-v-v-v-v-v-

if len(county_var) == 0:
    st.error("Please select at least one county.")
else:
    st.markdown(
        f""" 
        <div style='margin-top: 0px; margin-bottom: 10px; text-align: center'>
            <span style='font-size: 16px; font-weight: 200; color: #36454F;'>
                Metro Areas (and Cumulative Total) Sending <br/>the Most {dash_variable} Into {formatted_counties} County Since 2016: 
            </span>
        </div>
        """,
        unsafe_allow_html=True)


# get the top metros, counties
metro_rollup = df.groupby('aux_GeoRollup')[
    dash_variable_dict[dash_variable][0]].sum().nlargest(5).reset_index()


# function to format large numbers
def format_large_numbers(value, use_dollar_sign=True):
    """Formats numbers with K, M, B suffixes, optionally adding a dollar sign."""
    if value >= 1_000_000_000:
        formatted = f"{value / 1_000_000_000:.1f}B"  # Billions
    elif value >= 1_000_000:
        formatted = f"{value / 1_000_000:.1f}M"  # Millions
    elif value >= 1_000:
        formatted = f"{value / 1_000:.1f}K"  # Thousands
    else:
        formatted = f"{value:.0f}"  # No suffix

    return f"${formatted}" if use_dollar_sign else formatted


# Determine whether to use the dollar sign
use_dollar = dash_variable == "Dollars"

# Apply function with conditional dollar sign
metro_rollup["formatted_x"] = metro_rollup[dash_variable_dict[dash_variable][0]].apply(
    lambda x: format_large_numbers(x, use_dollar)
)


fig_metro_chart = px.bar(
    metro_rollup,
    x=dash_variable_dict[dash_variable][0],
    y='aux_GeoRollup',
    title=None,
    text=metro_rollup["formatted_x"],
    height=200,
)

# Update layout
fig_metro_chart.update_layout(
    margin=dict(l=0, r=0, t=10, b=0),
    yaxis_title=None,
    yaxis=dict(
        autorange="reversed",
        tickfont=dict(size=14, weight="bold")
    ),
    xaxis_title=None,
    xaxis_tickprefix=dash_variable_dict[dash_variable][4],
    uniformtext_minsize=13,
    uniformtext_mode='hide',
    barcornerradius=5,
)

fig_metro_chart.update_traces(
    hoverinfo="skip",
    hovertemplate=dash_variable_dict[dash_variable][5],
    marker_color='#08306b',
    textposition='inside',
    textangle=0,
    texttemplate='%{text}',
)

fig_metro_chart.layout.xaxis.fixedrange = True
fig_metro_chart.layout.yaxis.fixedrange = True

st.plotly_chart(
    fig_metro_chart,
    config=config,
    theme='streamlit',
    use_container_width=True,
    key='metro_chart'
)

# -v-v-v-v-v-v- COUNTY BAR CHART -v-v-v-v-v-v-
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
if len(county_var) == 0:
    st.error("Please select at least one county.")
else:
    st.markdown(
        f""" 
        <div style='margin-top: 0px; margin-bottom: 10px; text-align: center'>
            <span style='font-size: 16px; font-weight: 200; color: #36454F;'>
                Counties (and Cumulative Total) Sending <br/>the Most {dash_variable} Into {formatted_counties} County Since 2016: 
            </span>
        </div>
        """,
        unsafe_allow_html=True)

df['aux_countyState'] = df['aux_county'] + ' County, ' + df['aux_state']

county_rollup = df.groupby('aux_countyState')[
    dash_variable_dict[dash_variable][0]].sum().nlargest(5).reset_index()

# Apply function with conditional dollar sign
county_rollup["formatted_x"] = county_rollup[dash_variable_dict[dash_variable][0]].apply(
    lambda x: format_large_numbers(x, use_dollar)
)

fig_county_chart = px.bar(
    county_rollup,
    x=dash_variable_dict[dash_variable][0],
    y='aux_countyState',
    title=None,
    text=county_rollup["formatted_x"],
    height=200
)

# Update layout
fig_county_chart.update_layout(
    margin=dict(l=0, r=0, t=10, b=0),
    yaxis_title=None,
    yaxis=dict(
        autorange="reversed",
        tickfont=dict(size=14, weight="bold")
    ),
    xaxis_title=None,
    xaxis_tickprefix=dash_variable_dict[dash_variable][4],
    uniformtext_minsize=13,
    uniformtext_mode='hide',
    barcornerradius=5,
)

fig_county_chart.update_traces(
    hoverinfo="skip",
    hovertemplate=dash_variable_dict[dash_variable][5],
    marker_color='#08306b',
    textposition='inside',
    textangle=0,
    texttemplate='%{text}',
)

fig_county_chart.layout.xaxis.fixedrange = True
fig_county_chart.layout.yaxis.fixedrange = True

st.plotly_chart(
    fig_county_chart,
    config=config,
    theme='streamlit',
    use_container_width=True,
    key='county_chart'
)

# # Iterate over the columns and top 5 cities
# for col, (metro, migration_total) in zip([col1, col2, col3, col4, col5], metro_rollup.items()):
#     with col:
#         # Display ranking, from 1 to 5
#         metro_ranking = metro_rollup.index.get_loc(metro) + 1
#         st.markdown(
#             f"""
#             <div style='margin-top: 0px; margin-bottom: 0px; text-align: center'>
#                 <span style='font-size: 18px; font-weight: 200; color: #36454F;'>
#                     <b>{metro_ranking}</b>
#                 </span>
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

#         # Display the metro name
#         st.markdown(
#             f"""
#             <div style='margin-top: 0px; margin-bottom: -20px; text-align: center'>
#                 <span style='font-size: 14px; font-weight: 200; color: #36454F;'>
#                     <b>{metro}</b>
#                 </span>
#             </div>
#             """,
#             unsafe_allow_html=True)

#         # Display migration variable under metro name
#         st.markdown(
#             f"""
#             <div style='margin-top: 0px; margin-bottom: 0px; text-align: center'>
#                 <span style='font-size: 13px; font-weight: 200; color: #36454F;'>
#                     ({kpi_formatter}{migration_total:,})
#                 </span>
#             </div>
#             """,
#             unsafe_allow_html=True)

# finally, show the whole source data
st.write('---')
st.write("")
st.markdown(
    f"""
    <div style='margin-top: -30px; margin-bottom: 20px; text-align: left'>
        <span style='font-size: 16px; font-weight: 200; color: #36454F;'>
            See below table for migration source data from the 
            <a href="https://www.irs.gov/statistics/soi-tax-stats-migration-data" 
               target="_blank" 
               style="color: #08306b; 
               text-decoration: none;">
               <b>IRS Statistics of Income.</b>
            </a>
            Each row represents the flow of people, adjusted gross income (AGI), and AGI per capita into and out of {formatted_counties} County, {state_var} relative to the other county for the given year. 
            <br/><br/>Click on any of the column headers to sort the data ascending and then descending. A third click on the column header will remove the sort. Finally, hover over the table to reveal control buttons in the top-right corner of the table to download a copy of the data to CSV, search within the table, or expand the table to fullscreen.
        </span>
    </div>
    """,
    unsafe_allow_html=True)

df_display = df[df['migration_type'] != 'total']
df_display['year'] = df_display['year'].astype(str)
df_display = df_display.drop(
    columns=['migration_type', 'primary_FIPS', 'aux_FIPS'])
df_display = df_display.rename(columns={
    'year': 'Year',
    'aux_county': 'County',
    'aux_state': 'State',
    'aux_GeoRollup': 'Metro Area',
    'agi_capita_inflow': f'AGI Per Capita into Selected County',
    'agi_capita_outflow': f'AGI Per Capita leaving Selected County',
    'agi_inflow': f'AGI into Selected County',
    'agi_outflow': f'AGI leaving Selected County',
    'people_inflow': f'Persons into Selected County',
    'people_outflow': f'Persons leaving Selected County'
})
df_display = df_display[[
    'Year',
    'County',
    'State',
    'Metro Area',
    f'AGI into Selected County',
    f'Persons into Selected County',
    f'AGI Per Capita into Selected County',
    f'AGI leaving Selected County',
    f'Persons leaving Selected County',
    f'AGI Per Capita leaving Selected County'
]]

# Format the "AGI" column as currency
formatted_df = df_display.style.format({
    f"AGI Per Capita into Selected County": "${:,.0f}",
    f"AGI Per Capita leaving Selected County": "${:,.0f}",
    f"AGI into Selected County": "${:,.0f}",
    f"AGI leaving Selected County": "${:,.0f}",
    f"Persons into Selected County": "{:,.0f}",
    f"Persons leaving Selected County": "{:,.0f}",
})

st.dataframe(formatted_df)

st.write("")
st.write("")
st.write("")
col1, col2 = st.columns([4, 1])
col1.markdown(
    f"""
    For questions about this data explorer or the source data, please contact Will Wright by clicking <a href="mailto:williamcwrightjr@gmail.com?subject=Question about {county_var} County Migration Dashboard" style="text-decoration: none; color: #08306b;"><b>here</b>.</a> 
    """,
    unsafe_allow_html=True)
col2.image('Assets/kolter2.png', width=100)

# the custom CSS lives here:
hide_default_format = """
    <style>
        .reportview-container .main {visibility: hidden;}
        #MainMenu, header, footer {visibility: hidden;}
        div.stActionButton{visibility: hidden;}
        [class="stAppDeployButton"] {
            display: none;
        }
        .stRadio [role=radiogroup] p {
            font-size: 17px;
        }
        .stRadio [role=radiogroup] {
            justify-content: center;
            background-color: #fffaf6;
            border-radius: 7px;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 0px;
        }
        div[class="mapboxgl-map"] {
            border: 2px solid black;
        }
        .stMainBlockContainer {
            max-width: 800px;  
        }
    </style>
"""

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)
