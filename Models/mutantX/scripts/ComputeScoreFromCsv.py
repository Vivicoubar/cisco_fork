import argparse
import pickle
import pandas as pd
from tqdm import tqdm
from scipy.spatial.distance import cosine

parser = argparse.ArgumentParser()
parser.add_argument("pairs_list", help="Path to the .csv file containing the interesting pairs (pairs_testing_Dataset-Muaz.csv)")
parser.add_argument("out_path", help="Path to output file")
args = parser.parse_args()

# -- some vars

MutX_embeddings = "../MUTANTX2"
with open(MutX_embeddings,'rb') as file:
    mut_dict = pickle.load(file)

# -- Functions

def clean_bin_name(bin_name):
    out = bin_name.replace('IDBs/Dataset-Muaz/',"")
    out = out.replace('IDBs/Dataset-2/',"")
    out = out.replace('_byte.json',"")
    out = out.replace('.i64',"")
    return out

def cosine_similarity(e1, e2):
    return 1 - cosine(e1, e2)

# for each pair in pairs_testing_Dataset-Muaz.csv, computes the score using the embeddings in MUTANTX2

df = pd.read_csv(args.pairs_list)
new_df = pd.DataFrame(columns=["idb_path_1","func_name_1","idb_path_2","func_name_2","sim"])

for ind,row in tqdm(df.iterrows(), desc="Computing pair scores..."):
    # get p and t: those are going to be the keys for the embeddings in the mutantx2 pickled ouptut
    p = (clean_bin_name(row["idb_path_1"]), row["func_name_1"])
    t = (clean_bin_name(row["idb_path_2"]), row["func_name_2"])

    if p not in mut_dict.keys():
        print("{} not in mut_dict, skipping it".format(p))
        continue
    if t not in mut_dict.keys():
        print("{} not in mut_dict, skipping it".format(t))
        continue

    emb1 = mut_dict[p] # this is np darray of shape (4096,) (?)
    emb2 = mut_dict[t]
    sim = cosine_similarity(emb1,emb2)

    new_row = dict()
    new_row["idb_path_1"] = p[0]
    new_row["idb_path_2"] = t[0]
    new_row["func_name_1"] = p[1]
    new_row["func_name_2"] = t[1]
    new_row["sim"] = sim

    #new_df = new_df.append(new_row, ignore_index=True)
    new_df.loc[len(new_df)] = new_row

print("*** Success : {} / {} pairs were found".format(len(new_df),len(df)))
# --- save the results
new_df.to_csv(args.out_path, index=False)
