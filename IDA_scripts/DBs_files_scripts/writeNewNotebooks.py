import pickle
from os.path import basename
from tqdm import tqdm

with open("./set_t.pickle", "rb") as f:
    set_t_train=pickle.load(f)

list_f_tot_p = "../../../codemerger/scripts/scripts_tmp/merge/seeds.txt"
list_f_tot_t = "../../../codemerger/scripts/scripts_tmp/merge/targets.txt"

def cat(f):
    with open(f, "r") as file:
        # check that
        d = file.readlines()
        d = [e.replace("\n","") for e in d]
    return d

list_other_fun = list()

for l in cat(list_f_tot_p):
    if "/" not in l:
        continue
    binary, fun = l.split("/")[-2], basename(l).split(":")[-1]
    list_other_fun.append((binary, fun))


for l in cat(list_f_tot_t):
    if "/" not in l:
        continue
    binary, fun = l.split("/")[-2], basename(l).split(":")[-1]
    list_other_fun.append((binary, fun))

f1 = open("fun_of_interest.txt.new","w")
f2 = open("selected_pairs.csv.new","w")

# === write the files
# IDBs/Dataset-Muaz/sqlite3.i64,vdbeSortAllocUnpacked,IDBs/Dataset-Muaz/masscan.i64,safe_strcpy
outfun = set()
out = "idb_path_1,func_name_1,idb_path_2,func_name_2\n"
f2.write(out)
for binary, fun in tqdm(set_t_train):
    out = "IDBs/Dataset-Muaz/{}.i64,{},IDBs/Dataset-Muaz/{}.i64,{}\n".format(binary, fun, binary, fun) # t, t
    outfun.add(fun)
    for otherBin, otherFun in list_other_fun:
        out += "IDBs/Dataset-Muaz/{}.i64,{},IDBs/Dataset-Muaz/{}.i64,{}\n".format( binary, fun, otherBin, otherFun) # t, t
        outfun.add(otherFun)

    f2.write(out)

outfunstr = ""
for f in outfun:
    outfunstr += "{}\n".format(f)
    f1.write(outfunstr)


f1.close()
f2.close()
