import argparse
import numpy as np
import copy
import glob
import os
import random as rd
import subprocess

# ==== paths

ASM_FOLDER = "asm/"
CURL_PATH = "../../../curl/"
SQ3_PATH = "../../../sqlite3/"
# ==== args

parser = argparse.ArgumentParser()
parser.add_argument("source_code_path", help="Path to the source code file .c")
parser.add_argument("fun_name", help="Name of the function to shuffle inst into")
parser.add_argument("opt_level", help="Optimization level for compilation (ex: O0)")
parser.add_argument("inst_set", help="Path to the instruction set to insert file")
parser.add_argument("out_path", help="Path to output file")
args = parser.parse_args()

# ==== funcs
def extractFunAsmCode(data, fun_name):
    # Isolate the function asm instructions
    # rule: function starts at "cfi_startproc:\n" and end at "cfi_endproc"
    func_insts = list()
    in_func = False
    current_func_name = ""
    for inst in data:
        if "{}:".format(fun_name) in inst:
            current_func_name = fun_name
        if "cfi_startproc" in inst and current_func_name == fun_name:
            in_func = True
            continue
        if "cfi_endproc" in inst and current_func_name == fun_name:
            break
        if in_func:
            func_insts.append(inst)
    return func_insts

def modifyFunAsmCode(func_insts, inst_set_dict):
    modified_insts = copy.copy(func_insts)

    for inst, nb in inst_set_dict.items():
        # pick a random line number
        for i in range(int(nb)):
            line_nb = rd.randint(5,len(modified_insts)-5)
            # TODO: here modify the line if it contians "imm" or "ref" (size mismatch ?)
            inst = inst.replace("imm","0x100")
            modified_insts.insert(line_nb, inst)
    return modified_insts

def insertFunAsmInBin(data, shuffled_func_asm_code, fun_name):
    # Replace the functions asm instructions in data
    # by the shuffled ones
    current_func_name = ""
    slice1 = [] # before func
    slice2 = [] # during func
    slice3 = [] # after func
    b = 1
    for i, inst in enumerate(data):
        if "{}:".format(fun_name) in inst:
            current_func_name = fun_name
        if "cfi_startproc" in inst and current_func_name == fun_name:
            b = 2
            slice1.append(inst)
            continue
        if "cfi_endproc" in inst and current_func_name == fun_name:
            b = 3
            current_func_name = ""

        match b:
            case 1:
                slice1.append(inst)
            case 2:
                slice2.append(inst)
            case 3:
                slice3.append(inst)

    return slice1 + shuffled_func_asm_code + slice3

# ==== main func

def createBin(source_code_path, fun_name, opt_level, inst_set_dict, out_path):
    source = "sqlite3"

    print("---------- Launching main script ------ ")
    # name is from dumb pair dataset
    print(source_code_path)
    c_source_name = os.path.basename(source_code_path.split("+")[1])
    wdir = os.getcwd()

    # generate ASM file
    asm_path = os.path.realpath(os.path.join(ASM_FOLDER, os.path.basename(source_code_path[:-1]+"s")))
    if(source == "curl"):
        # copy source file to curl folder
        cmd = ["cp", source_code_path, os.path.join(CURL_PATH, "src")]
        os.chdir(os.path.join(CURL_PATH, "src"))
        cmd = ["gcc","-masm=intel", "-fno-inline", "-S", "-DHAVE_CONFIG_H", "-I../include", "-I../lib", "-I../src", "-I../lib", "-I../src", "-masm=intel", "-{}".format(opt_level), "--no-inline", "-Werror-implicit-function-declaration", "-Wno-system-headers", "-MT" ,"{}.o".format(c_source_name) ,"-MD" ,"-MP" ,"-MF" ,"$depbase.Tpo" ,"-c" ,"-o" ,"{}".format(asm_path) ,"{}.c".format(c_source_name)]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)
        os.chdir(wdir)

    elif(source == "sqlite3"):
        # copy source file to curl folder
        cmd = ["cp", source_code_path, os.path.join(SQ3_PATH, "src")]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)

        os.chdir(os.path.join(SQ3_PATH, "src"))

        cmd = ["git", "restore", "."]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)

        cmd = [ "gcc", "-masm=intel", "-fno-inline", "-S", "-{}".format(opt_level), "-DSQLITE_OS_UNIX=1", "-I..", "-I../src", "-I../ext/rtree", "-I../ext/icu", "-I../ext/fts3", "-I../ext/async", "-I../ext/session", "-I../ext/userauth", "-D_HAVE_SQLITE_CONFIG_H", "-DBUILD_sqlite", "-DNDEBUG", "-DSQLITE_THREADSAFE=1", "-DSQLITE_ENABLE_MATH_FUNCTIONS", "-DSQLITE_HAVE_ZLIB=1", "-DSQLITE_TEMP_STORE=1", "-c", "{}".format(c_source_name), "-o", "{}".format(asm_path) ]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)
        os.chdir(wdir)

    else:
        cmd = ["gcc","-masm=intel", "-fno-inline", "-S", source_code_path, "-o", asm_path, "-masm=intel", "-{}".format(opt_level)]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)

    # load asm file
    with open(asm_path,'r') as file:
        data = file.readlines()
    func_asm_code = extractFunAsmCode(data, fun_name)

    # shuffle the instructions
    shuffled_func_asm_code = modifyFunAsmCode(func_asm_code, inst_set_dict)

    # output the new asm file
    new_bin_asm_code = insertFunAsmInBin(data, shuffled_func_asm_code, fun_name)

    ## stupid naming convention from my other stupid scripts
    asm_obf_path = os.path.join(ASM_FOLDER, os.path.basename(source_code_path)[:-2]+"-2.s")
    with open(asm_obf_path, "w") as file:
        for line in new_bin_asm_code:
            file.write(str(line))

    # create a new object file
    cmd = ["gcc", "-x", "assembler", "-c", asm_obf_path, "-o", out_path]
    print("Running {} ...".format(cmd))
    res = subprocess.check_output(cmd)
    print("Created bin at {}".format(out_path))

    return 0

# ==== main

try:
    inst_dict = dict()
    with open(args.inst_set,"r") as f:
        for l in f.readlines():
            if len(l.split(";")) > 1:
                inst_dict[l.split(";")[1]] = int(l.split(";")[0])

    res = createBin(args.source_code_path, args.fun_name, args.opt_level, inst_dict, args.out_path)
except ValueError as a:
    print("Error running the createBin function: {}, continuing anyway".format(a))
