#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import angr
from os.path import isdir, join, isfile, abspath
from os import walk

'''
Creates a csv containing all the possible functions pairs given a folder of binaries
This uses Angr to get the functions data
@input: path to a folder containing the binaries
@output: a csv file similar to DBs/Dataset-1/pairs/pos_ranking_test.csv
'''

def add_bin_fun_to_csv(bin_path, fun_dict):
    # fun_dict["foo"] = [bin_name, fun_addr, fun_name]
    path = abspath(bin_path)
    try:
#        breakpoint()
        proj = angr.Project(path, load_options={'auto_load_libs':False})
        # CFG
        cfg = proj.analyses.CFGFast()
        # function stuff
        fun_manager = cfg.kb.functions

        for fva in list(fun_manager.function_addrs_set):
            unique_id = bin_path + str(fva)
            current_fun = fun_manager.function(fva)
            fun_dict[unique_id] = [bin_path, fva, current_fun.name]

        return True
    except Exception as e:
        print("[!] Exception in analyzing the functions\n{}".format(e))
        return False


@click.command()
@click.option('-i', '--input-folder', required=True,
              help='Input json file')
@click.option('-o', '--output-folder', required=True,
              help='Output csv folder.')
def main(input_folder, output_folder):
    i = 0

    fun_data_dict={}
    # this dict contain all the functions data
    # key: fun unique identifier bin/path_fva1
    # values : [bin_path, fva_1, func_name]

    print("[D] Input folder: {}".format(input_folder))
    print("[D] Output : {}".format(output_folder))
    if(not isdir(output_folder) or not isdir(input_folder)):
        print("[X] Error: input or output is not a directory")
        return

    #output
    csv_file_path = join(output_folder, "pairs_testing_Dataset-Muaz.csv")
    print("[D] Output file : {}".format(csv_file_path))
    csv_file = open(csv_file_path,  "a")
    csv_file.write(',idb_path_1,fva_1,func_name_1,idb_path_2,fva_2,func_name_2,db_type\n')

    success_cnt, error_cnt = 0, 0
    exit_success = False
    for root, _, files in walk(input_folder):
        for f_name in files:

            bin_path = join(root, f_name)
            print("\n[D] Processing: {}".format(bin_path))

            if not isfile(bin_path):
                print("[!] Error: {} not exists".format(bin_path))
                continue

            exit_success = add_bin_fun_to_csv(bin_path, fun_data_dict)
            if(exit_success):
                success_cnt += 1
            else:
                error_cnt += 1

    print("\n# Binaries correctly processed: {}".format(success_cnt))
    print("# Binaries error: {}".format(error_cnt))

    for fun1 in fun_data_dict.values():
        for fun2 in fun_data_dict.values():
            line = "{},{},{},{},{},{},{},{}\n".format(str(i), fun1[0],hex(fun1[1]), fun1[2], fun2[0], hex(fun2[1]), fun2[2], "XO")
            csv_file.write(line)
            i += 1

    csv_file.close()

    print("# Written results in: {}".format(csv_file_path))

if __name__ == "__main__":
    main()
