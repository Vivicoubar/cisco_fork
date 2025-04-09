model="$1"
LOG=$(realpath "$2")
OUT_DIR=$(realpath "$3")

CISCO_MODELS=$(realpath "Models/")
CISCO_RESULTS=$(realpath "Results/")
mkdir -p $CISCO_RESULTS/csv/
rm -r $CISCO_RESULTS/csv/*
mkdir -p $OUT_DIR
CWD=$(pwd)

if [ "$model" != "a2v" -a "$model" != "gmn"  -a "$model" != "all" ]; then
	echo "error, "$model" model not recognized"
	notif error "$0" "getModelScores.sh: model not recognized"
	exit 1
fi

if [ "$model" = "gmn" ]; then
	cd $CISCO_MODELS/GGSNN-GMN/
	echo "Running gmn test_script in $(pwd)" >> $LOG
	if ! ./test_script.sh gmn_opc; then
		cd -
		echo "Error running test script, no Dataset testing results created"
		echo "Error running test script, no Dataset testing results created" >> $LOG
		exit 1
	fi
	if ! cp $CISCO_RESULTS/csv/pairs_results_Dataset-Muaz_gmn_opc.csv $OUT_DIR/; then
		cd -
		echo "error copying result csv"
		echo "error copying result csv" >> $LOG
		exit 1
	fi

elif [ "$model" = "a2v" ]; then
	cd $CISCO_MODELS/Asm2vec/
	echo "Running asm2vec test_script in $(pwd)" >> $LOG
	if ! ./test_script.sh; then
		echo "Error running test script, no Dataset testing results created"
		echo "Error running test script, no Dataset testing results created" >> $LOG
		exit 1
	fi
	if ! cp $CISCO_RESULTS/csv/pairs_results_Dataset-Muaz_a2v.csv $OUT_DIR/; then
		echo "error copying result csv"
		echo "error copying result csv" >> $LOG
		exit 1
	fi

elif [ $model = "all" ]; then

	cd $CISCO_MODELS/SAFE/
	echo "Running SAFE test_script in $(pwd)" >> $LOG
	if ! ./test_script.sh; then
		echo "Error running test script, no Dataset testing results created"
		echo "Error running test script, no Dataset testing results created" >> $LOG
		notif error "$0 $*" finished
		exit 1
	fi
	echo "Done" >> $LOG

	cd $CISCO_MODELS/Asm2vec/
	echo "Running asm2vec test_script in $(pwd)" >> $LOG
	if ! ./test_script.sh; then
		echo "Error running test script, no Dataset testing results created"
		echo "Error running test script, no Dataset testing results created" >> $LOG
		notif error "$0 $*" finished
		exit 1
	fi
	echo "Done" >> $LOG

	cd $CISCO_MODELS/GGSNN-GMN/
	echo "Running gnn_opc test_script in $(pwd)" >> $LOG
	if ! ./test_script.sh gnn_opc; then
		echo "Error running test script, no Dataset testing results created"
		echo "Error running test script, no Dataset testing results created" >> $LOG
		notif error "$0 $*" finished
		exit 1
	fi
	echo "Done" >> $LOG

	echo "Running gmn test_script in $(pwd)" >> $LOG
	if ! ./test_script.sh gmn_opc; then
		echo "Error running test script, no Dataset testing results created"
		echo "Error running test script, no Dataset testing results created" >> $LOG
		notif error "$0 $*" finished
		exit 1
	fi
	echo "Done" >> $LOG

	cd $CISCO_MODELS/Zeek/
	echo "Running gnn test_script in $(pwd)" >> $LOG
	if ! ./test_script.sh; then
		echo "Error running test script, no Dataset testing results created"
		echo "Error running test script, no Dataset testing results created" >> $LOG
		notif error "$0 $*" finished
		exit 1
	fi
	echo "Done" >> $LOG

	cd $CWD

	# copy the resulting csvs
	if ! cp $CISCO_RESULTS/csv/pairs_results_Dataset-Muaz_*.csv $OUT_DIR/; then
		echo "error copying result csvs"
		echo "error copying result csvs" >> $LOG
		exit 1
	fi
fi

echo "Done"
echo "Done" >> $LOG
