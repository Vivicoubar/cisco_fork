rm ~/codemerger/data/inst_insertion_test/results/pairs_results_Dataset-Muaz_trx.csv
docker run --rm -v $(pwd)/../../DBs/Dataset-Muaz/features/acfg_disasm:/input -v $(pwd)/Preprocessing/:/output -it trex-preprocessing /code/generate_function_traces.py -i /input -o /output/Dataset-Muaz-trex

if docker run --rm -v $(pwd)/../../DBs/Dataset-Muaz/pairs/:/pairs -v $(pwd)/Preprocessing/Dataset-Muaz-trex/:/traces -v $(pwd)/NeuralNetwork/:/output -it trex-inference conda run --no-capture-output -n trex python3 trex_inference.py --input-pairs /pairs/pairs_testing_Dataset-Muaz.csv --input-traces /traces/trex_traces.json --model-checkpoint-dir checkpoints/similarity/ --data-bin-dir data-bin-sim/similarity/ --output-dir /output/Dataset-Muaz-trex; then

cp NeuralNetwork/Dataset-Muaz-trex/pairs_testing_Dataset-Muaz.csv.trex_out.csv ~/codemerger/scripts/benchmark/results/pairs_results_Dataset-Muaz_trx.csv
fi

# copy the output
# -> to the notebook folders to compute the scores if it's only the embeddings
# -> to the codemerger rsults folder if those are the score directly
