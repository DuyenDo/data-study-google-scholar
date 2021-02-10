# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 12:10:31 2020

@author: duyen
"""

import pandas as pd
import os

dirname = os.path.dirname(__file__)
path = os.path.join(dirname, '../data', 'field_based_summary/')

ml_cit = pd.read_csv(path + 'summary_ml_top_citations.csv')
ml_hind = pd.read_csv(path + 'summary_ml_top_hindex.csv')
ml_pub = pd.read_csv(path + 'summary_ml_top_publication.csv')

#ml = ml_cit.merge(ml_hind, left_on='id', right_on='id', how = 'outer')\
#            .merge(ml_pub, left_on='id', right_on='id', how = 'outer')

wl_cit = pd.read_csv(path + 'summary_wireless_top_citations.csv')
wl_hind = pd.read_csv(path + 'summary_wireless_top_hindex.csv')
wl_pub = pd.read_csv(path + 'summary_wireless_top_publication.csv')

ct_cit = pd.read_csv(path + 'summary_comtheo_top_citations.csv')
ct_hind = pd.read_csv(path + 'summary_comtheo_top_hindex.csv')
ct_pub = pd.read_csv(path + 'summary_comtheo_top_publication.csv')

#%%

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns; sns.set()

fig = go.Figure()

# Line plot for the number of cancelled flights
fig.add_trace(
    go.Scatter(name='h-index in total', x=ml_hind['name'], y=ml_hind['h_index'],
               marker=dict(color='rgba(0,0,0,0.8)',)),
)

# Line plot for the number of delayed flights
fig.add_trace(
    go.Scatter(name='h-index in field', x=ml_hind['name'], y=ml_hind['in_field_h_index'],
               marker=dict(color='rgba(222,45,38,0.8)',)),
)

## Set parameters for the plot
#fig.update_xaxes(title_text="<b>Dates</b>", showticklabels=False)
#fig.update_yaxes(title_text="<b>Number of flights</b>")
#
#fig.update_layout(title={'text': "<b>Cancelled flights and Delayed flights per Day</b>",
#                                          'y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'},
#                  autosize=False, width=1000,height=500,
#)

fig.show()

