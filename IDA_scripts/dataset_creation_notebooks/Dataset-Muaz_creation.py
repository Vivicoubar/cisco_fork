#!/usr/bin/env python
# coding: utf-8

import json
import csv
import pandas as pd
import itertools

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("fun_of_interest_path")
parser.add_argument("selected_pairs_path")
args = parser.parse_args()

from tqdm import tqdm

# **Read the flowchart CSV**

flowchart = pd.read_csv("~/cisco_fork/DBs/Dataset-Muaz/features/flowchart_Dataset-Muaz.csv")
print(flowchart.shape)

flowchart.loc[flowchart['func_name'] == 'getMatrixElements']

# **Functions of interest**

#fun_of_interest = list(flowchart['func_name'])
file = open(args.fun_of_interest_path,'r')
file_pairs = open(args.selected_pairs_path,'r')

fun_of_interest = []
for line in file.readlines():
    if line.split('\n')[0] in fun_of_interest:
        continue
    fun_of_interest.append(line.split('\n')[0])
file.close()
print(fun_of_interest)
selected_columns = ['idb_path', 'fva', 'func_name', 'hashopcodes']

df0 = flowchart[selected_columns]
df = df0.loc[df0['func_name'].isin(fun_of_interest)]

print(df)
# Store the new function pairs
df.reset_index(inplace=True)

import csv

datareader = csv.reader(file_pairs)
next(datareader) # skip header
pairs=list()
for row in datareader:
    index_1 = df.loc[ (df['idb_path'] == row[0]) & (df['func_name'] == row[1])].index
    index_2 = df.loc[ (df['idb_path'] == row[2]) & (df['func_name'] == row[3])].index
    if len(index_1) == 0 or len(index_2) == 0:
        continue
    pairs.append((index_1[0],index_2[0]))
    print(pairs[-1])

#pairs = list(itertools.combinations_with_replacement(df.index,2)) # this is bad

df = df.drop('index', axis=1)

# **Create all pairs of all functions of interest**

comparison_list = list()
print("Nb of fun: {}".format(len(df)))

# Iterate over each unique pair of function in the list
i=0
for f1,f2 in tqdm(set(pairs)):
    i+=1
    comparison_list.append(list(df.iloc[f1]) + list(df.iloc[f2]))

# Create a new DataFrame
columns = [x + "_1" for x in selected_columns ] + [x + "_2" for x in selected_columns ]
testing = pd.DataFrame(comparison_list, columns=columns)

# Add the db_type column 
testing['db_type'] = ['XM'] * testing.shape[0]

# Sort the rows
testing.sort_values(by=['idb_path_1', 'fva_1', 'idb_path_2', 'fva_2'], inplace=True)
testing.reset_index(inplace=True, drop=True)

# Check that the hashopcodes of the functions to compare are different
for i, row in testing.iterrows():
    if row['hashopcodes_1'] == row['hashopcodes_2']:
        continue

# Paranoid check
testing.drop_duplicates(inplace=True)
testing.reset_index(inplace=True, drop=True)
print(testing.shape)


# Remove hashopcodes columns
del testing['hashopcodes_1']
del testing['hashopcodes_2']

# Save the DataFrame to file
testing.to_csv("~/cisco_fork/DBs/Dataset-Muaz/pairs/pairs_testing_Dataset-Muaz.csv")

# Save the "selected functions" to a JSON.
# This is useful to limit the IDA analysis to some functions only.

testing_functions = set([tuple(x) for x in testing[['idb_path_1', 'fva_1']].values])
testing_functions |= set([tuple(x) for x in testing[['idb_path_2', 'fva_2']].values])
print("Found {} unique functions".format(len(testing_functions)))

from collections import defaultdict
selected_functions = defaultdict(list)
for t in testing_functions:
    selected_functions[t[0]].append(int(t[1], 16))

# Test
assert(sum([len(v) for v in selected_functions.values()]) == len(testing_functions))

# Save to file
with open("/home/gabriel/cisco_fork/DBs/Dataset-Muaz/features/selected_Dataset-Muaz.json", "w+") as f_out:

    json.dump(selected_functions, f_out)

# Save the "selected functions" to a CSV.
# This will be useful to post-process the results.

# Remove from flowchart the functions that are not used for the testing
dataset = flowchart.copy()
del dataset['bb_list']
del_list = list()
for i, row in dataset.iterrows():
    if not tuple([row['idb_path'], row['fva']]) in testing_functions:
        del_list.append(i)
dataset.drop(del_list, inplace=True)
dataset.reset_index(inplace=True, drop=True)
print(dataset.shape)

# Save to file
dataset.to_csv("~/cisco_fork/DBs/Dataset-Muaz/testing_Dataset-Muaz.csv")


file.close()
file_pairs.close()
