#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################################################
#                                                                            #
#  Code for the USENIX Security '22 paper:                                   #
#  How Machine Learning Is Solving the Binary Function Similarity Problem.   #
#                                                                            #
#  MIT License                                                               #
#                                                                            #
#  Copyright (c) 2019-2022 Cisco Talos                                       #
#                                                                            #
#  Permission is hereby granted, free of charge, to any person obtaining     #
#  a copy of this software and associated documentation files (the           #
#  "Software"), to deal in the Software without restriction, including       #
#  without limitation the rights to use, copy, modify, merge, publish,       #
#  distribute, sublicense, and/or sell copies of the Software, and to        #
#  permit persons to whom the Software is furnished to do so, subject to     #
#  the following conditions:                                                 #
#                                                                            #
#  The above copyright notice and this permission notice shall be            #
#  included in all copies or substantial portions of the Software.           #
#                                                                            #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,           #
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF        #
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND                     #
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE    #
#  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION    #
#  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION     #
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.           #
#                                                                            #
#  cli_flowchart.py - Call IDA_flowchart.py IDA script.                      #
#                                                                            #
##############################################################################

import click
import subprocess

from os import getcwd
from os import getenv
from os import walk
from os.path import abspath
from os.path import dirname
from os.path import isfile
from os.path import join
from os.path import relpath

IDA_PATH = getenv("IDA_PATH", "/home/gab/idapro-7.5/idat64")
IDA_PLUGIN = join(dirname(abspath(__file__)), 'IDA_flowchart.py')
REPO_PATH = dirname(dirname(dirname(abspath(__file__))))
LOG_PATH = "flowchart_log.txt"

from pathlib import Path

# Load IDBs from selected_pairs
def get_selected_idbs(selected_pairs_file):
    selected_idbs = set()
    with open(selected_pairs_file, 'r') as f:
        for line in f:
            if line.strip() == "":
                continue
            try:
                b1, _, b2, _, *_ = line.replace(",", " ").split()
                selected_idbs.add(Path(b1).as_posix())
                selected_idbs.add(Path(b2).as_posix())
            except ValueError:
                continue
    return selected_idbs


@click.command()
@click.option("-i", "--idbs-folder", required=True,
              help="Path to the IDBs folder")
@click.option("-o", "--output-csv", required=True,
              help="Path to the output CSV file")
@click.option("-s", "--selected-pairs", required=True,
              help="Path to the selected_pairs file")
def main(idbs_folder, output_csv, n_bb_min, selected_pairs):
    """Call IDA_flowchart.py IDA script."""
    try:
        if not isfile(IDA_PATH):
            print("[!] Error: IDA_PATH:{} not valid".format(IDA_PATH))
            print("Use 'export IDA_PATH=/full/path/to/idat64'")
            return

        print("[D] IDBs folder: {}".format(idbs_folder))
        print("[D] Output CSV: {}".format(output_csv))

        selected_idbs = get_selected_idbs(selected_pairs)

        success_cnt, error_cnt = 0, 0
        for root, _, files in walk(idbs_folder):
            for f_name in files:
                if (not f_name.endswith(".i64")) and \
                        (not f_name.endswith(".idb")):
                    continue

                idb_path = join(root, f_name)
                print("\n[D] Processing: {}".format(idb_path))

                if not isfile(idb_path):
                    print("[!] Error: {} not exists".format(idb_path))
                    continue

                # Compute the normalized relative path from the main directory
                rel_idb_path = relpath(
                    join(getcwd(), root, f_name),  # absolute path if IDB
                    REPO_PATH)  # absolute path of the repo folder

                if rel_idb_path not in selected_idbs:
                    print(f"{rel_idb_path} not in selected pairs !")
                    continue

                cmd = [IDA_PATH,
                       '-A',
                       '-L{}'.format(LOG_PATH),
                       '-S{}'.format(IDA_PLUGIN),
                       '-Oflowchart:{}:{}:{}'.format(
                           rel_idb_path,
                           output_csv)
                       idb_path]

                print("[D] cmd: {}".format(cmd))

                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = proc.communicate()

                if proc.returncode == 0:
                    print("[D] {}: success".format(idb_path))
                    success_cnt += 1
                else:
                    print("[!] Error in {} (returncode={})".format(
                        idb_path, proc.returncode))
                    error_cnt += 1

        print("\n# IDBs correctly processed: {}".format(success_cnt))
        print("# IDBs error: {}".format(error_cnt))

    except Exception as e:
        print("[!] Exception in cli_flowchart\n{}".format(e))


if __name__ == '__main__':
    main()
