from urllib.request import Request, urlopen

import json

import pandas as pd

import os
import sys
import platform
import time
import re

def get_top_by_region(df, region, top):
    sub_df = df.loc[df['region'] == region]
    sub_df['rank'] = sub_df.apply(lambda x: int(str(x['rank_display']).split('-')[0]))
    sub_df_top= sub_df.sort_values(by=['rank']).head(top)
    sub_df_top['name_for_searching_gs'] = sub_df_top['title'].apply(lambda x: re.sub(' ', '+', re.sub('^[tT]he ', '' , re.sub(r'\([^\)]+\)', '', x).strip())))
    sub_df_top['org_id'] = '-1'
    return sub_df_top

# Get top universities from www.topuniversities.com
ts = int(time.time())
url = "https://www.topuniversities.com/sites/default/files/qs-rankings-data/914824.txt?_={}".format(ts)

req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
data = json.loads(webpage.decode())
data_df = pd.DataFrame.from_records(data['data'])
data_df['rank_display'] = data_df['rank_display'].str.replace('=','')

top = 100
top_north_america = get_top_by_region(data_df, 'North America', top)
top_europe = get_top_by_region(data_df, 'Europe', top)
top_asia = get_top_by_region(data_df, 'Asia', top)

top_asia.to_csv('top_asia.csv', index=False)
top_europe.to_csv('top_europe.csv', index=False)
top_north_america.to_csv('top_north_america.csv', index=False)
