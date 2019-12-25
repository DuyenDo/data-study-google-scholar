import pandas as pd

import os
import sys

from utils.tools import get_path
from configuration import ROOT_DIR

orgs_path = get_path([ROOT_DIR, "data", "organizations.txt"])

def get_id_orgs(names=[], orgs_path=orgs_path):
    orgs_df = pd.read_csv(orgs_path)

    orgs_df['orgID'] = orgs_df['URL'].apply(lambda url: url.split("&org=")[1].split("&")[0])
    
    orgs_df['Organization'] = orgs_df['Organization'].str.lower()
    orgs_df.loc[:, ['Organization', 'orgID']].drop_duplicates(subset='Organization', inplace=True)
    
    names = map(str.lower, names)
    mapping_df = orgs_df[orgs_df['Organization'].isin(names)]
    
    return mapping_df.set_index('Organization')['orgID'].to_dict()

def get_name_orgs(ids=[], orgs_path=orgs_path):
    orgs_df = pd.read_csv(orgs_path)

    orgs_df['orgID'] = orgs_df['URL'].apply(lambda url: url.split("&org=")[1].split("&")[0])
    
    orgs_df['Organization'] = orgs_df['Organization'].str.lower()
    orgs_df.loc[:, ['Organization', 'orgID']].drop_duplicates(subset='orgID', inplace=True)
    
    mapping_df = orgs_df[orgs_df['orgID'].isin(ids)]
    
    return mapping_df.set_index('orgID')['Organization'].to_dict()
