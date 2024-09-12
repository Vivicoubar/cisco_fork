import pandas as pd
from tqdm import tqdm
from os.path import basename

dfAdv = pd.read_csv("./pairs/testing_Dataset-adv.csv")
dfAdvTrain = pd.read_csv("./pairs/training_Dataset-adv.csv")
dfM = pd.read_csv("./pairs/pairs_testing_Dataset-Muaz.csv")

advSet = set()
for i, row in dfAdv.iterrows():
    advSet.add((basename(row["idb_path"]).replace("-O2","-2").replace("-O1","-2"), row["func_name"]))

trainSet = set()
for i, row in dfAdvTrain.iterrows():
    trainSet.add((basename(row["idb_path"]).replace("-O2","-2").replace("-O1","-2"), row["func_name"]))

good_index = list()
unique_adv = set()
for i, row in tqdm(dfM.iterrows(), total=len(dfM)):
    bin1, bin2 = basename(row["idb_path_1"]), basename(row["idb_path_2"])
    fun1, fun2 = row["func_name_1"], row["func_name_2"]
    if "+" in bin1 and "+" not in bin2:
        if (bin1, fun1) in trainSet:
            unique_adv.add(row["idb_path_1"])
            good_index.append(i)
    elif "+" in bin2 and "+" not in bin1:
        if (bin2, fun2) in trainSet:
            unique_adv.add(row["idb_path_2"])
            good_index.append(i)
    elif "+" in bin2 and "+" in bin1:
        if (bin1, fun1) in trainSet:
            if (bin2, fun2) in trainSet:
                unique_adv.add(row["idb_path_2"])
                unique_adv.add(row["idb_path_1"])
                good_index.append(i)
    else:
        good_index.append(i)

dfNew = dfM.loc[good_index]
dfNew.to_csv("./pairs/pairs_testing_Dataset-Muaz.csv.new")
print(len(unique_adv))
