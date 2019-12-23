import os
import csv
import pickle

def get_path(list_subdir):
    path = list_subdir[0]
    for subdir in list_subdir[1:]:
        path = os.path.join(path, subdir)
    return path

def write_csv(list_dict, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    keys = list_dict[0].keys()
    with open(file_path, 'w', encoding='utf-8', newline='') as cfile:
        dict_writer = csv.DictWriter(cfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_dict)

def write_pickle(list_dict, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as pfile:
        pickle.dump(list_dict, pfile)

def monitor_crawler(monitor_file, text):
    os.makedirs(os.path.dirname(monitor_file), exist_ok=True)
    with open(monitor_file, 'a') as tfile:
        tfile.write(str(text) + '\n')
        tfile.close()