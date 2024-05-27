# $1 : gnn or gmn

set -e
./preprocess_data_test.sh

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
cp NeuralNetwork/Dataset-Muaz/pairs_testing_Dataset-Muaz.csv ~/codemerger/scripts/benchmark/results/pairs_results_Dataset-Muaz_"$1".csv
# we directly have the output csv file
