import pandas as pd

from configuration import ROOT_DIR

from utils.mapping import get_id_orgs, get_name_orgs
from utils.tools import get_path

eurecom_id = get_id_orgs(names=['eurecom'])['eurecom']
auhors_path = get_path([ROOT_DIR, "data", "authors", 'authors_orgID_{}.csv'.format(eurecom_id)])
authors_df = pd.read_csv(auhors_path)
print(authors_df.head(5))