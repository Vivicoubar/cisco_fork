#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import json
import subprocess
import time

from os import getenv
from os.path import abspath, realpath
from os.path import dirname
from os.path import isfile
from os.path import join

ANGR_SCRIPT = join(dirname(abspath(__file__)), 'ANGR_acfg_disasm.py')
#REPO_PATH = dirname(dirname(dirname(abspath(__file__))))
REPO_PATH = dirname(realpath(__file__))
LOG_PATH = "acfg_disasm_log.txt"

'''
Gather all info about given functions (values in the json file) inside given
binaries (keys in the json file)
'''

@click.command()
@click.option('-j', '--json-path', required=True,
              help='JSON file with selected functions.')
@click.option('-o', '--output-dir', required=True,
              help='Output directory.')
def main(json_path, output_dir):
    """Call ANGR_acfg_disasm.py script."""
    try:
        print("[D] JSON path: {}".format(json_path))
        print("[D] Output directory: {}".format(output_dir))

        # input note: the json is a dict with
        # key : idb (bin for us) path
        # value : list of functions entry points

        if not isfile(json_path):
            print("[!] Error: {} does not exist".format(json_path))
            return

        with open(json_path) as f_in:
            jj = json.load(f_in)

            success_cnt, error_cnt = 0, 0
            start_time = time.time()
            for bin_key_path in jj.keys():
                bin_path =abspath(bin_key_path)
                print("\n[D] Processing (json key): {}".format(bin_key_path))

                # Convert the relative path into a full path
                print("[D] Bin abs path: {}".format(bin_path))
                if not isfile(bin_path):
                    print("[!] Error: {} does not exist".format(bin_path))
                    continue

                cmd = ["python3",
                       ANGR_SCRIPT,
                       '-i{}'.format(bin_key_path),
                       '-o{}'.format(output_dir),
                       '-j{}'.format(json_path),
                       '-l{}'.format(LOG_PATH),
                       ]

                print("[D] cmd: {}".format(cmd))

                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = proc.communicate()
                if proc.returncode == 0:
                    print("[D] {}: success".format(bin_path))
                    success_cnt += 1
                else:
                    print("[!] Error in {} (returncode={})".format(
                        bin_path, proc.returncode))
                    print(stderr.decode('UTF-8'))
                    error_cnt += 1

            end_time = time.time()
            print("[D] Elapsed time: {}".format(end_time - start_time))
            with open(LOG_PATH, "a+") as f_out:
                f_out.write("elapsed_time: {}\n".format(end_time - start_time))

            print("\n# IDBs correctly processed: {}".format(success_cnt))
            print("# Error: {}".format(error_cnt))

    except Exception as e:
        print("[!] Exception in cli_acfg_disasm\n{}".format(e))


if __name__ == '__main__':
    main()
