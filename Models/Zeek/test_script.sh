docker run --rm --name zeek_preprocessing -v $(pwd)/../../DBs/Dataset-Muaz/features/acfg_disasm:/input -v $(pwd)/Preprocessing/zeek_intermediate/Dataset-Muaz:/output -it zeek /code/zeek.py process /input /output --workers-num 10

cp Preprocessing/zeek_intermediate/Dataset-Muaz/zeek.json ../../DBs/Dataset-Muaz/features/zeek_Dataset-Muaz.json

docker run --rm -v $(pwd)/../../DBs:/input -v $(pwd)/NeuralNetwork/:/output -it zeekneuralnetwork /code/zeek_nn.py --test --dataset muaz -c /code/model_checkpoint -o /output/Dataset-Muaz

# copy the output
# -> to the notebook folders to compute the scores if it's only the embeddings
# -> to the codemerger rsults folder if those are the score directly
