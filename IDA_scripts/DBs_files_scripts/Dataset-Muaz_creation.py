#!/usr/bin/env python
# coding: utf-8

import json
#import csv
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("selected_pairs_path")
parser.add_argument("flowchart_path")
parser.add_argument("output_pairs_testing")
parser.add_argument("output_selected_json")
parser.add_argument("output_testing_csv")
parser.add_argument("--n_bb", "-n", default=5, help="Min nb of bb for a function", type=int)
args = parser.parse_args()


# **Read the flowchart CSV**

flowchart_file = pd.read_csv(args.flowchart_path)
print(flowchart_file.shape)


# **Functions of interest**

file_pairs = open(args.selected_pairs_path, 'r')

selected_columns = ['idb_path', 'fva', 'func_name', 'hashopcodes', 'bb_num']
df = flowchart_file[selected_columns]
df.reset_index(inplace=True)
print("Flowchart selected columns df shape {}".format(df.shape))

flowchart_dict = dict()  # used to make the pairs, fast
flowchart_bb = dict()  # used to make the pairs, fast
for i, row in tqdm(df.iterrows(), total=len(df)):
    flowchart_dict[(row["idb_path"], row["func_name"])] = i
    flowchart_bb[(row["idb_path"], row["func_name"])] = row["bb_num"]
df = df.drop('index', axis=1)

pairs=list()
selected_pairs = pd.read_csv(file_pairs)
print("Selected pairs df shape {}".format(selected_pairs.shape))
skipped_funs = set()
small_funs = set()

for i, row in tqdm(selected_pairs.iterrows(), total=len(selected_pairs)):
    #index_1 = df.loc[ (df['idb_path'] == row["idb_path_1"]) & (df['func_name'] == row["func_name_1"])].index
    #index_2 = df.loc[ (df['idb_path'] == row["idb_path_2"]) & (df['func_name'] == row["func_name_2"])].index
    t1 = (row["idb_path_1"], row["func_name_1"])
    t2 = (row["idb_path_2"], row["func_name_2"])
    if t1 not in flowchart_dict.keys():
        #print(f"{t1} skipped")
        skipped_funs.add(t1)
        continue
    elif t2 not in flowchart_dict.keys():
        #print(f"{t2} skipped")
        skipped_funs.add(t2)
        continue
    index_1 = flowchart_dict[t1]
    index_2 = flowchart_dict[t2]
    if flowchart_bb[t1] < args.n_bb:
        small_funs.add(t1)
        continue
    if flowchart_bb[t2] < args.n_bb:
        small_funs.add(t2)
        continue
    pairs.append((index_1,index_2))

print("Skipped functions pairs from selected_pairs.csv that do not appear in flowchart_dict : {}".format(len(skipped_funs)))
print(f"Skipped {len(small_funs)} functions pairs from selected_pairs.csv that are too small (< {args.n_bb} bb)")

# **Create all pairs of all functions of interest**

comparison_list = list()
i=0
for f1,f2 in tqdm(set(pairs)):
    i+=1
    comparison_list.append(list(df.iloc[f1]) + list(df.iloc[f2]))

# Create a new DataFrame
columns = [x + "_1" for x in selected_columns ] + [x + "_2" for x in selected_columns ]
testing = pd.DataFrame(comparison_list, columns=columns)

# Add the db_type column for compatibility reasons
testing['db_type'] = ['XM'] * testing.shape[0]

# Sort the rows
testing.sort_values(by=['idb_path_1', 'fva_1', 'idb_path_2', 'fva_2'], inplace=True)
testing.reset_index(inplace=True, drop=True)

# Paranoid check
testing.drop_duplicates(inplace=True)
testing.reset_index(inplace=True, drop=True)
print(testing.shape)

# Remove hashopcodes columns
del testing['hashopcodes_1']
del testing['hashopcodes_2']

# Save the DataFrame to file
testing.to_csv(args.output_pairs_testing)

# Save the "selected functions" to a JSON.
# This is useful to limit the IDA analysis to some functions only.

testing_functions = set([tuple(x) for x in testing[['idb_path_1', 'fva_1']].values])
testing_functions |= set([tuple(x) for x in testing[['idb_path_2', 'fva_2']].values])

print("Found {} unique functions".format(len(testing_functions)))

selected_functions = defaultdict(list)
for t in testing_functions:
    selected_functions[t[0]].append(int(t[1], 16))

tot = 0
for k,v in selected_functions.items():
    tot += len(v)

print("Coming from {} unique binaries".format(len(selected_functions.keys())))
print("Total functions in output json: {} ".format(tot))

# Test
assert(sum([len(v) for v in selected_functions.values()]) == len(testing_functions))

# Save to file
with open(args.output_selected_json, "w+") as f_out:
    json.dump(selected_functions, f_out)

# Save the "selected functions" to a CSV.
# This will be useful to post-process the results.

# Remove from flowchart the functions that are not used for the testing
dataset = flowchart_file.copy()
del dataset['bb_list']
del_list = list()
for i, row in dataset.iterrows():
    if not tuple([row['idb_path'], row['fva']]) in testing_functions:
        del_list.append(i)
dataset.drop(del_list, inplace=True)
dataset.reset_index(inplace=True, drop=True)
print(dataset.shape)

# Save to file
dataset.to_csv(args.output_testing_csv)

file_pairs.close()
