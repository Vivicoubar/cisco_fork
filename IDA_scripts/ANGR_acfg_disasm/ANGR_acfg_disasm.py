import base64
import angr
import click
import sys
import json
import ntpath
import os
import time

from capstone import *
from collections import namedtuple

BasicBlock = namedtuple('BasicBlock', ['va', 'size', 'succs'])

def convert_procname_to_str(procname, bitness):
    """Convert the arch and bitness to a std. format."""
    if procname == 'mipsb':
        return "mips-{}".format(bitness)
    if procname == "arm":
        return "arm-{}".format(bitness)
    if "pc" in procname or procname in ["amd64","x64","x86"]:
        return "x86-{}".format(bitness)
    raise RuntimeError(
        "[!] Arch not supported ({}, {})".format(
            procname, bitness))

def initialize_capstone(procname, bitness):
    """
    Initialize the Capstone disassembler.

    Original code from Willi Ballenthin (Apache License 2.0):
    https://github.com/williballenthin/python-idb/blob/
    2de7df8356ee2d2a96a795343e59848c1b4cb45b/idb/idapython.py#L874
    """
    md = None
    prefix = "UNK_"

    # WARNING: mipsl mode not supported here
    if procname == 'mipsb':
        prefix = "M_"
        if bitness == 32:
            md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_BIG_ENDIAN)
        if bitness == 64:
            md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 | CS_MODE_BIG_ENDIAN)

    if procname == "arm":
        prefix = "A_"
        if bitness == 32:
            # WARNING: THUMB mode not supported here
            md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
        if bitness == 64:
            md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

    if "pc" in procname or procname in ["amd64","x64","x86"]:
        prefix = "X_"
        if bitness == 32:
            md = Cs(CS_ARCH_X86, CS_MODE_32)
        if bitness == 64:
            md = Cs(CS_ARCH_X86, CS_MODE_64)

    if md is None:
        raise RuntimeError(
            "Capstone initialization failure ({}, {})".format(
                procname, bitness))

    # Set detail to True to get the operand detailed info
    md.detail = True
    return md, prefix


def capstone_disassembly(md, bb):
    """Return the BB (normalized) disassembly, with mnemonics and BB heads."""
    try:
        bb_heads, bb_mnems, bb_disasm, bb_norm = list(), list(), list(), list()

        # Iterate over each instruction in the BB
        for i_inst in md.disasm(bb.bytes, bb.addr):
            # Get the address
            bb_heads.append(i_inst.address)
            # Get the mnemonic
            bb_mnems.append(i_inst.mnemonic)
            # Get the disasm
            bb_disasm.append("{} {}".format(
                i_inst.mnemonic,
                i_inst.op_str))

            # Compute the normalized code. Ignore the prefix.
            # cinst = prefix + i_inst.mnemonic
            cinst = i_inst.mnemonic

            # Iterate over the operands
            for op in i_inst.operands:

                # Type register
                if (op.type == 1):
                    cinst = cinst + " " + i_inst.reg_name(op.reg)

                # Type immediate
                elif (op.type == 2):
                    imm = int(op.imm)
                    if (-int(5000) <= imm <= int(5000)):
                        cinst += " " + str(hex(op.imm))
                    else:
                        cinst += " " + str('HIMM')

                # Type memory
                elif (op.type == 3):
                    # If the base register is zero, convert to "MEM"
                    if (op.mem.base == 0):
                        cinst += " " + str("[MEM]")
                    else:
                        # Scale not available, e.g. for ARM
                        if not hasattr(op.mem, 'scale'):
                            cinst += " " + "[{}+{}]".format(
                                str(i_inst.reg_name(op.mem.base)),
                                str(op.mem.disp))
                        else:
                            cinst += " " + "[{}*{}+{}]".format(
                                str(i_inst.reg_name(op.mem.base)),
                                str(op.mem.scale),
                                str(op.mem.disp))

                if (len(i_inst.operands) > 1):
                    cinst += ","

            # Make output looks better
            cinst = cinst.replace("*1+", "+")
            cinst = cinst.replace("+-", "-")

            if "," in cinst:
                cinst = cinst[:-1]
            cinst = cinst.replace(" ", "_").lower()
            bb_norm.append(str(cinst))

        return bb_heads, bb_mnems, bb_disasm, bb_norm

    except Exception as e:
        print("[!] Capstone exception", e)
        return list(), list(), list(), list()

def get_bb_disasm(md, bb):
    """Return the (nomalized) disassembly for a BasicBlock."""
    b64_bytes = base64.b64encode(bb.bytes)
    bb_heads, bb_mnems, bb_disasm, bb_norm = \
        capstone_disassembly(md, bb)
    return b64_bytes, bb_heads, bb_mnems, bb_disasm, bb_norm


@click.command()
@click.option("-i", "--bin-path", required=True,
              help="Path to the input binaries folder")
@click.option("-o", "--output-csv", required=True,
              help="Path to the output CSV file")
@click.option('-j', '--json-path', required=True,
              help='JSON file with selected functions.')
@click.option("-l", "--log-path", required=True,
              help="Path to the log file")
def run_acfg_disasm(bin_path, output_csv, json_path, log_path):
    """Disassemble each function. Extract the CFG. Save output to JSON."""
    with open(json_path) as f_in:
        selected_functions = json.load(f_in)
    fva_list = selected_functions[bin_path]
    # gather all the entry addresses

    print("[D] Found %d addresses" % len(fva_list))

    print("[D] Processing: %s" % bin_path)

    # Create output directory if it does not exist
    if not os.path.isdir(output_csv):
        os.mkdir(output_csv)

    output_dict = dict()
    output_dict[bin_path] = dict()
 
    # ANGR project
    ANGR_proj = angr.Project(os.path.abspath(bin_path), load_options={'auto_load_libs':False})
    # build the CFG
    cfg = ANGR_proj.analyses.CFGFast()
    # function stuff
    fun_manager = cfg.kb.functions
    bin_fva_list = list(fun_manager.function_addrs_set)

    procname = ANGR_proj.arch.name.lower()
    bitness = ANGR_proj.arch.bits
    output_dict[bin_path]['arch'] = convert_procname_to_str(procname, bitness)

    md, prefix = initialize_capstone(procname, bitness)
    # Iterate over each function
    for fva in fva_list:
        try:
            current_fun = fun_manager.function(fva)
            start_time = time.time()
            nodes_set, edges_set = set(), set()
            bbs_dict = dict()
            for bb_addr in current_fun.block_addrs_set:
                bb = current_fun.get_block(bb_addr)
            #for bb in get_basic_blocks(fva):
                # CFG
                nodes_set.add(bb.addr)
                for succ_node in cfg.get_any_node(bb_addr).successors:
                    edges_set.add((bb_addr, succ_node.addr))
                # BB-level features
                if bb.size:
                    b64_bytes, bb_heads, bb_mnems, bb_disasm, bb_norm = \
                        get_bb_disasm(md,bb)
                    bbs_dict[bb.addr] = {
                        'bb_len': bb.size,
                        'b64_bytes': b64_bytes.decode(),
                        'bb_heads': bb_heads,
                        'bb_mnems': bb_mnems,
                        'bb_disasm': bb_disasm,
                        'bb_norm': bb_norm
                    }
                else:
                    bbs_dict[bb.addr] = {
                        'bb_len': bb.size,
                        'b64_bytes': "",
                        'bb_heads': list(),
                        'bb_mnems': list(),
                        'bb_disasm': list(),
                        'bb_norm': list()
                    }
            elapsed_time = time.time() - start_time
            func_dict = {
                'nodes': list(nodes_set),
                'edges': list(edges_set),
                'elapsed_time': elapsed_time,
                'basic_blocks': bbs_dict
            }
            output_dict[bin_path][hex(fva)] = func_dict

        except Exception as e:
            print("[!] Exception: skipping function fva: %d" % fva)
            print(e)

    out_name = ntpath.basename(bin_path) + "_acfg_disasm"
    print("Saving data in file {}".format(os.path.join(output_csv, out_name)))
    with open(os.path.join(output_csv, out_name), "w") as f_out:
        json.dump(output_dict, f_out)


if __name__ == '__main__':
    '''
   input: bin_path, lis tof selected functions, output dir 
   output: none. writes info about the functions in the output dir though
   --> see the line json.dump
    '''
    run_acfg_disasm()
    sys.exit(0)
