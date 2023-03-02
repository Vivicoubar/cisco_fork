#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import angr

from os import walk
from os.path import isfile
from os.path import join, abspath
import json

'''
Extract automatically ALL the functions from the binaries in the folder
and outputs a json file with allt heir entry points.
The json file is designed to be fed to the ANGR plugins.
@input: path to a FOLDER containing all the binaries
@output: a json file with key: path to a binary / value: list of its functions ep
'''

def add_bin_fun_to_dict(bin_path, out_dict):
    path = abspath(bin_path)
    try:
#        breakpoint()
        proj = angr.Project(bin_path, load_options={'auto_load_libs':False})
        # CFG
        cfg = proj.analyses.CFGFast()
        # function stuff
        fun_manager = cfg.kb.functions
        if(len(fun_manager.function_addrs_set)):
            out_dict[path] = list()
        for fva in list(fun_manager.function_addrs_set):
            out_dict[path].append(fva)
        return True
    except Exception as e:
        print("[!] Exception in analyzing the functions\n{}".format(e))
        return False

@click.command()
@click.option('-i', '--input-folder', required=True,
              help='Input folder containing the binaries')
@click.option('-o', '--output-json', required=True,
              help='Output json file.')
def main(input_folder, output_json):
    out_dict = dict()
    try:

        print("[D] Binaries folder: {}".format(input_folder))
        print("[D] Output json: {}".format(output_json))

        success_cnt, error_cnt = 0, 0
        exit_success = False
        for root, _, files in walk(input_folder):
            for f_name in files:

                bin_path = join(root, f_name)
                print("\n[D] Processing: {}".format(bin_path))

                if not isfile(bin_path):
                    print("[!] Error: {} not exists".format(bin_path))
                    continue

                exit_success = add_bin_fun_to_dict(bin_path, out_dict)
                if(exit_success):
                    success_cnt += 1
                else:
                    error_cnt += 1

        print("\n# Binaries correctly processed: {}".format(success_cnt))
        print("# Binaries error: {}".format(error_cnt))

        with open(output_json, "a") as jfile:
            json.dump(out_dict, jfile)

        print("# Written results in: {}".format(output_json))
    except Exception as e:
        print("[!] Exception:\n{}".format(e))

if __name__ == "__main__":
    main()
