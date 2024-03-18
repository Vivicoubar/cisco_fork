#!/usr/bin/env python
# coding: utf-8

import json
import math
import numpy as np
import os
import pandas as pd
from tqdm import tqdm

from IPython.display import display
from collections import defaultdict
from sklearn import metrics, preprocessing

import matplotlib.pyplot as plt


# ### Utility functions

def merge_data(df_pairs, df_similarity, is_pos):
    #df_pair: csv file (my output)
    #df_similarity (ground truth)
    df_pairs = df_pairs.merge(
        df_similarity,
        how='left',
        left_on=['idb_path_1', 'fva_1', 'idb_path_2', 'fva_2'],
        right_on=['idb_path_1', 'fva_1', 'idb_path_2', 'fva_2'])

    if is_pos:
        # If positive pairs, the perfect similarity is 1
        df_pairs['gt'] = [1] * df_pairs.shape[0]
    else:
        # if negative pairs, the perfect similarity is 0
        df_pairs['gt'] = [-1] * df_pairs.shape[0]

    return df_pairs

def plot_sim_and_roc(df_pos, df_neg, test_name, output_dir):
    result_list = list()
    task_list = sorted(set(df_pos['db_type']))

    plt_height = 10
    plt_width = 3
    if len(task_list) == 3:
        plt_height = 3
        plt_width
    if len(task_list) == 4:
        plt_height = 3
        plt_width = 4

    fig_auc, axs = plt.subplots(
        int(len(task_list) / plt_width),
        plt_width,
        figsize=(10, plt_height))
    axs = axs.reshape(-1, 1)

    sim_list = list()
    labels_list = list()

    for i, task in enumerate(task_list):
        df_pos_task = df_pos[df_pos['db_type'] == task]
        df_neg_task = df_neg[df_neg['db_type'] == task]

        sim_list.append(df_pos_task['sim'])
        sim_list.append(df_neg_task['sim'])

        labels_list.append('Pos (task: {})'.format(task))
        labels_list.append('Neg (task: {})'.format(task))

        pred_list = list(df_pos_task['sim'].values)
        pred_list += list(df_neg_task['sim'].values)
        gt_list = list(df_pos_task['gt'].values)
        gt_list += list(df_neg_task['gt'].values)

        # AUC
        roc_auc = metrics.roc_auc_score(gt_list, pred_list)
        result_list.append(["%20s" % (task), "%0.2f" % (roc_auc)])

        # FPR vs. TPR plot
        fpr, tpr, thresholds = metrics.roc_curve(gt_list, pred_list)
        p_axs = axs[i][0].plot(fpr, tpr, linewidth=1.0)
        axs[i][0].set_xlabel('FPR')
        axs[i][0].set_ylabel('TPR')
        axs[i][0].set_xlim([0, 1])
        axs[i][0].set_ylim([0, 1])
        axs[i][0].set_title("AUC = %0.2f - Task: %s" % (roc_auc, task))

    fig_auc.tight_layout()
    # fig_path = os.path.join(output_dir, "{}_roc.png".format(test_name))
    # plt.savefig(fig_path, dpi=300)
    plt.show()

    fig_bplot, axs = plt.subplots(figsize=(10, plt_height))
    bplot = axs.boxplot(
        x=sim_list[::-1],
        labels=labels_list[::-1],
        showfliers=False,
        patch_artist=True,
        vert=False)
    axs.set_title("Similarity distribution for positive and negative pairs")
    for c, patch in enumerate(bplot['boxes']):
        if c % 2:
            patch.set_facecolor('lightblue')
    # fig_path = os.path.join(output_dir, "{}_boxplot.png".format(test_name))
    # plt.savefig(fig_path, dpi=300)
    plt.show()

    return result_list

def compute_auc_and_plot(df_pos, df_neg, results_dir, output_dir):
    results = list()
    for csv_file in sorted(os.listdir(results_dir)):
        # TODO: add filter here for the selected models

        # for every POSITIVE .csv in the "result dir"
        # find the NEGATIVE counterpart
        # read them to DataFrames
        # check there are no NaN values
        if (not csv_file.endswith(".csv")) or \
                ("pos_testing" not in csv_file):
            continue

        print("[D] Processing\n\t{}\n\t{}".format(
            csv_file, csv_file.replace("pos_testing", "neg_testing")))

        test_name = csv_file.replace("pos_testing_", "")
        test_name = test_name.replace(".csv", "")

        df_pos_sim = pd.read_csv(
            os.path.join(results_dir, csv_file))

        df_neg_sim = pd.read_csv(
            os.path.join(results_dir, csv_file.replace(
                "pos_testing", "neg_testing")))

        print("Reading {}\n".format(os.path.join(results_dir, csv_file)))
        print("csv_file Headers: {}\n".format(df_pos_sim.columns))
        print("df_pos headers: {}".format(df_pos.columns))

        assert(df_pos_sim.isna().sum()['sim'] == 0)
        assert(df_neg_sim.isna().sum()['sim'] == 0)

        # Plot the similarity distribution
        df_pos_sim['sim'].hist(bins=200)
        df_neg_sim['sim'].hist(bins=200, alpha=0.8)
        print("Similarity distribution")

        # fig_path = os.path.join(output_dir, "{}_sim.png".format(test_name))
        # plt.savefig(fig_path, dpi=300)
        plt.show()

        # Merge
        df_pos_m = merge_data(df_pos, df_pos_sim, is_pos=True)
        df_neg_m = merge_data(df_neg, df_neg_sim, is_pos=False)
        print("Merged Headers: {}".format(df_pos_m.columns))

        # CALL to PLOT_SIM_AND_ROC
        tmp_list = [['title', test_name]]
        tmp_list.extend(plot_sim_and_roc(
            df_pos_m, df_neg_m, test_name, output_dir))
        results.append(tmp_list)

    return results

def compute_thresholds(df_pos, df_neg, results_dir, output_dir, selected_models):
    results = list()

    for csv_file in sorted(os.listdir(results_dir)):
        if (not csv_file.endswith(".csv")) or \
                ("pos_testing" not in csv_file):
            continue

        is_csv_good = False
        for model in selected_models:
            if model in csv_file:
                print("Finding optimal threshold for {} (found {} in name)".format(csv_file, model))
                is_csv_good = True
                break
        if not is_csv_good:
            continue

        # for every POSITIVE .csv in the "result dir"
        # find the NEGATIVE counterpart
        # read them to DataFrames
        # check there are no NaN values

        print("[D] Processing\n\t{}\n\t{}".format(
            csv_file, csv_file.replace("pos_testing", "neg_testing")))

        test_name = csv_file.replace("pos_testing_", "")
        test_name = test_name.replace(".csv", "")

        df_pos_sim = pd.read_csv(
            os.path.join(results_dir, csv_file))

        df_neg_sim = pd.read_csv(
            os.path.join(results_dir, csv_file.replace(
                "pos_testing", "neg_testing")))

        print("Reading {}\n".format(os.path.join(results_dir, csv_file)))
        print("csv_file Headers: {}\n".format(df_pos_sim.columns))
        print("df_pos headers: {}".format(df_pos.columns))

        assert(df_pos_sim.isna().sum()['sim'] == 0)
        assert(df_neg_sim.isna().sum()['sim'] == 0)

        # Plot the similarity distribution
        df_pos_sim['sim'].hist(bins=200)
        df_neg_sim['sim'].hist(bins=200, alpha=0.8)
        print("Similarity distribution")

        fig_path = os.path.join(output_dir, "{}_sim.png".format(test_name))
        plt.savefig(fig_path, dpi=300)
        plt.show()

        # Merge "testing_Dataset-1.csv" with the results .csv
        df_pos_m = merge_data(df_pos, df_pos_sim, is_pos=True)
        df_neg_m = merge_data(df_neg, df_neg_sim, is_pos=False)
        print("Merged Headers: {}".format(df_pos_m.columns))

        # CALL to PLOT_SIM_AND_ROC
        tmp_list = [['title', test_name]]
        tmp_list.extend(get_model_perfomance_point(
            df_pos_m, df_neg_m, test_name, output_dir))
        results.append(tmp_list)

    return results

def get_model_perfomance_point(df_pos, df_neg, test_name, output_dir):
    result_list = list()
    task_list = sorted(set(df_pos['db_type']))

    plt_height = 10
    if len(task_list) == 3:
        plt_height = 3
    if len(task_list) == 4:
        plt_height = 3

    sim_list = list()
    labels_list = list()

    for i, task in enumerate(task_list):

        df_pos_task = df_pos[df_pos['db_type'] == task]
        df_neg_task = df_neg[df_neg['db_type'] == task]

        sim_list.append(df_pos_task['sim'])
        sim_list.append(df_neg_task['sim'])

        labels_list.append('Pos (task: {})'.format(task))
        labels_list.append('Neg (task: {})'.format(task))

        pred_list = list(df_pos_task['sim'].values)
        pred_list += list(df_neg_task['sim'].values)
        gt_list = list(df_pos_task['gt'].values)
        gt_list += list(df_neg_task['gt'].values)

        # AUC
        roc_auc = metrics.roc_auc_score(gt_list, pred_list)

        # Best f1 score and associated threshold
        precision, recall, thresholds = metrics.precision_recall_curve(gt_list, pred_list)
        f1_scores = 2*recall*precision/(recall+precision)
        opt_f1 = np.max(f1_scores)
        opt_thr = thresholds[np.argmax(f1_scores)]

        result_list.append(["%20s" % (task), "%0.2f" % (roc_auc), "%0.2f" % (opt_f1), "%0.2f" % (opt_thr)])

    fig_bplot, axs = plt.subplots(figsize=(10, plt_height))
    bplot = axs.boxplot(
        x=sim_list[::-1],
        labels=labels_list[::-1],
        showfliers=False,
        patch_artist=True,
        vert=False)
    axs.set_title("Similarity distribution for positive and negative pairs")
    for c, patch in enumerate(bplot['boxes']):
        if c % 2:
            patch.set_facecolor('lightblue')
    fig_path = os.path.join(output_dir, "{}_boxplot.png".format(test_name))
    plt.savefig(fig_path, dpi=300)

    return result_list

def from_list_to_df(auc_list):
    pd_temp_dict = defaultdict(list)
    pd_temp_dict_f1 = defaultdict(list)
    pd_temp_dict_thr = defaultdict(list)
    for xr in auc_list:
        columns_set = set()
        columns = list()
        values_auc = list()
        values_f1 = list()
        values_thr = list()
        columns.append(xr[0][0].strip())
        values_auc.append(xr[0][1].strip())
        values_f1.append(xr[0][1].strip())
        values_thr.append(xr[0][1].strip())
        for x in xr[1:]:
            columns.append(x[0].strip())
            values_auc.append(x[1].strip())
            values_f1.append(x[2].strip())
            values_thr.append(x[3].strip())

        for c, v in zip(columns, values_auc):
            columns_set.add(c)
            pd_temp_dict[c].append(v)
        for c, v in zip(columns, values_f1):
            pd_temp_dict_f1[c].append(v)
        for c, v in zip(columns, values_thr):
            pd_temp_dict_thr[c].append(v)

    df_auc = pd.DataFrame.from_dict(pd_temp_dict)
    df_auc = df_auc.rename(columns={"title":"model_name"})
    df_auc['model_name'] = df_auc['model_name'].apply(lambda x: x.replace("Dataset-1_", ""))
    df_auc['model_name'] = df_auc['model_name'].apply(lambda x: x.replace("Dataset-2-CodeCMR_", ""))
    df_auc['model_name'] = df_auc['model_name'].apply(lambda x: x.replace("Dataset-2_", ""))

    df_opt_f1 = pd.DataFrame.from_dict(pd_temp_dict_f1)
    df_opt_f1 = df_opt_f1.rename(columns={"title":"model_name"})
    df_opt_f1['model_name'] = df_opt_f1['model_name'].apply(lambda x: x.replace("Dataset-1_", ""))
    df_opt_f1['model_name'] = df_opt_f1['model_name'].apply(lambda x: x.replace("Dataset-2-CodeCMR_", ""))
    df_opt_f1['model_name'] = df_opt_f1['model_name'].apply(lambda x: x.replace("Dataset-2_", ""))

    df_opt_thr = pd.DataFrame.from_dict(pd_temp_dict_thr)
    df_opt_thr = df_opt_thr.rename(columns={"title":"model_name"})
    df_opt_thr['model_name'] = df_opt_thr['model_name'].apply(lambda x: x.replace("Dataset-1_", ""))
    df_opt_thr['model_name'] = df_opt_thr['model_name'].apply(lambda x: x.replace("Dataset-2-CodeCMR_", ""))
    df_opt_thr['model_name'] = df_opt_thr['model_name'].apply(lambda x: x.replace("Dataset-2_", ""))

    return df_auc, df_opt_f1, df_opt_thr

# Create output folders
os.system('mkdir -p metrics_and_plots/Dataset-1')
os.system('mkdir -p metrics_and_plots/Dataset-1-CodeCMR')
os.system('mkdir -p metrics_and_plots/Dataset-2')

### Dataset 1 (for threshold computing)

MODELS_LIST = [ "asm2vec_e10", "GGSNN_OPC-200_e10", "GMN_OPC-200_e16", "SAFE_ASM-list_250_e5", "Trex", "Zeek" ]
RESULTS_DIR = "../data/Dataset-1/"
OUTPUT_DIR = "metrics_and_plots/Dataset-1-thresholds/"

base_path = "../../DBs/Dataset-1/pairs/testing/"

df_pos_testing = pd.read_csv(
    os.path.join(base_path, "pos_testing_Dataset-1.csv"))

df_neg_testing = pd.read_csv(
    os.path.join(base_path, "neg_testing_Dataset-1.csv"))

auc_list = compute_thresholds(df_pos_testing, df_neg_testing, RESULTS_DIR, OUTPUT_DIR, MODELS_LIST)
df_auc, df_f1, df_thr = from_list_to_df(auc_list)
df_auc.to_csv(os.path.join(OUTPUT_DIR, "df_auc.csv"))
df_f1.to_csv(os.path.join(OUTPUT_DIR, "df_f1.csv"))
df_thr.to_csv(os.path.join(OUTPUT_DIR, "df_thr.csv"))
print("Dataframes saved in {}".format(OUTPUT_DIR))

### Dataset 2

#RESULTS_DIR = "../data/Dataset-2/"
#OUTPUT_DIR = "metrics_and_plots/Dataset-2/"
#
#base_path = "../../DBs/Dataset-2/pairs/"
#
#df_pos_testing = pd.read_csv(
#    os.path.join(base_path, "pos_testing_Dataset-2.csv"))
#
#df_neg_testing = pd.read_csv(
#    os.path.join(base_path, "neg_testing_Dataset-2.csv"))
#
#auc_list = compute_auc_and_plot(df_pos_testing, df_neg_testing, RESULTS_DIR, OUTPUT_DIR)
#df_auc = from_list_to_df(auc_list)
#display(df_auc)
#df_auc.to_csv(os.path.join(OUTPUT_DIR, "df_auc.csv"))
#
