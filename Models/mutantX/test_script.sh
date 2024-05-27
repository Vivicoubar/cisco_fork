# This script writes a .csv containing the scores of selected pairs of functions

DATASET_KEY="Muaz"
# Input:
DB_PATH=$HOME/cisco_fork/DBs/Dataset-${DATASET_KEY}/
OUTPUT=$(pwd)/bytes/ # where the bytes.json are saved
OUTPUT_SCORES=$(pwd)/pairs_results_Dataset-Muaz_mut.csv # where the bytes.json are saved

CWD=$(pwd)
PAIR_LIST=$DB_PATH/pairs/pairs_testing_Dataset-${DATASET_KEY}.csv
TESTING_PATH=$DB_PATH/testing_Dataset-${DATASET_KEY}.csv
ACFG_PATH=$DB_PATH/features/acfg_disasm/

#== cleaning

rm "$OUTPUT"/*
rm "$OUTPUT_SCORES"
rm "MUTANTX2"

#== main script

job(){
	#echo "Making bytes .json from $1"
	# output -> saves the .json files containing data on the binary code bytes in bytes/binary.json
	if ! python3 MakeBytesJsonFromACFG.py $1 $2 $3; then
		echo "Failed !"
		exit 1
	fi
}

echo "Making bytes json from acfg files..."
cd scripts
for acfg_file in $(find $ACFG_PATH -type f); do
	job "$acfg_file" "$TESTING_PATH" "$OUTPUT" &
	pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done
echo "Done"

cd $CWD
echo "Running MutantX to create MUTANTX2 file embeddings..."
if ! python3 MutantXS.py; then
	echo "Error running MutantX"
	exit 1
fi
#results saved in MUTANTX2
echo "Done"
# MUTANTX2 is a dict: { (bin1+file1.c+fun1+bin2+file2.c+bin2, fun1) : [0.,1.,3,4,...,6] } (the vector is the fun1 embedding)
# Note: could also be { (curl, funi) : [0.,1.,3,4,...,6] }

cd scripts
echo "Computing scores for pairs..."
if ! python3 ComputeScoreFromCsv.py "$PAIR_LIST" "$OUTPUT_SCORES" ; then # for each line in testing_Dataset-Muaz.csv, computes the score using the embeddings in MUTANTX2
	echo "Error"
	exit 1
fi
echo "Done"
# output -> a csv file containing the score (cosine similarity) (like the cisco output !)
cd $CWD

cp pairs_results_Dataset-Muaz_mut.csv $HOME/codemerger/scripts/benchmark/results/
echo "Pairs results was copied in $HOME/codemerger/data/inst_insertion_test/results/pairs_results_Dataset-Muaz_mut.csv"

# copy the csv line to ~/codemerger/data/inst_insertion_test/results/pairs_results_Dataset-Muaz_mut.csv
