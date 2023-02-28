import argparse
from sklearn.metrics.pairwise import cosine_similarity as cosim
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Compute cosinus similarity on asm2vec embeddings.')
parser.add_argument('--input', '-i',
                    help='input file')
parser.add_argument('--output', '-o',
                    help='output file (don\'t forget the .csv)')

args = parser.parse_args()
header = ','
output_csv=''
sorted_list_embed = []

with open(args.input,"r") as file:
    data = file.readlines()
    for line in data[1:]:
        spline = line.split(",")
        header += spline[0] + "@" + spline[1] + ","
        spline = spline[2].split(";")
        spline[-1] = spline[-1][:-1] # remove the last \n
        sorted_list_embed.append(np.array([val for val in spline]).reshape(1,-1))
    header = header[:-1]

    for i,fun_emb in enumerate(tqdm(sorted_list_embed)):
        tmp_line = header.split(",")[i+1] +","
        for j,fun2_emb in enumerate(sorted_list_embed):
            score = float(cosim(fun_emb, fun2_emb))
            if(i==j):
                tmp_line += "{:2f}".format(0)
            else:
                tmp_line += "{:2f}".format(score)
            tmp_line += ","
        tmp_line = tmp_line[:-1]
        tmp_line += "\n"
        output_csv += tmp_line


    header+="\n"
    output_csv = header + output_csv

with open(args.output,"w") as file:
    file.write(output_csv)
