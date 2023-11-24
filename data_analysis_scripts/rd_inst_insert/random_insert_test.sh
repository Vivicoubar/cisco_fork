# WARNING: run this script after properly filling the folders:
# "./acgf"
# "./misc"
# "../dumb_pairs_dataset"
# "../compiled_obfuscated_binaries"
# ... with codemerger/scripts/bin_folder_to_score.sh and codemerger/scripts/dumb_dataset_creation.sh
CWD=$(pwd)
COMP_OBF_BIN="../compiled_obfuscated_bins"
MERGED_SOURCES="../dumb_pairs_dataset"
NB_F1="notebook_files/fun_of_interest.txt"
NB_F2="notebook_files/selected_pairs.csv"
RES_DIR="results"
mkdir -p $RES_DIR

CISCO_BINS="../../../cisco_fork/Binaries/Dataset-Muaz/bins/"
CISCO_IDBS="../../../cisco_fork/IDBs/Dataset-Muaz/"
CISCO_DBS="../../../cisco_fork/DBs/Dataset-Muaz/"
CISCO_SCRIPTS="../../../cisco_fork/IDA_scripts/"

FUN_FEATURES_SCRIPTS="../../scripts/data_analysis"

# Prep
echo "" > $NB_F1
echo "idb_path_1,func_name_1,idb_path_2,func_name_2" > $NB_F2

rm -r $CISCO_DBS/*
# ground truth bins
cp ../binaries/curl ../binaries/sqlite3 $CISCO_BINS
cp $COMP_OBF_BIN/* $CISCO_BINS


# ----------- Main loop

for bin in $(find $COMP_OBF_BIN -type f); do
	P=$(echo $(basename $bin) | cut -d "+" -f 1)
	SFILE_NAME=$(echo $bin | cut -d "+" -f 2)
	SFUN_NAME=$(echo $bin | cut -d "+" -f 3)
	T=$(echo $bin | cut -d "+" -f 4)
	TFILE_NAME=$(echo $bin | cut -d "+" -f 5)
	TFUN_NAME=$(echo $bin | cut -d "+" -f 6)
	NEW_NAME=$P+${SFUN_NAME}+${TFUN_NAME}
	BIN3=$(echo ${NEW_NAME}-2)

	# ----------- Notebook files (what to compare and print for asm2vec)
	# I'll also need all the necessary names in the fun_of_interest and selected_pairs file
	echo $SFUN_NAME >> $NB_F1
	echo $TFUN_NAME >> $NB_F1

	echo "IDBs/Dataset-Muaz/$P.i64,$SFUN_NAME,IDBs/Dataset-Muaz/$T.i64,$TFUN_NAME" >> $NB_F2
	echo "IDBs/Dataset-Muaz/$NEW_NAME.i64,$SFUN_NAME,IDBs/Dataset-Muaz/$T.i64,$TFUN_NAME" >> $NB_F2
	echo "IDBs/Dataset-Muaz/$P.i64,$SFUN_NAME,IDBs/Dataset-Muaz/$NEW_NAME.i64,$SFUN_NAME" >> $NB_F2

	# New bin we're gonna create after random insertions (p'')
	echo "IDBs/Dataset-Muaz/$P.i64,$SFUN_NAME,IDBs/Dataset-Muaz/$P.i64,$SFUN_NAME" >> $NB_F2
	echo "IDBs/Dataset-Muaz/$BIN3.i64,$SFUN_NAME,IDBs/Dataset-Muaz/$T.i64,$TFUN_NAME" >> $NB_F2
	echo "IDBs/Dataset-Muaz/$P.i64,$SFUN_NAME,IDBs/Dataset-Muaz/$BIN3.i64,$SFUN_NAME" >> $NB_F2

	cp $NB_F1 $CISCO_SCRIPTS/dataset_creation_notebooks/
	cp $NB_F2 $CISCO_SCRIPTS/dataset_creation_notebooks/

	# ------------ Binaries: curl (t), sqlite3 (p), p', p''
	# I'll need bins to run a2v on them
	# I already copied p, t and p' in the cisco folers
	# I need to add p'' (bin3)

	# compute instructions to insert set: this doesn't need the asm
	cd $FUN_FEATURES_SCRIPTS
	python3 compare_functions_features.py $CWD/acfg/${NEW_NAME}_acfg_disasm.json $SFUN_NAME $CWD/acfg/${T}_acfg_disasm.json $TFUN_NAME -c $CWD/misc/testing_Dataset-Muaz.csv -o $CWD/misc/${BIN3}_inst_dict -r 1

	cd $CWD

	# insert instructions

	python3 create_payload_after_random_insert.py $MERGED_SOURCES/$(basename $bin.c) $SFUN_NAME "O0" $CWD/misc/${BIN3}_inst_dict bins/$BIN3

done
exit 0
cp bins/* $CISCO_BINS

# ----------- Compute the IDBs and DBs files

# preprocess the new binaries
cd $CISCO_SCRIPTS
python3 generate_idbs.py --muaz
./generate_acfg_feature_from_idbs.sh

# run the model on test data
cd ../../cisco_fork/Models/Asm2vec/
./test_script.sh

# copy the results in $CWD/results
cd $CWD
rm $RES_DIR/*
cp ../../cisco_fork/Results/data/Dataset-Muaz/pairs_testing_Dataset-Muaz_asm2vec_e10.csv $RES_DIR/pairs_tmp_results.csv
echo "Copied processed embeddings to $(realpath $RES_DIR)/pairs_tmp_results.csv"
#python3 get_scores.py -r a2v/pairs_tmp_results.csv -s a2v/selected_pairs.csv
