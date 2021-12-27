import numpy as np
import pandas as pd
import deps.states.get_states as gs
import plotly.graph_objects as go

# Loading in commitments file (local)
df = pd.read_csv("/home/justinmiller/tpMain/commitments/Commitment Form 2021.csv")
print("Loaded in " + str(len(df)) + " commitments.")
states_raw = df["STATE"].values

# Getting cleaned states
states = gs.get_states(states_raw)

# Removing unknowns
known_idx = [idx for idx in range(len(states)) if states[idx] != "UNKNOWN"]
states = np.array(states)[known_idx]
states = [state.upper() for state in states] # Getting as uppercase to work with plotly
print("We have " + str(len(states)) + " plottable commitments")

# Trimming df as well and adding states back into STATE column
df = df.iloc[known_idx]
df["STATE"] = states

# Now we group it as a collection

count = df.groupby("STATE").agg({df.columns[0]:len})
count = count.apply(lambda x:x.sort_values(ascending=False))
print("State Counts: ")
print(count)

fig = go.Figure(data=go.Choropleth(type='choropleth',
        colorscale = 'greens',
        autocolorscale = True,
        locations = list(count.index),
        z = list(count[df.columns[0]]),
        locationmode = 'USA-states',
        marker_line_color='black'
))

fig.update_layout(title_text = 'Tree-Plenish 2021 Event Recruitment Process',
        geo = dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)'),)

fig.show()