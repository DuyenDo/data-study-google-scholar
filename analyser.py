import glob
import pandas as pd

data_folder = "data/papers_eurecom/"

count = len(glob.glob1(data_folder,"*.csv"))
print("Number of eurecom's authors in google scholar: ", count)

f = pd.read_csv(data_folder + "papers-of-authorID-_b6dDHMAAAAJ.csv")
print(f.head)