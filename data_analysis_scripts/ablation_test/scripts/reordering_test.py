import argparse
import numpy as np
import copy
import glob
import os
import random as rd
import subprocess

# ==== args

parser = argparse.ArgumentParser()
parser.add_argument("source_code_path", help="Path to the source code file .c")
parser.add_argument("fun_name", help="Name of the function to shuffle inst from .c")
parser.add_argument("opt_level", help="Optimization level for compilation (ex: O0)")
parser.add_argument("shuffle_mode", help="Type of modifications, 'fun', 'bb', 'reg,' 'genreg', 'opt' or 'none'")
parser.add_argument("nb_it", help="Number of iteration for the mean calculus")
parser.add_argument("source", help="Source of the file. Can be 'none', 'sqlite3' or 'curl'. (this affects the compilation folder)")
args = parser.parse_args()

if args.shuffle_mode not in ["fun", "bb","none",'reg', 'genreg', 'opt']:
    print("Error wrong shuffle mode")
    exit(1)
if args.source not in ["none","curl","sqlite3"]:
    print("Error wrong source arg")
    exit(1)
# ==== data reading


# === globals

ASM_FOLDER = "../asm/"
OBF_FOLDER = "../obf_bins/"
GT_FOLDER = "../gt_bins/"
CURL_PATH = "../../../../curl/"
SQ3_PATH = "../../../../sqlite/"
OBF_FOLDER_REALPATH = os.path.realpath(OBF_FOLDER)
GT_FOLDER_REALPATH = os.path.realpath(GT_FOLDER)

JUMP_INST = ["JO","JNO","JS","JNS","JE","JZ","JNE","JNZ","JB","JNAE","JC","JNB","JAE","JNC","JBE","JNA","JA","JNBE","JL","JNGE","JGE","JNL","JLE","JNG","JG","JNLE","JP","JPE","JNP","JPO","JCXZ","JECXZ", "jo","jno","js","jns","je","jz","jne","jnz","jb","jnae","jc","jnb","jae","jnc","jbe","jna","ja","jnbe","jl","jnge","jge","jnl","jle","jng","jg","jnle","jp","jpe","jnp","jpo","jcxz","jecxz","jmp","JMP","ret"]
REG_64 = ["rax", "rcx", "rdx", "rbx","rsp","rbp","rsi", "rdi"]
REG_32 =["eax", "ecx", "edx", "ebx","esp","ebp","esi", "edi"]
REG_16 =["ax", "cx", "dx", "bx","sp","bp","si", "di"]
GENREG_64 = ["rax", "rcx", "rdx", "rbx"]
GENREG_32 =["eax", "ecx", "edx", "ebx"]
GENREG_16 =["ax", "cx", "dx", "bx"]

# ==== functions

def isCondInst(inst):
    for elt in JUMP_INST:
        if elt in inst:
            return True
    return False

def insertFunAsmInBin(data, shuffled_func_asm_code, fun_name):
    # Replace the functions asm instructions in data
    # by the shuffled ones
    for i, inst in enumerate(data):
        if "{}:".format(fun_name) in inst:
            offset = 1
            while ".cfi_startproc"  not in data[i+offset]:
                offset += 1
            offset += 1
            for j,new_int in enumerate(shuffled_func_asm_code):
                data[i+offset+j] = new_int
            assert(".cfi_endproc" in data[i+offset+len(shuffled_func_asm_code)])
            break
    return data

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

def switchInst(inst1, inst2):
    if ":" in inst1 or ":" in inst2:
        return inst1, inst2
    if ".cfi" in inst1 or ".cfi" in inst2:
        return inst1, inst2
    if(isCondInst(inst1) or isCondInst(inst2)):
        return inst1, inst2
    return inst2, inst1

def modifyFunAsmCode(func_insts, modifications):
    '''
    @args: modifications is "bb" or "fun" or "none".
    If modifications == "bb" then shuffle all non jump instructions within basic blocks
    If modifications == "fun" then shuffle all non jump instructions within the function
    If modifications == "reg" then we just rename the registers
    If modifications == "genreg" then we just rename the genral purpos registers registers
    '''
    modified_insts = copy.copy(func_insts)
    # do the shuffle:
    # rule: don't switch the jump order.
    if(modifications in ["none", "opt"]):
        return modified_insts

    if(modifications == "reg"):
        for k, inst in enumerate(func_insts):
            inst2 = copy.copy(inst)
            for reg in REG_64:
                if reg in inst:
                    inst2 = inst2.replace(reg, rd.sample(REG_64, 1)[0])
            for reg in REG_32:
                if reg in inst:
                    inst2 = inst2.replace(reg, rd.sample(REG_32, 1)[0])
            for reg in REG_16:
                if reg in inst:
                    inst2 = inst2.replace(reg, rd.sample(REG_16, 1)[0])
            modified_insts[k] = inst2
        return modified_insts

    if(modifications == "genreg"):
        for k, inst in enumerate(func_insts):
            inst2 = copy.copy(inst)
            for reg in GENREG_64:
                if reg in inst:
                    inst2 = inst2.replace(reg, rd.sample(GENREG_64, 1)[0])
            for reg in GENREG_32:
                if reg in inst:
                    inst2 = inst2.replace(reg, rd.sample(GENREG_32, 1)[0])
            for reg in GENREG_16:
                if reg in inst:
                    inst2 = inst2.replace(reg, rd.sample(GENREG_16, 1)[0])
            modified_insts[k] = inst2
        return modified_insts

    if(modifications == "fun"):
        nb_perm = len(modified_insts)
        for _ in range(nb_perm):
            i = rd.randint(0,len(modified_insts)-1)
            j = rd.randint(0,len(modified_insts)-1)
            modified_insts[i], modified_insts[j] = switchInst(modified_insts[i],  modified_insts[j])
        return modified_insts

    if(modifications == "bb"):
        bb_start = 0
        for k, inst in enumerate(func_insts):
            if isCondInst(inst):
                # we reached the end of a basic block
                nb_perm = k - bb_start
                for _ in range(nb_perm):
                    i = rd.randint(bb_start, k-1)
                    j = rd.randint(bb_start, k-1)
                    modified_insts[i], modified_insts[j] = switchInst(modified_insts[i], modified_insts[j])
                bb_start = k+1
        return modified_insts

# ==== code

def getFunScore(source_code_path, fun_name, opt_level, shuffle_mode, source):
    """
    @args:
        - opt_level should be like: O0
        - shuffle_mode choices: ["bb", "fun", "none","opt"]
    """

    print("---------- Launching main script ------ ")
    bin_name = os.path.basename(source_code_path.split(".")[-2])
    wdir = os.getcwd()

    # clean the working directories
    files = glob.glob(OBF_FOLDER+"*")
    print("Delete {}".format(files))
    for file in files:
        os.remove(file)

    files = glob.glob(ASM_FOLDER+"*")
    print("Delete {}".format(files))
    for file in files:
        os.remove(file)

    files = glob.glob(GT_FOLDER+"*")
    print("Delete {}".format(files))
    for file in files:
        os.remove(file)

    # add ground truth binary
    bin_path = os.path.realpath(os.path.join(GT_FOLDER, bin_name))
    if(source == "curl"):
        # copy source file to curl folder
        cmd = ["cp", source_code_path, os.path.join(CURL_PATH, "src")]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)

        # compile it
        os.chdir(os.path.join(CURL_PATH, "src"))
        print("Moved to {}".format(os.getcwd()))
        cmd = ["gcc", "-fno-inline", "-DHAVE_CONFIG_H", "-I../include", "-I../lib", "-I../src", "-I../lib", "-I../src", "-{}".format(opt_level), "--no-inline", "-Werror-implicit-function-declaration", "-Wno-system-headers", "-MT"]
        cmd.append("{}.o".format(bin_name))
        cmd.append("-MD")
        cmd.append("-MP")
        cmd.append("-MF")
        cmd.append("$depbase.Tpo")
        cmd.append("-c")
        cmd.append("-o")
        cmd.append("{}".format(bin_path))
        cmd.append("{}.c".format(bin_name))
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)
        os.chdir(wdir)
        print("Moved to {}".format(os.getcwd()))

    elif(source == "sqlite3"):
        cmd = ["cp", source_code_path, os.path.join(SQ3_PATH, "src")]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)

        # compile it
        os.chdir(os.path.join(SQ3_PATH, "src"))
        print("Moved to {}".format(os.getcwd()))
        cmd = [ "gcc", "-fno-inline", "-c", "-{}".format(opt_level), "-DSQLITE_OS_UNIX=1", "-I..", "-I../src", "-I../ext/rtree", "-I../ext/icu", "-I../ext/fts3", "-I../ext/async", "-I../ext/session", "-I../ext/userauth", "-D_HAVE_SQLITE_CONFIG_H", "-DBUILD_sqlite", "-DNDEBUG", "-DSQLITE_THREADSAFE=1", "-DSQLITE_ENABLE_MATH_FUNCTIONS", "-DSQLITE_HAVE_ZLIB=1", "-DSQLITE_TEMP_STORE=1", "{}.c".format(bin_name), "-o", "{}".format(bin_path) ]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)
        os.chdir(wdir)
        print("Moved to {}".format(os.getcwd()))
    else:
        cmd = ["gcc", "-fno-inline", "-c", source_code_path, "-{}".format(opt_level), "-o", bin_path]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)

    # generate ASM file
    asm_path = os.path.realpath(os.path.join(ASM_FOLDER, os.path.basename(bin_name)))
    if(shuffle_mode == "opt"):
        opt_level = "O2"
    if(source == "curl"):
        # copy source file to curl folder
        cmd = ["cp", source_code_path, os.path.join(CURL_PATH, "src")]
        os.chdir(os.path.join(CURL_PATH, "src"))
        cmd = ["gcc", "-fno-inline", "-S", "-DHAVE_CONFIG_H", "-I../include", "-I../lib", "-I../src", "-I../lib", "-I../src", "-masm=intel", "-{}".format(opt_level), "--no-inline", "-Werror-implicit-function-declaration", "-Wno-system-headers", "-MT" ,"{}.o".format(bin_name) ,"-MD" ,"-MP" ,"-MF" ,"$depbase.Tpo" ,"-c" ,"-o" ,"{}".format(asm_path) ,"{}.c".format(bin_name)]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)
        os.chdir(wdir)
    elif(source == "sqlite3"):
        # copy source file to curl folder
        cmd = ["cp", source_code_path, os.path.join(SQ3_PATH, "src")]
        os.chdir(os.path.join(SQ3_PATH, "src"))
        cmd = [ "gcc", "-fno-inline", "-S", "-{}".format(opt_level), "-DSQLITE_OS_UNIX=1", "-I..", "-I../src", "-I../ext/rtree", "-I../ext/icu", "-I../ext/fts3", "-I../ext/async", "-I../ext/session", "-I../ext/userauth", "-D_HAVE_SQLITE_CONFIG_H", "-DBUILD_sqlite", "-DNDEBUG", "-DSQLITE_THREADSAFE=1", "-DSQLITE_ENABLE_MATH_FUNCTIONS", "-DSQLITE_HAVE_ZLIB=1", "-DSQLITE_TEMP_STORE=1", "-c", "{}.c".format(bin_name), "-o", "{}".format(asm_path) ]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)
        os.chdir(wdir)
    else:
        cmd = ["gcc", "-fno-inline", "-S", source_code_path, "-o", asm_path, "-masm=intel", "-{}".format(opt_level)]
        print("Running {} ...".format(cmd))
        res = subprocess.check_output(cmd)

    # load asm file
    with open(asm_path,'r') as file:
        data = file.readlines()
    func_asm_code = extractFunAsmCode(data, fun_name)

    # shuffle the instructions
    shuffled_func_asm_code = modifyFunAsmCode(func_asm_code, shuffle_mode)

    # output the new asm file
    new_bin_asm_code = insertFunAsmInBin(data, shuffled_func_asm_code, fun_name)
    ## stupid naming convention from my other stupid scripts
    asm_obf_path = os.path.join(ASM_FOLDER, os.path.basename(bin_name)+"_obf")
    with open(asm_obf_path, "w") as file:
        for line in new_bin_asm_code:
            file.write(line)

    # create a new object file
    bin_obf_path = os.path.join(OBF_FOLDER, os.path.basename(bin_name)+"+"+os.path.basename(source_code_path)+"+"+fun_name)
    cmd = ["gcc", "-x", "assembler", "-c", asm_obf_path, "-o", bin_obf_path]
    print("Running {} ...".format(cmd))
    res = subprocess.check_output(cmd)

    # compute the similarity score
    os.chdir("../../../scripts/")

    cmd = ["./bin_folder_to_scores.sh",
           OBF_FOLDER_REALPATH,
           "a2v",
           GT_FOLDER_REALPATH]
    print("Running {} ...".format(cmd))
    res = subprocess.check_output(cmd)
    print("Res: {} ...".format(res.decode('utf-8')))

    # get the a2v score
    os.chdir(wdir)

    cmd = ["cat", "../../../tmp_results/a2v/pairs_tmp_results.csv"]
    print("Running {} ...".format(cmd))
    res = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    score_line = res.communicate()[0].decode("utf-8")
    score_line = score_line.split("\n")
    score_line = [ elt for elt in score_line if fun_name in elt ] # get the line
    if(len(score_line) > 1):
        print("Error, score output has more than one line of score for {}".format(fun_name))
        exit(1)

    score = float(score_line[0].split(",")[-1])
    print("sim({}, shuffled({})) = {:.2f}".format(os.path.basename(bin_path), os.path.basename(bin_path), score))
    return score, len(func_asm_code)

#==== main

def main():
    x = []
    for i in range(int(args.nb_it)):
        try:
            res = getFunScore(args.source_code_path, args.fun_name, args.opt_level, args.shuffle_mode, args.source)
            x.append(res[0])
        except ValueError as a:
            print("Error running the getFunScore function: {}, continuing anyway".format(a))
            continue
    print("Scores : {}".format(x))
    print("Mean : {} var : {}".format(np.mean(x), np.var(x)))
    print("Function size : {} instructions".format(res[1]))


if __name__ == "__main__":
    main()

