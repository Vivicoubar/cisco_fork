ID=${RANDOM}$(date +%s)
docker run --rm --name zeek_preprocessing -v $(pwd)/../../DBs/Dataset-Muaz/features/acfg_disasm:/input -v $(pwd)/Preprocessing/zeek_intermediate/Dataset-Muaz_$ID:/output -it zeek /code/zeek.py process /input /output --workers-num 30

cp Preprocessing/zeek_intermediate/Dataset-Muaz_$ID/zeek.json ../../DBs/Dataset-Muaz/features/zeek_Dataset-Muaz.json

docker run --rm -v $(pwd)/../../DBs:/input -v $(pwd)/NeuralNetwork/:/output -it zeekneuralnetwork /code/zeek_nn.py --test --dataset muaz -c /code/model_checkpoint_2024-06-14/ -o /output/Dataset-Muaz

cp NeuralNetwork/Dataset-Muaz/pairs_testing_Dataset-Muaz.csv ../../Results/csv/pairs_results_Dataset-Muaz_zek.csv
# copy the output
# -> to the notebook folders to compute the scores if it's only the embeddings
# -> to the codemerger rsults folder if those are the score directly
