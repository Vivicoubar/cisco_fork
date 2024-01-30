from capstone import Cs, CS_ARCH_X86, CS_MODE_64
import pandas as pd
from os.path import basename
import argparse
import json
import base64

parser = argparse.ArgumentParser()
parser.add_argument("input_acfg", help="Path to the .json file containing a binary acfg disasm data")
parser.add_argument("fun_info_file", help="Path to the .csv file that links functions names to their entry point (testing_Dataset-Muaz.csv")
parser.add_argument("output_folder", help="Ouput folder to save bytes .json data to")
args = parser.parse_args()

# Init capstone engine
md = Cs(CS_ARCH_X86, CS_MODE_64) # Initialize X86 engine
md.detail = True # Turn on detail mode

def getFunName(csv_file, bin_name, fun_ea):
    df = pd.read_csv(csv_file)
    line = ((df['fva'] == fun_ea) &
             (df["idb_path"] == bin_name))

    if line.any():
        return df.loc[line]["func_name"].values[0]
    else:
        print("Could not find {}:{:x} in {}".format(bin_name, fun_ea, csv_file))
        return ""

#Return a list where each item is the bytes of 1 instruction
def getInstBytesFromBB(bb_name, data):

    ret_list = list()

    #We get the base64 string, representing all bytes in the basic block
    bb_bytes_b64 = data[bb_name]["b64_bytes"]

    #Decode base64 to hex
    bb_bytes = base64.b64decode(bb_bytes_b64)

    #Separate the bytes per instruction
    for c_inst in md.disasm(bb_bytes, 0X0):
        inst_bytes = ""
        for b in c_inst.bytes:
            inst_bytes = inst_bytes + (format(b,"2x").replace(" ","0"))

        ret_list.append(inst_bytes)

    return ret_list

# === Main script

## Load the acfg file
with open(args.input_acfg,'r') as file:
    d = json.load(file)

#first_key = "IDBs/Dataset-Muaz/" + args[1].replace("_acfg_disasm.json",".i64")

for key in d.keys():
    all_bbs_bytes = list()
    #For each basic block, we get the bytes of each instruction

    for fun_ea in [k for k in d[key].keys() if k != "arch"]:
        # all keys are function entry points, except "arch"
        fun_name = getFunName(args.fun_info_file, key, fun_ea)
        if len(fun_name) == 0:
            continue

        for bb_name in d[key][fun_ea]["basic_blocks"]:
            all_bbs_bytes.extend(getInstBytesFromBB(bb_name, d[key][fun_ea]["basic_blocks"]))

        #Creation of the output JSON file
        d_out = {"name": args.input_acfg, "md5": "placeholder", "architecture": dict(), "ida_compiler": "GNU C++", "bytes": all_bbs_bytes}
        d_out["architecture"] = {"type": "metapc", "size": "b64", "endian": "be"}

        out_path = "{}/{}+{}".format(args.output_folder, basename(args.input_acfg.replace("_acfg_disasm.json", "")), fun_name)
        with open(out_path, "w") as file:
            json.dump(d_out, file)

## gather:
### - the full bytes of the function d[premier_elt_du_dict]
### - the function name -> dans le nom du fichier input 'input.split("+")[2]
### - the asm instructions of the function, IN A CERTAIN SEQUENCE -> séquence par défaut pour l'instant

# for each basic block
## for each instruction in the basic block:
### get bytes of the instruction using keystone
## check that the full bytes == concatenated bytes of the instructions

## save the new json in the correct folder
