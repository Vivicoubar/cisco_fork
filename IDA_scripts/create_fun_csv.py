#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import angr

from os import walk
from os.path import isfile
from os.path import join, abspath

count = 0

'''
Extract automatically ALL the functions from the binaries in the folder
and fills a csv with all their data (similar to DBs/Dataset-1/testing_Dataset-1.csv
@input: path to a FOLDER containing all the binaries
@output: the csv file
'''

def get_bin_fun_data(bin_path):
    global count
    output_str = ""
    path = abspath(bin_path)
    try:
#        breakpoint()
        proj = angr.Project(bin_path, load_options={'auto_load_libs':False})
        # CFG
        cfg = proj.analyses.CFGFast()
        # function stuff
        fun_manager = cfg.kb.functions
        for fva in list(fun_manager.function_addrs_set):
            if(has more than 5 basic blocks):
                count += 1
                c_func = fun_manager.function(fva)
                bin_path =
                func_name =
                start_ea =
                bb_num =
                hash_opcode = 
                project = 
                library =
                arch = 
                bit =
                compiler =
                optimization =

                
            
        return output_str
    except Exception as e:
        print("[!] Exception in analyzing the functions\n{}".format(e))
        return output_str

@click.command()
@click.option('-i', '--input-folder', required=True,
              help='Input folder containing the binaries')
@click.option('-o', '--output-csv', required=True,
              help='Output csv file.')
def main(input_folder, output_csv):
    global count
    csv_file_str = ",idb_path,fva,func_name,start_ea,end_ea,bb_num,hashopcodes,project,library,arch,bit,compiler,version,optimizations"
    csv_file_str += "\n"
    try:

        print("[D] Binaries folder: {}".format(input_folder))
        print("[D] Output csv: {}".format(output_csv))

        success_cnt, error_cnt = 0, 0
        exit_success = False
        for root, _, files in walk(input_folder):
            for f_name in files:

                bin_path = join(root, f_name)
                print("\n[D] Processing: {}".format(bin_path))

                if not isfile(bin_path):
                    print("[!] Error: {} not exists".format(bin_path))
                    continue

                bin_fun_str = get_bin_fun_data(bin_path)
                csv_file_str += bin_fun_str

                if(exit_success):
                    success_cnt += 1
                else:
                    error_cnt += 1

        print("\n# Binaries correctly processed: {}".format(success_cnt))
        print("# Binaries error: {}".format(error_cnt))

        with open(output_csv, "a") as jfile:
            jfile.write(csv_file_str)

        print("# Written results in: {}".format(output_csv))
    except Exception as e:
        print("[!] Exception:\n{}".format(e))

if __name__ == "__main__":
    main()
