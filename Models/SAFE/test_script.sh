set -e
rm -f NeuralNetwork/Dataset-Muaz_testing/pairs_testing_Dataset-Muaz.csv

docker run --rm \
    -v $(pwd)/../../DBs/Dataset-Muaz/features/acfg_disasm:/input \
    -v $(pwd)/Pretraining/Dataset-1_training:/instruction_embeddings \
    -v $(pwd)/Preprocessing:/output \
    -it safe-preprocessing /code/safe_preprocessing.py -i /input -o /output/Dataset-Muaz

docker run --rm \
    -v $(pwd)/../../DBs:/input \
    -v $(pwd)/Pretraining/Dataset-1_training:/instruction_embeddings \
    -v $(pwd)/Preprocessing:/preprocessing \
    -v $(pwd)/NeuralNetwork/:/output \
    -it safe-neuralnetwork /code/safe_nn.py \
        --test \
        --dataset muaz \
        -c /output/model_checkpoint_2024-06-14 \
        -o /output/Dataset-Muaz_testing

echo -e "\n *** Results saved in $(pwd)/NeuralNetwork/Dataset-Muaz_testing\n"

cp $(pwd)/NeuralNetwork/Dataset-Muaz_testing/pairs_testing_Dataset-Muaz.csv ../../Results/csv/pairs_results_Dataset-Muaz_saf.csv
echo -e "\nResult copied in ~/codemerger/scripts/benchmark/results/pairs_results_Dataset-Muaz_saf.csv"
