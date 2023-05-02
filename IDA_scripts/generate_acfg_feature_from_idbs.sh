#!/bin/bash

# setup
# put all your IDA-extracted (with /IDA_scripts/generate_idbs.py) databases in /IDBs/Dataset-Muaz/
# create a Dbs/Dataset-Muaz folder
# create features and pairs folders
mkdir ../DBs/Dataset-Muaz
mkdir ../DBs/Dataset-Muaz/features
mkdir ../DBs/Dataset-Muaz/pairs

# flowchart (to select functions with at least 5 blocks)
## input: IDBs fodler
## output: csv file with selected functions data
python3 IDA_flowchart/cli_flowchart.py -i ../IDBs/Dataset-Muaz -o ../DBs/Dataset-Muaz/features/flowchart_Dataset-Muaz.csv

# select pairs and functions
## input: flowchart csv file
## output: testing_dataset.csv, features/selected_Dataset-Muaz.json, pairs/pairs_testing_Dataset-Muaz.csv
jupyter nbconvert --execute --to notebook dataset_creation_notebooks/Dataset-Muaz_creation.ipynb

# compute acfg features
## input: selected_Dataset-Muaz.json
## output: features/acfg_disasm/acfg_disasm.json files
python3 IDA_acfg_disasm/cli_acfg_disasm.py -j ../DBs/Dataset-Muaz/features/selected_Dataset-Muaz.json -o ../DBs/Dataset-Muaz/features/acfg_disasm
