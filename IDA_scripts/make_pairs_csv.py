#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from os.path import isdir

import json

'''
Creates a csv containing all the possible functions pairs given a specific json, coming
for example from create_json.py
@input: path to a json file containing all binaries and their functions ep
@output: a csv file similar to DBs/Dataset-1/pairs/pos_ranking_test.csv
'''

@click.command()
@click.option('-i', '--input-file', required=True,
              help='Input json file')
@click.option('-o', '--output-folder', required=True,
              help='Output csv folder.')
def main(input_file, output_csv):
    print("[D] Json input: {}".format(input_file))
    print("[D] Output : {}".format(output_csv))
    if(not isdir(output_csv)):
        print("[X] Error: output is not a directory")

    file = open(input_file,'r')
    with open(input_file,'r') as file:
        data = json.load(file)

    csv_file = open(output_csv + "/pairs_testing_Dataset-Muaz.csv", "a")
    csv_file.write(',bin_path_1,fva1,bin_path_2,fva2\n')

    for i,bin1 in enumerate(data.keys()):
        for fun1 in data[bin1]:
            for bin2 in data.keys():
                for fun2 in data[bin2]:
                    line = "{},{},{},{},{}\n".format(str(i), str(bin1), hex(fun1), str(bin2), hex(fun2))
                    csv_file.write(line)

    csv_file.close()

    print("# Written results in: {}".format(output_csv))

if __name__ == "__main__":
    main()
