# $1 : gnn or gmn

set -e

docker run --rm \
       -v $(pwd)/../../DBs/Dataset-Muaz/features/acfg_disasm:/input \
       -v $(pwd)/Preprocessing/Dataset-1_training:/training_data \
       -v $(pwd)/Preprocessing/Dataset-Muaz:/output \
       -it gnn-preprocessing /code/gnn_preprocessing.py -i /input -d /training_data/opcodes_dict.json -o /output

echo " ------------------------ Done preprocessing"

if [ "$1" = "gnn" ]; then
docker run --rm \
	-v $(pwd)/../../DBs:/input \
	-v $(pwd)/NeuralNetwork/:/output \
	-v $(pwd)/Preprocessing:/preprocessing \
	-it gnn-neuralnetwork /code/gnn.py --test \
		--model_type embedding --training_mode pair \
		--features_type opc --dataset muaz \
		-c /output/model_checkpoint_2023-05-16 \
		-o /output/Dataset-Muaz

elif [ "$1" = "gmn" ]; then
docker run --rm \
	-v $(pwd)/../../DBs:/input \
	-v $(pwd)/NeuralNetwork/:/output \
	-v $(pwd)/Preprocessing:/preprocessing \
	-it gnn-neuralnetwork /code/gnn.py --test \
		--model_type matching --training_mode pair \
		--features_type opc --dataset muaz \
		-c /output/model_checkpoint_GMN_2023-09-26 \
		-o /output/Dataset-Muaz

else
	echo "Error, model not recognized"
	exit 1
fi

echo -e "\n *** Results saved in $(pwd)/NeuralNetwork/Dataset-Muaz/pairs_testing_Dataset-Muaz_"$1".csv\n"
cp NeuralNetwork/Dataset-Muaz/pairs_testing_Dataset-Muaz.csv ../../Results/csv/pairs_results_Dataset-Muaz_"$1".csv
