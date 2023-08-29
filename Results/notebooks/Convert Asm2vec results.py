#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
#  Convert Asm2vec results                                                   #
#                                                                            #
##############################################################################


# In[12]:

import numpy as np
import os
import pandas as pd

from scipy.spatial.distance import cosine
from tqdm import tqdm


# In[13]:


def cosine_similarity(e1, e2):
    return 1 - cosine(e1, e2)


# In[4]:


def compute_cosine_similarity(df_input):
    sim_list = list()
    for idx, row in tqdm(df_input.iterrows()):

        if row['embeddings_1'] is np.nan or \
                row['embeddings_2'] is np.nan:
            print("[!] Missing value in (idx:{})".format(idx))
            sim_list.append(0)
            continue

        e1 = np.array([float(x) for x in row['embeddings_1'].split(";")])
        e2 = np.array([float(x) for x in row['embeddings_2'].split(";")])
        sim_list.append(cosine_similarity(e1, e2))
    return sim_list


# In[5]:


def compute_embedding_similarity(df_pairs, df_asm2vec):
    
    df_asm2vec = df_asm2vec[['idb_path', 'fva', 'embeddings']]
    
    df_pairs = df_pairs.merge(df_asm2vec,
                              how='left',
                              left_on=['idb_path_1', 'fva_1'],
                              right_on=['idb_path', 'fva'])
    df_pairs.rename(columns={'embeddings': 'embeddings_1'}, inplace=True)
    
    df_pairs = df_pairs.merge(df_asm2vec,
                              how='left',
                              left_on=['idb_path_2', 'fva_2'],
                              right_on=['idb_path', 'fva'])
    df_pairs.rename(columns={'embeddings': 'embeddings_2'}, inplace=True)

    df_pairs['sim'] = compute_cosine_similarity(df_pairs)
    df_pairs = df_pairs[['idb_path_1','fva_1','idb_path_2','fva_2','sim']]
    return df_pairs


# ### Process Dataset-1 results

# In[6]:


DB1_PATH = "../../DBs/Dataset-1/pairs/testing/"

for folder in [
    'Dataset-1_asm2vec_e10',
    'Dataset-1_pvdbow_e10',
        'Dataset-1_pvdm_e10']:

    embedding_path = os.path.join(
        "../data/raw_results/Asm2vec/", folder, "embeddings.csv")
    print("[D] Processing {}".format(embedding_path))
    if not os.path.isfile(embedding_path):
        print("[!] File not found: {}".format(embedding_path))
        continue

    df_emb = pd.read_csv(embedding_path)

    df_pos = pd.read_csv(os.path.join(DB1_PATH, "pos_testing_Dataset-1.csv"), index_col=0)
    df_neg = pd.read_csv(os.path.join(DB1_PATH, "neg_testing_Dataset-1.csv"), index_col=0)
    df_pos_rank = pd.read_csv(os.path.join(DB1_PATH, "pos_rank_testing_Dataset-1.csv"), index_col=0)
    df_neg_rank = pd.read_csv(os.path.join(DB1_PATH, "neg_rank_testing_Dataset-1.csv"), index_col=0)
    
    df_pos = compute_embedding_similarity(df_pos, df_emb)
    df_neg = compute_embedding_similarity(df_neg, df_emb)
    df_pos_rank = compute_embedding_similarity(df_pos_rank, df_emb)
    df_neg_rank = compute_embedding_similarity(df_neg_rank, df_emb)

    df_pos.to_csv("../data/Dataset-1/pos_testing_{}.csv".format(folder), index=False)
    df_neg.to_csv("../data/Dataset-1/neg_testing_{}.csv".format(folder), index=False)
    df_pos_rank.to_csv("../data/Dataset-1/pos_rank_testing_{}.csv".format(folder), index=False)
    df_neg_rank.to_csv("../data/Dataset-1/neg_rank_testing_{}.csv".format(folder), index=False)


# ### Process Dataset-2 results

# In[7]:


DB2_PATH = "../../DBs/Dataset-2/pairs/"

for folder in [
    'Dataset-2_asm2vec_e10',
    'Dataset-2_pvdbow_e10',
        'Dataset-2_pvdm_e10']:

    embedding_path = os.path.join(
        "../data/raw_results/Asm2vec/", folder, "embeddings.csv")
    print("[D] Processing {}".format(embedding_path))
    if not os.path.isfile(embedding_path):
        print("[!] File not found: {}".format(embedding_path))
        continue

    df_emb = pd.read_csv(embedding_path)

    df_pos = pd.read_csv(os.path.join(DB2_PATH, "pos_testing_Dataset-2.csv"), index_col=0)
    df_neg = pd.read_csv(os.path.join(DB2_PATH, "neg_testing_Dataset-2.csv"), index_col=0)
    df_pos_rank = pd.read_csv(os.path.join(DB2_PATH, "pos_rank_testing_Dataset-2.csv"), index_col=0)
    df_neg_rank = pd.read_csv(os.path.join(DB2_PATH, "neg_rank_testing_Dataset-2.csv"), index_col=0)
    
    df_pos = compute_embedding_similarity(df_pos, df_emb)
    df_neg = compute_embedding_similarity(df_neg, df_emb)
    df_pos_rank = compute_embedding_similarity(df_pos_rank, df_emb)
    df_neg_rank = compute_embedding_similarity(df_neg_rank, df_emb)

    df_pos.to_csv("../data/Dataset-2/pos_testing_{}.csv".format(folder), index=False)
    df_neg.to_csv("../data/Dataset-2/neg_testing_{}.csv".format(folder), index=False)
    df_pos_rank.to_csv("../data/Dataset-2/pos_rank_testing_{}.csv".format(folder), index=False)
    df_neg_rank.to_csv("../data/Dataset-2/neg_rank_testing_{}.csv".format(folder), index=False)


# ### Process Dataset-Vulnerability results

# In[8]:


DB2_PATH = "../../DBs/Dataset-Vulnerability/pairs/"

for folder in [
    'Dataset-Vulnerability_asm2vec_e10',
    'Dataset-Vulnerability_pvdbow_e10',
    'Dataset-Vulnerability_pvdm_e10']:

    embedding_path = os.path.join(
        "../data/raw_results/Asm2vec/", folder, "embeddings.csv")
    print("[D] Processing {}".format(embedding_path))
    if not os.path.isfile(embedding_path):
        print("[!] File not found: {}".format(embedding_path))
        continue

    df_emb = pd.read_csv(embedding_path)

    df_testing = pd.read_csv(os.path.join(DB2_PATH, "pairs_testing_Dataset-Vulnerability.csv"), index_col=0)
    
    df_testing = compute_embedding_similarity(df_testing, df_emb)

    df_testing.to_csv("../data/Dataset-Vulnerability/testing_{}.csv".format(folder), index=False)

